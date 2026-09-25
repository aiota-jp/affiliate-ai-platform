ALLOWED_STATUSES={"started","product_selected","keyword_selected","article_generated","saved","failed","duplicate"}
def validate_status(status: str)->str:
    status=(status or "").strip()
    if status not in ALLOWED_STATUSES: raise ValueError(f"invalid status: {status}")
    return status
