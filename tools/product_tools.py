# tools/product_tools.py
from mcp_app import mcp
import rakuten
import db


@mcp.tool()
def search_products(keyword: str, hits: int = 20) -> list[dict]:
    """キーワードで楽天商品検索APIを呼び出し、商品一覧を返す。"""
    if not keyword.strip():
        raise ValueError("検索キーワードを指定してください。")

    # 楽天商品検索APIの hits は 1〜30 の範囲。CodexやユーザーがhitsにAPI範囲外の
    # 値（hits=100 など）を渡しても壊れないように、ここで丸める。
    hits = max(1, min(hits, 30))

    data = rakuten.search(rakuten.SEARCH_URL, {"keyword": keyword, "hits": hits})
    return [rakuten.to_product(e["Item"]) for e in data.get("Items", [])]


@mcp.tool()
def get_ranking_products(genre_id: str | None = None) -> list[dict]:
    """楽天ランキングから売れ筋商品を取得する。genre_id で絞り込みも可能。"""
    params = {}
    if genre_id:
        params["genreId"] = genre_id

    data = rakuten.search(rakuten.RANKING_URL, params)
    return [rakuten.to_product(e["Item"]) for e in data.get("Items", [])]


@mcp.tool()
def get_product(item_code: str) -> dict | None:
    """item_code で楽天商品検索APIを呼び出し、該当商品の基本情報を返す。"""
    if not item_code.strip():
        raise ValueError("商品コード（itemCode）を指定してください。")

    data = rakuten.search(rakuten.SEARCH_URL, {"itemCode": item_code})
    items = data.get("Items", [])
    if not items:
        return None
    return rakuten.to_product(items[0]["Item"])


@mcp.tool()
def save_product(product: dict) -> dict:
    """商品を products テーブルへ保存する（UPSERT）。"""
    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO products (
                item_code, name, price, url, affiliate_url,
                image_urls, catchcopy, description,
                genre_id, review_count, review_average
            )
            VALUES (
                %(item_code)s, %(name)s, %(price)s, %(url)s, %(affiliate_url)s,
                %(image_urls)s, %(catchcopy)s, %(description)s,
                %(genre_id)s, %(review_count)s, %(review_average)s
            )
            ON CONFLICT (item_code) DO UPDATE SET
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
            RETURNING id, item_code
            """,
            product,
        )
        row = cur.fetchone()
        conn.commit()
    return {"id": row[0], "item_code": row[1]}


@mcp.tool()
def list_saved_products(limit: int = 20) -> list[dict]:
    """保存済みの商品を一覧取得する（確認用）。"""
    # limit=-1 など想定外の値が渡っても壊れないように、1〜100 に丸める。
    limit = max(1, min(limit, 100))
    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, item_code, name, price, review_count, review_average
            FROM products
            ORDER BY updated_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [
        {
            "id": r[0],
            "item_code": r[1],
            "name": r[2],
            "price": r[3],
            "review_count": r[4],
            "review_average": float(r[5]) if r[5] is not None else 0,
        }
        for r in rows
    ]

@mcp.tool()
def get_product_detail(item_code: str) -> dict | None:
    """item_code で楽天商品検索APIを呼び出し、記事生成用の詳細情報を返す。

    商品説明・画像・店舗などを含む。この戻り値自体はDBへ再保存せず、
    記事生成時にCodexへ渡して使う（商品説明・画像などは第2回で
    products に保存済み。店舗名などDBに無い項目はここで一時利用する）。
    """
    if not item_code.strip():
        raise ValueError("商品コード（itemCode）を指定してください。")

    data = rakuten.search(rakuten.SEARCH_URL, {"itemCode": item_code})
    items = data.get("Items", [])
    if not items:
        return None
    return rakuten.to_product_detail(items[0]["Item"])