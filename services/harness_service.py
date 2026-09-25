from typing import Any
from db import get_conn
from harness.idempotency import create_run_key
from harness.logger import log_event
from harness.state import validate_status

class HarnessService:
    def check_run(self,product:dict[str,Any])->dict:
        key=create_run_key(str(product.get("provider") or ""),str(product.get("item_code") or ""))
        with get_conn() as conn,conn.cursor() as cur:
            cur.execute("SELECT run_key,status,current_step,error_message FROM workflow_runs WHERE run_key=%s",(key,))
            row=cur.fetchone()
        return {"duplicate":row is not None,"run_key":key,"run":dict(row) if row else None}

    def start_run(self,product:dict[str,Any],keyword:str="")->dict:
        provider=str(product.get("provider") or ""); item_code=str(product.get("item_code") or "")
        key=create_run_key(provider,item_code)
        with get_conn() as conn,conn.cursor() as cur:
            cur.execute("""INSERT INTO workflow_runs(run_key,keyword,provider,item_code,status,current_step)
                         VALUES(%s,%s,%s,%s,'started','START') ON CONFLICT(run_key) DO NOTHING RETURNING id""",
                        (key,keyword,provider,item_code))
            row=cur.fetchone()
        created=row is not None
        if created: self.add_log(key,"INFO","START","workflow started")
        return {"created":created,"duplicate":not created,"run_key":key}

    def update_state(self,run_key:str,status:str,current_step:str,error_message:str|None=None)->dict:
        status=validate_status(status)
        with get_conn() as conn,conn.cursor() as cur:
            cur.execute("""UPDATE workflow_runs SET status=%s,current_step=%s,error_message=%s,
                         updated_at=CURRENT_TIMESTAMP WHERE run_key=%s
                         RETURNING id,run_key,status,current_step,error_message""",
                        (status,current_step,error_message,run_key))
            row=cur.fetchone()
        if row is None: raise ValueError(f"run_key not found: {run_key}")
        self.add_log(run_key,"ERROR" if status=="failed" else "INFO",current_step,error_message or f"state changed to {status}")
        return dict(row)

    def add_log(self,run_key:str,level:str,step:str,message:str)->dict:
        level=(level or "INFO").upper()
        if level not in {"DEBUG","INFO","WARNING","ERROR"}: raise ValueError("invalid log level")
        with get_conn() as conn,conn.cursor() as cur:
            cur.execute("INSERT INTO workflow_logs(run_key,level,step,message) VALUES(%s,%s,%s,%s) RETURNING id,created_at",
                        (run_key,level,step,message))
            row=cur.fetchone()
        log_event(level,run_key,step,message)
        return {"id":row["id"],"run_key":run_key,"level":level,"step":step,"message":message,"created_at":row["created_at"].isoformat()}
harness_service=HarnessService()
