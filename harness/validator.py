from typing import Any

def validate_selected_product(product: dict[str,Any] | None) -> dict:
    errors=[]
    if not isinstance(product,dict):
        return {"valid":False,"errors":["product must be an object"]}
    for key in ("provider","item_code","name","price","url"):
        if product.get(key) in (None,""): errors.append(f"{key} is required")
    price=product.get("price")
    if price not in (None,""):
        try:
            if int(price)<0: errors.append("price must be 0 or greater")
        except (TypeError,ValueError): errors.append("price must be numeric")
    return {"valid":not errors,"errors":errors}

def validate_article(title: str, keyword: str, content: str) -> dict:
    errors=[]
    title,keyword,content=(title or "").strip(),(keyword or "").strip(),(content or "").strip()
    if not title: errors.append("title is required")
    if not keyword: errors.append("keyword is required")
    if not content: errors.append("content is required")
    elif len(content)<200: errors.append("content is too short")
    return {"valid":not errors,"errors":errors}
