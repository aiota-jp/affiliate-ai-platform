# db.py
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    """本シリーズで使用するテーブルを作成する。"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id              SERIAL PRIMARY KEY,
                item_code       TEXT UNIQUE NOT NULL,
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