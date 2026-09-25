import json
import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ["DATABASE_URL"]


def get_conn():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id BIGSERIAL PRIMARY KEY,
            provider VARCHAR(50) NOT NULL DEFAULT 'rakuten',
            item_code TEXT NOT NULL,
            name TEXT NOT NULL,
            price INTEGER NOT NULL DEFAULT 0,
            url TEXT NOT NULL,
            affiliate_url TEXT,
            image_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
            catchcopy TEXT,
            description TEXT,
            genre_id TEXT,
            review_count INTEGER,
            review_average DOUBLE PRECISION,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_products_provider_item_code ON products(provider,item_code)")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id BIGSERIAL PRIMARY KEY,
            product_id BIGINT REFERENCES products(id),
            title TEXT NOT NULL,
            keyword TEXT NOT NULL,
            content TEXT NOT NULL,
            wordpress_post_id BIGINT,
            status VARCHAR(50) NOT NULL DEFAULT 'draft',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)



def upsert_product(product: dict) -> int:
    """商品をproductsテーブルへUPSERTし、products.idを返す。"""
    required = ("item_code", "name", "url")
    missing = [key for key in required if not product.get(key)]
    if missing:
        raise ValueError(f"missing required product fields: {', '.join(missing)}")

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO products (
                provider, item_code, name, price, url, affiliate_url,
                image_urls, catchcopy, description, genre_id,
                review_count, review_average
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s)
            ON CONFLICT (provider, item_code)
            DO UPDATE SET
                name=EXCLUDED.name,
                price=EXCLUDED.price,
                url=EXCLUDED.url,
                affiliate_url=EXCLUDED.affiliate_url,
                image_urls=EXCLUDED.image_urls,
                catchcopy=EXCLUDED.catchcopy,
                description=EXCLUDED.description,
                genre_id=EXCLUDED.genre_id,
                review_count=EXCLUDED.review_count,
                review_average=EXCLUDED.review_average,
                updated_at=CURRENT_TIMESTAMP
            RETURNING id
            """,
            (
                product.get("provider") or "rakuten",
                product["item_code"],
                product["name"],
                int(product.get("price") or 0),
                product["url"],
                product.get("affiliate_url"),
                json.dumps(product.get("image_urls") or [], ensure_ascii=False),
                product.get("catchcopy"),
                product.get("description"),
                product.get("genre_id"),
                product.get("review_count"),
                product.get("review_average"),
            ),
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("failed to upsert product")
        return int(row["id"])
