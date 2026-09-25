from harness.retry import run_with_retry
from models.product import Product
from providers.base import ProductProvider
import rakuten


class RakutenProvider(ProductProvider):
    @property
    def name(self) -> str:
        return "rakuten"

    def _from_dict(self, value: dict) -> Product:
        return Product(**value)

    def search_products(self, keyword: str, hits: int = 20) -> list[Product]:
        # Timeout / Network Error / 429 / 5xx の場合だけ最大3回試行する。
        data = run_with_retry(
            lambda: rakuten.search(
                rakuten.SEARCH_URL,
                {"keyword": keyword, "hits": hits},
            ),
            max_attempts=3,
            base_delay=1.0,
        )

        result = []
        for entry in data.get("Items", []):
            item = entry.get("Item", entry)
            result.append(self._from_dict(rakuten.to_product(item)))
        return result
