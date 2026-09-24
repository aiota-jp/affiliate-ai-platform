from models.product import Product
from providers.base import ProductProvider
from providers.rakuten_provider import RakutenProvider
from providers.yahoo_provider import YahooProvider


class ProductService:
    def __init__(self, providers: list[ProductProvider] | None = None) -> None:
        providers = providers or [RakutenProvider(), YahooProvider()]
        self.providers = {provider.name: provider for provider in providers}

    def search_products(
        self,
        keyword: str,
        provider: str = "all",
        hits: int = 20,
    ) -> list[Product]:
        keyword = keyword.strip()
        provider = provider.strip().lower()

        if not keyword:
            raise ValueError("検索キーワードを指定してください。")

        hits = max(1, min(int(hits), 30))

        if provider == "all":
            products: list[Product] = []
            errors: list[str] = []

            for current in self.providers.values():
                try:
                    products.extend(current.search_products(keyword, hits))
                except Exception as exc:
                    errors.append(f"{current.name}: {exc}")

            if not products and errors:
                raise RuntimeError(
                    "すべてのProviderの商品検索に失敗しました: "
                    + " / ".join(errors)
                )
            return products

        target = self.providers.get(provider)
        if target is None:
            available = ", ".join(["all", *self.providers.keys()])
            raise ValueError(
                f"未対応のproviderです: {provider}。指定可能: {available}"
            )

        return target.search_products(keyword, hits)

    def get_product(
        self,
        item_code: str,
        provider: str = "rakuten",
    ) -> Product | None:
        provider = provider.strip().lower()
        target = self.providers.get(provider)

        if target is None:
            raise ValueError(f"未対応のproviderです: {provider}")

        try:
            return target.get_product(item_code)
        except NotImplementedError as exc:
            raise ValueError(
                f"{provider} は item_code による単品取得へ未対応です。"
            ) from exc
