# tools/article_tools.py
from mcp_app import mcp
import db


@mcp.tool()
def list_article_candidates(limit: int = 10) -> list[dict]:
    """記事候補の商品を、レビュー評価の高い順に返す。

    同じ商品でも異なる検索意図の記事を作れるよう、商品単位では除外しない。
    重複は check_duplicate_article()（商品ID＋キーワード）で判定する。
    """
    limit = max(1, min(limit, 50))
    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.id, p.item_code, p.name, p.price,
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
            "item_code": r[1],
            "name": r[2],
            "price": r[3],
            "review_count": r[4],
            "review_average": float(r[5]) if r[5] is not None else 0,
            "genre_id": r[6],
        }
        for r in rows
    ]


@mcp.tool()
def check_duplicate_article(product_id: int, keyword: str) -> dict:
    """同じ商品＋キーワードの記事が既にないか確認する。"""
    if not keyword.strip():
        raise ValueError("キーワードを指定してください。")
    keyword = keyword.strip()
    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, status FROM articles
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
    product_id: int,
    title: str,
    keyword: str,
    content: str,
    wordpress_post_id: int | None = None,
    status: str = "draft",
) -> dict:
    """記事情報（本文含む）を articles テーブルへ保存する。"""
    if not title.strip():
        raise ValueError("記事タイトルを指定してください。")
    if not keyword.strip():
        raise ValueError("キーワードを指定してください。")
    if not content.strip():
        raise ValueError("記事本文を指定してください。")
    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO articles (
                product_id, title, keyword, content, wordpress_post_id, status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                product_id,
                title.strip(),
                keyword.strip(),
                content,
                wordpress_post_id,
                status,
            ),
        )
        article_id = cur.fetchone()[0]
        conn.commit()
    return {"article_id": article_id, "status": status}