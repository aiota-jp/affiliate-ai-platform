import html
import os

import httpx
from dotenv import load_dotenv

from models.product import Product
from providers.base import ProductProvider

load_dotenv()


class YahooProvider(ProductProvider):
    SEARCH_URL = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"

    @property
    def name(self) -> str:
        return "yahoo"

    def _app_id(self) -> str:
        app_id = os.getenv("YAHOO_APP_ID", "").strip()
        if not app_id:
            raise RuntimeError("YAHOO_APP_ID が設定されていません。")
        return app_id

    def search_products(self, keyword: str, hits: int = 20) -> list[Product]:
        keyword = keyword.strip()
        if not keyword:
            raise ValueError("検索キーワードを指定してください。")

        hits = max(1, min(int(hits), 30))
        params = {
            "appid": self._app_id(),
            "query": keyword,
            "results": hits,
        }

        with httpx.Client(timeout=20.0) as client:
            response = client.get(self.SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

        return [self._to_product(item) for item in data.get("hits", [])]

    def _to_product(self, item: dict) -> Product:
        image = item.get("image") or {}
        review = item.get("review") or {}
        genre = item.get("genreCategory") or {}

        image_urls = [
            url for url in (image.get("medium"), image.get("small")) if url
        ]

        return Product(
            provider="yahoo",
            item_code=str(item.get("code") or ""),
            name=html.unescape(str(item.get("name") or "")),
            price=int(item.get("price") or 0),
            url=str(item.get("url") or ""),
            # APIから得た通常商品URLをaffiliate_urlとは扱わない。
            affiliate_url=None,
            image_urls=image_urls,
            catchcopy=html.unescape(str(item.get("headLine") or "")) or None,
            description=html.unescape(str(item.get("description") or "")) or None,
            genre_id=str(genre.get("id")) if genre.get("id") is not None else None,
            review_count=int(review["count"]) if review.get("count") is not None else None,
            review_average=float(review["rate"]) if review.get("rate") is not None else None,
        )
