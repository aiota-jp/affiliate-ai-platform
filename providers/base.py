from abc import ABC, abstractmethod
from models.product import Product


class ProductProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def search_products(self, keyword: str, hits: int = 20) -> list[Product]:
        raise NotImplementedError

    def get_product(self, item_code: str) -> Product | None:
        raise NotImplementedError
