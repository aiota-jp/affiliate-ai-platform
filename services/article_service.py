from db import get_conn, upsert_product


class ArticleService:
    def save_article(
        self,
        title: str,
        keyword: str,
        content: str,
        product_id: int | None = None,
        product: dict | None = None,
        wordpress_post_id: int | None = None,
        status: str = "draft",
    ) -> dict:
        if product_id is None:
            if not product:
                raise ValueError("product_id or product is required")
            product_id = upsert_product(product)

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO articles(product_id,title,keyword,content,wordpress_post_id,status)
                   VALUES(%s,%s,%s,%s,%s,%s)
                   RETURNING id,product_id,title,keyword,status,wordpress_post_id,created_at""",
                (product_id,title,keyword,content,wordpress_post_id,status),
            )
            return dict(cur.fetchone())

    def list_article_candidates(self, limit: int = 20) -> list[dict]:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""SELECT p.* FROM products p
                           WHERE NOT EXISTS(SELECT 1 FROM articles a WHERE a.product_id=p.id)
                           ORDER BY p.id DESC LIMIT %s""",(limit,))
            return [dict(x) for x in cur.fetchall()]

    def check_duplicate_article(self, product_id: int) -> dict:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT id,title,status FROM articles WHERE product_id=%s ORDER BY id DESC LIMIT 1",(product_id,))
            row=cur.fetchone()
            return {"duplicate":row is not None,"article":dict(row) if row else None}


article_service=ArticleService()
