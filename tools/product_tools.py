from mcp_app import mcp
import db
import rakuten

from services.product_service import ProductService

product_service = ProductService()


@mcp.tool()
def search_products(
    keyword: str,
    provider: str = "all",
    hits: int = 20,
) -> list[dict]:
    """楽天・Yahoo!の商品を共通形式で検索する。"""
    products = product_service.search_products(
        keyword=keyword,
        provider=provider,
        hits=hits,
    )
    return [product.to_dict() for product in products]


@mcp.tool()
def get_ranking_products(genre_id: str | None = None) -> list[dict]:
    """楽天ランキングから売れ筋商品を取得する。"""
    params = {}
    if genre_id:
        params["genreId"] = genre_id

    data = rakuten.search(rakuten.RANKING_URL, params)
    products = []
    for entry in data.get("Items", []):
        product = rakuten.to_product(entry["Item"])
        product["provider"] = "rakuten"
        products.append(product)
    return products


@mcp.tool()
def get_product(
    item_code: str,
    provider: str = "rakuten",
) -> dict | None:
    """商品コードで1件取得する。第2回では楽天の単品取得に対応。"""
    product = product_service.get_product(
        item_code=item_code,
        provider=provider,
    )
    return product.to_dict() if product else None


@mcp.tool()
def save_product(product: dict) -> dict:
    """商品をproductsテーブルへ保存する（Provider込みでUPSERT）。"""
    provider = str(product.get("provider") or "rakuten")
    item_code = str(product.get("item_code") or "")

    if not item_code:
        raise ValueError("item_code がありません。")

    params = {
        "provider": provider,
        "item_code": item_code,
        "name": product.get("name") or "",
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

    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO products (
                provider, item_code, name, price, url, affiliate_url,
                image_urls, catchcopy, description,
                genre_id, review_count, review_average
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
            params,
        )
        row = cur.fetchone()
        conn.commit()

    return {"id": row[0], "provider": row[1], "item_code": row[2]}


@mcp.tool()
def list_saved_products(limit: int = 20) -> list[dict]:
    """保存済み商品を一覧取得する。"""
    limit = max(1, min(int(limit), 100))

    with db.get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, provider, item_code, name, price, url,
                   affiliate_url, image_urls, catchcopy, description,
                   genre_id, review_count, review_average,
                   created_at, updated_at
            FROM products
            ORDER BY updated_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        columns = [desc.name for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
