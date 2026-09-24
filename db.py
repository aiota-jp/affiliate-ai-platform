import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    """第1回のDBを維持しつつ、第2回の複数Provider対応へ移行する。"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id              SERIAL PRIMARY KEY,
                provider        TEXT NOT NULL DEFAULT 'rakuten',
                item_code       TEXT NOT NULL,
                name            TEXT NOT NULL,
                price           INTEGER,
                url             TEXT,
                affiliate_url   TEXT,
                image_urls      TEXT[],
                catchcopy       TEXT,
                description     TEXT,
                genre_id        TEXT,
                review_count    INTEGER DEFAULT 0,
                review_average  NUMERIC(3, 2) DEFAULT 0,
                created_at      TIMESTAMP DEFAULT now(),
                updated_at      TIMESTAMP DEFAULT now()
            )
            """
        )

        # 第1回DBがすでに存在する場合の移行。
        cur.execute(
            """
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS provider TEXT NOT NULL DEFAULT 'rakuten'
            """
        )

        # 第1回の item_code 単独UNIQUEを安全に外す。
        cur.execute(
            """
            DO $$
            DECLARE
                constraint_name text;
            BEGIN
                SELECT c.conname
                  INTO constraint_name
                  FROM pg_constraint c
                  JOIN pg_class t ON t.oid = c.conrelid
                  JOIN pg_namespace n ON n.oid = t.relnamespace
                 WHERE t.relname = 'products'
                   AND n.nspname = current_schema()
                   AND c.contype = 'u'
                   AND (
                       SELECT array_agg(a.attname ORDER BY x.ord)
                       FROM unnest(c.conkey) WITH ORDINALITY AS x(attnum, ord)
                       JOIN pg_attribute a
                         ON a.attrelid = t.oid AND a.attnum = x.attnum
                   ) = ARRAY['item_code']::name[];

                IF constraint_name IS NOT NULL THEN
                    EXECUTE format(
                        'ALTER TABLE products DROP CONSTRAINT %I',
                        constraint_name
                    );
                END IF;
            END $$;
            """
        )

        cur.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
                uq_products_provider_item_code
            ON products(provider, item_code)
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS product_attributes (
                id               SERIAL PRIMARY KEY,
                product_id       INTEGER NOT NULL
                                 REFERENCES products(id) ON DELETE CASCADE,
                attribute_name   TEXT NOT NULL,
                attribute_value  TEXT,
                created_at       TIMESTAMP DEFAULT now(),
                UNIQUE (product_id, attribute_name)
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id                SERIAL PRIMARY KEY,
                product_id        INTEGER NOT NULL REFERENCES products(id),
                title             TEXT NOT NULL,
                keyword           TEXT,
                content           TEXT,
                wordpress_post_id INTEGER,
                status            TEXT DEFAULT 'draft',
                published_at      TIMESTAMP,
                created_at        TIMESTAMP DEFAULT now(),
                updated_at        TIMESTAMP DEFAULT now()
            )
            """
        )
        conn.commit()
