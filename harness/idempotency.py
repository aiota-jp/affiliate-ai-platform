import hashlib
def create_run_key(provider: str,item_code: str)->str:
    provider=(provider or "").strip().lower(); item_code=(item_code or "").strip()
    if not provider: raise ValueError("provider is required")
    if not item_code: raise ValueError("item_code is required")
    return hashlib.sha256(f"{provider}:{item_code}".encode()).hexdigest()
