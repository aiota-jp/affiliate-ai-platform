from mcp_app import mcp
from harness.validator import validate_article,validate_selected_product
from services.harness_service import harness_service

@mcp.tool()
def validate_product(product:dict)->dict:
    return validate_selected_product(product)

@mcp.tool()
def validate_generated_article(title:str,keyword:str,content:str)->dict:
    return validate_article(title,keyword,content)

@mcp.tool()
def check_article_run(product:dict)->dict:
    return harness_service.check_run(product)

@mcp.tool()
def start_article_run(product:dict,keyword:str="")->dict:
    return harness_service.start_run(product,keyword)

@mcp.tool()
def update_article_run(run_key:str,status:str,current_step:str,error_message:str|None=None)->dict:
    return harness_service.update_state(run_key,status,current_step,error_message)

@mcp.tool()
def write_workflow_log(run_key:str,level:str,step:str,message:str)->dict:
    return harness_service.add_log(run_key,level,step,message)
