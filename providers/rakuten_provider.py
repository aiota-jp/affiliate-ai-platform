from models.product import Product
from providers.base import ProductProvider
import rakuten


class RakutenProvider(ProductProvider):
    @property
    def name(self) -> str:
        return "rakuten"

    def search_products(self, keyword: str, hits: int = 20) -> list[Product]:
        keyword = keyword.strip()
        if not keyword:
            raise ValueError("検索キーワードを指定してください。")

        hits = max(1, min(int(hits), 30))
        data = rakuten.search(
            rakuten.SEARCH_URL,
            {"keyword": keyword, "hits": hits},
        )

        return [
            self._from_dict(rakuten.to_product(entry["Item"]))
            for entry in data.get("Items", [])
        ]

    def get_product(self, item_code: str) -> Product | None:
        item_code = item_code.strip()
        if not item_code:
            raise ValueError("商品コードを指定してください。")

        data = rakuten.search(
            rakuten.SEARCH_URL,
            {"itemCode": item_code, "hits": 1},
        )
        items = data.get("Items", [])
        if not items:
            return None
        return self._from_dict(rakuten.to_product(items[0]["Item"]))

    def _from_dict(self, item: dict) -> Product:
        return Product(
            provider="rakuten",
            item_code=str(item.get("item_code") or ""),
            name=str(item.get("name") or ""),
            price=int(item.get("price") or 0),
            url=str(item.get("url") or ""),
            affiliate_url=item.get("affiliate_url"),
            image_urls=item.get("image_urls") or [],
            catchcopy=item.get("catchcopy"),
            description=item.get("description"),
            genre_id=str(item.get("genre_id")) if item.get("genre_id") is not None else None,
            review_count=int(item.get("review_count") or 0),
            review_average=float(item.get("review_average") or 0),
        )
