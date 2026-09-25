from mcp_app import mcp
from services.article_service import article_service

@mcp.tool()
def list_article_candidates(limit: int=20) -> list[dict]:
    return article_service.list_article_candidates(limit)

@mcp.tool()
def check_duplicate_article(product_id: int) -> dict:
    return article_service.check_duplicate_article(product_id)

@mcp.tool()
def save_article(
    title: str,
    keyword: str,
    content: str,
    product_id: int | None = None,
    product: dict | None = None,
    wordpress_post_id: int | None = None,
    status: str = "draft",
) -> dict:
    """Difyで生成した記事下書きを保存する。product指定時は商品をUPSERTする。"""
    return article_service.save_article(title,keyword,content,product_id,product,wordpress_post_id,status)
