from dataclasses import asdict, dataclass, field


@dataclass
class Product:
    provider: str
    item_code: str
    name: str
    price: int
    url: str
    affiliate_url: str | None = None
    image_urls: list[str] = field(default_factory=list)
    catchcopy: str | None = None
    description: str | None = None
    genre_id: str | None = None
    review_count: int | None = None
    review_average: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)
