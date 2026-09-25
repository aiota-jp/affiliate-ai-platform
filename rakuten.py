import os
import httpx

SEARCH_URL = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
RANKING_URL = "https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601"


def _headers() -> dict:
    headers = {}
    if os.getenv("RAKUTEN_REFERER"):
        headers["Referer"] = os.environ["RAKUTEN_REFERER"]
    if os.getenv("RAKUTEN_ORIGIN"):
        headers["Origin"] = os.environ["RAKUTEN_ORIGIN"]
    return headers


def search(url: str, params: dict) -> dict:
    app_id = os.environ["RAKUTEN_APP_ID"]
    access_key = os.environ["RAKUTEN_ACCESS_KEY"]
    query = {"applicationId": app_id, "accessKey": access_key, "format": "json", **params}
    affiliate_id = os.getenv("RAKUTEN_AFFILIATE_ID")
    if affiliate_id:
        query["affiliateId"] = affiliate_id
    response = httpx.get(url, params=query, headers=_headers(), timeout=20.0)
    response.raise_for_status()
    return response.json()


def to_product(item: dict) -> dict:
    images = item.get("mediumImageUrls") or []
    image_urls = []
    for image in images:
        if isinstance(image, dict):
            value = image.get("imageUrl")
        else:
            value = image
        if value:
            image_urls.append(value)

    return {
        "provider": "rakuten",
        "item_code": item.get("itemCode", ""),
        "name": item.get("itemName", ""),
        "price": int(item.get("itemPrice") or 0),
        "url": item.get("itemUrl", ""),
        "affiliate_url": item.get("affiliateUrl"),
        "image_urls": image_urls,
        "catchcopy": item.get("catchcopy"),
        "description": item.get("itemCaption"),
        "genre_id": str(item.get("genreId") or "") or None,
        "review_count": item.get("reviewCount"),
        "review_average": item.get("reviewAverage"),
    }
