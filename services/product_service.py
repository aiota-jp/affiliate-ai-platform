from models.product import Product
from providers.rakuten_provider import RakutenProvider
from providers.yahoo_provider import YahooProvider


class ProductService:
    def __init__(self):
        self.providers = {"rakuten": RakutenProvider(), "yahoo": YahooProvider()}

    def search_products(self, keyword: str, provider: str = "all", hits: int = 20) -> list[Product]:
        provider = (provider or "all").strip().lower()
        if provider == "all":
            products = []
            errors = []
            for name, current in self.providers.items():
                try:
                    products.extend(current.search_products(keyword, hits))
                except Exception as exc:
                    errors.append(f"{name}: {exc}")
            if not products and errors:
                raise RuntimeError("; ".join(errors))
            return products
        selected = self.providers.get(provider)
        if selected is None:
            raise ValueError("provider must be one of: all, rakuten, yahoo")
        return selected.search_products(keyword, hits)
