from mcp_app import mcp
from db import get_conn, upsert_product
from services.product_service import ProductService

product_service=ProductService()

@mcp.tool()
def search_products(keyword: str, provider: str="all", hits: int=20) -> list[dict]:
    """楽天・Yahoo!の商品を共通形式で検索する。"""
    return [p.to_dict() for p in product_service.search_products(keyword,provider,hits)]

@mcp.tool()
def save_product(product: dict) -> dict:
    """商品をproductsテーブルへ保存する（Provider込みでUPSERT）。"""
    return {"id":upsert_product(product)}

@mcp.tool()
def list_saved_products(limit: int=20) -> list[dict]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM products ORDER BY id DESC LIMIT %s",(limit,))
        return [dict(x) for x in cur.fetchall()]
