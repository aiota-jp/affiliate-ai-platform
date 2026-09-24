# rakuten.py
import os
import sys
import httpx
from dotenv import load_dotenv

# .env を読み込む
load_dotenv()

# 楽天APIの認証・接続情報
RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID", "")
RAKUTEN_ACCESS_KEY = os.environ.get("RAKUTEN_ACCESS_KEY", "")
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID", "")

# 楽天アフィリエイトに登録した運営サイトURL
RAKUTEN_REFERER = os.environ.get("RAKUTEN_REFERER", "")
RAKUTEN_ORIGIN = os.environ.get("RAKUTEN_ORIGIN", "")

# URL末尾の日付はAPIの「バージョン番号」。
# エンドポイント系列・バージョンはAPIごとに異なるので、各APIの公式ドキュメントに従う。
SEARCH_URL = (
    "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
)
RANKING_URL = (
    "https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601"
)


def search(url: str, params: dict) -> dict:
    """楽天市場APIを呼び出し、JSONを辞書で返す共通関数。"""
    # 必須の認証・接続情報を確認する
    if not RAKUTEN_APP_ID:
        raise RuntimeError(
            "RAKUTEN_APP_ID が未設定です。.env を確認してください。"
        )
    if not RAKUTEN_ACCESS_KEY:
        raise RuntimeError(
            "RAKUTEN_ACCESS_KEY が未設定です。.env を確認してください。"
        )
    if not RAKUTEN_REFERER:
        raise RuntimeError(
            "RAKUTEN_REFERER が未設定です。.env を確認してください。"
        )
    if not RAKUTEN_ORIGIN:
        raise RuntimeError(
            "RAKUTEN_ORIGIN が未設定です。.env を確認してください。"
        )

    # 楽天APIへ送信するパラメータ
    query = {
        "applicationId": RAKUTEN_APP_ID,
        "accessKey": RAKUTEN_ACCESS_KEY,
        "format": "json",
        **params,
    }
    # Affiliate ID が設定されている場合だけ追加
    if RAKUTEN_AFFILIATE_ID:
        query["affiliateId"] = RAKUTEN_AFFILIATE_ID

    # 楽天アフィリエイトに登録した運営サイトURLをHTTPヘッダーとして送信する
    headers = {
        "Referer": RAKUTEN_REFERER,
        "Origin": RAKUTEN_ORIGIN,
    }

    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            res = client.get(url, params=query)
            # HTTPエラー（4xx/5xx）の場合
            if res.is_error:
                error_message = (
                    f"楽天APIエラー: status={res.status_code}, "
                    f"response={res.text}"
                )
                print(error_message, file=sys.stderr)
                raise RuntimeError(error_message)
            return res.json()
    # タイムアウトの場合
    except httpx.TimeoutException as e:
        error_message = f"楽天APIへの接続がタイムアウトしました: {e}"
        print(error_message, file=sys.stderr)
        raise RuntimeError(error_message) from e
    # 通信エラーの場合
    except httpx.RequestError as e:
        error_message = f"楽天APIへの接続に失敗しました: {e}"
        print(error_message, file=sys.stderr)
        raise RuntimeError(error_message) from e

def to_product(item: dict) -> dict:
    """楽天APIのレスポンスをDBの列名へ変換する（APIの都合をここで吸収する）。"""
    # 商品画像URL（mediumImageUrls）。無い商品もあるので空リストで受ける。
    image_urls = [
        img.get("imageUrl", "")
        for img in item.get("mediumImageUrls", [])
        if img.get("imageUrl")
    ]
    return {
        "item_code": item["itemCode"],
        "name": item["itemName"],
        "price": item.get("itemPrice"),
        "url": item.get("itemUrl"),
        "affiliate_url": item.get("affiliateUrl") or item.get("itemUrl"),
        "image_urls": image_urls,
        "catchcopy": item.get("catchcopy", ""),
        "description": item.get("itemCaption", ""),  # 商品説明文
        "genre_id": str(item.get("genreId", "")),
        "review_count": item.get("reviewCount", 0),
        "review_average": item.get("reviewAverage", 0),
    }

def to_product_detail(item: dict) -> dict:
    """楽天APIのレスポンスから、記事生成に使う詳細情報を抽出する。"""
    return {
        "item_code": item["itemCode"],
        "name": item["itemName"],
        "price": item.get("itemPrice"),
        "catch_copy": item.get("catchcopy", ""),
        "caption": item.get("itemCaption", ""),   # 商品説明文
        "shop_name": item.get("shopName", ""),
        "genre_id": str(item.get("genreId", "")),
        "review_count": item.get("reviewCount", 0),
        "review_average": item.get("reviewAverage", 0),
        "image_urls": [
            img.get("imageUrl", "")
            for img in item.get("mediumImageUrls", [])
        ],
        "affiliate_url": item.get("affiliateUrl") or item.get("itemUrl"),
    }