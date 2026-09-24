from mcp_app import mcp
import db

from services.article_service import ArticleService

article_service = ArticleService()


@mcp.tool()
def list_article_candidates(limit: int = 10) -> list[dict]:
    """保存済み商品から記事候補を取得する。"""
    limit = max(1, min(limit, 50))
    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.id, p.provider, p.item_code, p.name, p.price,
                   p.review_count, p.review_average, p.genre_id
            FROM products p
            ORDER BY p.review_average DESC, p.review_count DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [
        {
            "product_id": r[0],
            "provider": r[1],
            "item_code": r[2],
            "name": r[3],
            "price": r[4],
            "review_count": r[5],
            "review_average": float(r[6]) if r[6] is not None else 0,
            "genre_id": r[7],
        }
        for r in rows
    ]


@mcp.tool()
def check_duplicate_article(product_id: int, keyword: str) -> dict:
    """商品IDとキーワードの組み合わせで既存記事を確認する。"""
    if not keyword.strip():
        raise ValueError("キーワードを指定してください。")
    keyword = keyword.strip()

    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, status
            FROM articles
            WHERE product_id = %s AND keyword = %s
            """,
            (product_id, keyword),
        )
        rows = cur.fetchall()

    return {
        "exists": len(rows) > 0,
        "articles": [
            {"id": r[0], "title": r[1], "status": r[2]} for r in rows
        ],
    }


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
    """
    Difyで生成した記事下書きを保存する。

    第3回では SELECT_PRODUCT の商品オブジェクトを product に渡せる。
    product_id が未指定の場合は、product を products テーブルへUPSERTして
    得られたIDを articles.product_id に使用する。

    第2回までのように、すでに保存済みの商品IDを product_id で指定する
    呼び出し方も利用できる。
    """
    return article_service.save_article(
        title=title,
        keyword=keyword,
        content=content,
        product_id=product_id,
        product=product,
        wordpress_post_id=wordpress_post_id,
        status=status,
    )
