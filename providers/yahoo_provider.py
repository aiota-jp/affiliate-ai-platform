import html
import os

import httpx

from harness.retry import run_with_retry
from models.product import Product
from providers.base import ProductProvider


class YahooProvider(ProductProvider):
    SEARCH_URL = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"

    @property
    def name(self) -> str:
        return "yahoo"

    def _request(self, keyword: str, hits: int) -> dict:
        response = httpx.get(
            self.SEARCH_URL,
            params={
                "appid": os.environ["YAHOO_APP_ID"],
                "query": keyword,
                "results": hits,
            },
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def search_products(self, keyword: str, hits: int = 20) -> list[Product]:
        # Timeout / Network Error / 429 / 5xx の場合だけ最大3回試行する。
        data = run_with_retry(
            lambda: self._request(keyword, hits),
            max_attempts=3,
            base_delay=1.0,
        )

        products = []
        for item in data.get("hits", []):
            review = item.get("review") or {}
            image = item.get("image") or {}
            image_urls = [x for x in (image.get("medium"), image.get("small")) if x]
            products.append(
                Product(
                    provider="yahoo",
                    item_code=item.get("code", ""),
                    name=html.unescape(item.get("name", "")),
                    price=int(item.get("price") or 0),
                    url=item.get("url", ""),
                    affiliate_url=None,
                    image_urls=image_urls,
                    catchcopy=html.unescape(item.get("headline") or ""),
                    description=html.unescape(item.get("description") or ""),
                    genre_id=str(item.get("genreCategory") or "") or None,
                    review_count=review.get("count"),
                    review_average=review.get("rate"),
                )
            )
        return products
