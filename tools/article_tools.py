from mcp_app import mcp
import db


@mcp.tool()
def list_article_candidates(limit: int = 10) -> list[dict]:
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
    product_id: int,
    title: str,
    keyword: str,
    content: str,
    wordpress_post_id: int | None = None,
    status: str = "draft",
) -> dict:
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
                product_id, title, keyword, content,
                wordpress_post_id, status
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
