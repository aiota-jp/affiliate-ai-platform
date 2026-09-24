import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID", "")
RAKUTEN_ACCESS_KEY = os.environ.get("RAKUTEN_ACCESS_KEY", "")
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID", "")
RAKUTEN_REFERER = os.environ.get("RAKUTEN_REFERER", "")
RAKUTEN_ORIGIN = os.environ.get("RAKUTEN_ORIGIN", "")

SEARCH_URL = (
    "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
)
RANKING_URL = (
    "https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601"
)


def search(url: str, params: dict) -> dict:
    if not RAKUTEN_APP_ID:
        raise RuntimeError("RAKUTEN_APP_ID が未設定です。.env を確認してください。")
    if not RAKUTEN_ACCESS_KEY:
        raise RuntimeError("RAKUTEN_ACCESS_KEY が未設定です。.env を確認してください。")
    if not RAKUTEN_REFERER:
        raise RuntimeError("RAKUTEN_REFERER が未設定です。.env を確認してください。")
    if not RAKUTEN_ORIGIN:
        raise RuntimeError("RAKUTEN_ORIGIN が未設定です。.env を確認してください。")

    query = {
        "applicationId": RAKUTEN_APP_ID,
        "accessKey": RAKUTEN_ACCESS_KEY,
        "format": "json",
        **params,
    }
    if RAKUTEN_AFFILIATE_ID:
        query["affiliateId"] = RAKUTEN_AFFILIATE_ID

    headers = {
        "Referer": RAKUTEN_REFERER,
        "Origin": RAKUTEN_ORIGIN,
    }

    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            res = client.get(url, params=query)
            if res.is_error:
                message = (
                    f"楽天APIエラー: status={res.status_code}, "
                    f"response={res.text}"
                )
                print(message, file=sys.stderr)
                raise RuntimeError(message)
            return res.json()
    except httpx.TimeoutException as exc:
        message = f"楽天APIへの接続がタイムアウトしました: {exc}"
        print(message, file=sys.stderr)
        raise RuntimeError(message) from exc
    except httpx.RequestError as exc:
        message = f"楽天APIへの接続に失敗しました: {exc}"
        print(message, file=sys.stderr)
        raise RuntimeError(message) from exc


def to_product(item: dict) -> dict:
    image_urls = []
    for image in item.get("mediumImageUrls") or []:
        url = image.get("imageUrl") if isinstance(image, dict) else image
        if url:
            image_urls.append(str(url))

    return {
        "provider": "rakuten",
        "item_code": item.get("itemCode", ""),
        "name": item.get("itemName", ""),
        "price": item.get("itemPrice"),
        "url": item.get("itemUrl", ""),
        "affiliate_url": item.get("affiliateUrl"),
        "image_urls": image_urls,
        "catchcopy": item.get("catchcopy"),
        "description": item.get("itemCaption"),
        "genre_id": str(item.get("genreId")) if item.get("genreId") is not None else None,
        "review_count": item.get("reviewCount", 0),
        "review_average": item.get("reviewAverage", 0),
    }
