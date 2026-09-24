import db


class ArticleService:
    """選定商品と生成記事をPostgreSQLへ保存する。"""

    @staticmethod
    def _normalize_product(product: dict) -> dict:
        provider = str(product.get("provider") or "").strip().lower()
        item_code = str(product.get("item_code") or "").strip()
        name = str(product.get("name") or "").strip()

        if not provider:
            raise ValueError("product.provider を指定してください。")
        if not item_code:
            raise ValueError("product.item_code を指定してください。")
        if not name:
            raise ValueError("product.name を指定してください。")

        return {
            "provider": provider,
            "item_code": item_code,
            "name": name,
            "price": product.get("price"),
            "url": product.get("url"),
            "affiliate_url": product.get("affiliate_url"),
            "image_urls": product.get("image_urls") or [],
            "catchcopy": product.get("catchcopy"),
            "description": product.get("description"),
            "genre_id": product.get("genre_id"),
            "review_count": product.get("review_count") or 0,
            "review_average": product.get("review_average") or 0,
        }

    def save_article(
        self,
        *,
        title: str,
        keyword: str,
        content: str,
        product_id: int | None = None,
        product: dict | None = None,
        wordpress_post_id: int | None = None,
        status: str = "draft",
    ) -> dict:
        title = title.strip()
        keyword = keyword.strip()
        content = content.strip()
        status = status.strip() or "draft"

        if not title:
            raise ValueError("記事タイトルを指定してください。")
        if not keyword:
            raise ValueError("キーワードを指定してください。")
        if not content:
            raise ValueError("記事本文を指定してください。")
        if product_id is None and product is None:
            raise ValueError("product_id または product を指定してください。")

        with db.get_connection() as conn, conn.cursor() as cur:
            saved_product = None

            if product_id is None:
                p = self._normalize_product(product or {})
                cur.execute(
                    """
                    INSERT INTO products (
                        provider, item_code, name, price, url, affiliate_url,
                        image_urls, catchcopy, description, genre_id,
                        review_count, review_average
                    )
                    VALUES (
                        %(provider)s, %(item_code)s, %(name)s, %(price)s,
                        %(url)s, %(affiliate_url)s, %(image_urls)s,
                        %(catchcopy)s, %(description)s, %(genre_id)s,
                        %(review_count)s, %(review_average)s
                    )
                    ON CONFLICT (provider, item_code) DO UPDATE SET
                        name           = EXCLUDED.name,
                        price          = EXCLUDED.price,
                        url            = EXCLUDED.url,
                        affiliate_url  = EXCLUDED.affiliate_url,
                        image_urls     = EXCLUDED.image_urls,
                        catchcopy      = EXCLUDED.catchcopy,
                        description    = EXCLUDED.description,
                        genre_id       = EXCLUDED.genre_id,
                        review_count   = EXCLUDED.review_count,
                        review_average = EXCLUDED.review_average,
                        updated_at     = now()
                    RETURNING id, provider, item_code
                    """,
                    p,
                )
                row = cur.fetchone()
                product_id = row[0]
                saved_product = {
                    "id": row[0],
                    "provider": row[1],
                    "item_code": row[2],
                }
            else:
                cur.execute(
                    "SELECT id, provider, item_code FROM products WHERE id = %s",
                    (product_id,),
                )
                row = cur.fetchone()
                if row is None:
                    raise ValueError(f"product_id={product_id} の商品がありません。")
                saved_product = {
                    "id": row[0],
                    "provider": row[1],
                    "item_code": row[2],
                }

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
                    title,
                    keyword,
                    content,
                    wordpress_post_id,
                    status,
                ),
            )
            article_id = cur.fetchone()[0]
            conn.commit()

        return {
            "article_id": article_id,
            "product": saved_product,
            "title": title,
            "keyword": keyword,
            "status": status,
        }
