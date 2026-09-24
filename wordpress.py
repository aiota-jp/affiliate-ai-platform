# wordpress.py
import os
import sys
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()

WORDPRESS_URL = os.environ.get("WORDPRESS_URL", "")
WORDPRESS_USER = os.environ.get("WORDPRESS_USER", "")
WORDPRESS_APP_PASSWORD = os.environ.get("WORDPRESS_APP_PASSWORD", "")


def _auth_header() -> dict:
    """アプリケーションパスワードによるBasic認証ヘッダーを作る。"""
    if not (WORDPRESS_URL and WORDPRESS_USER and WORDPRESS_APP_PASSWORD):
        raise RuntimeError(
            "WORDPRESS_URL / WORDPRESS_USER / WORDPRESS_APP_PASSWORD が"
            "未設定です。.env を確認してください。"
        )
    token = base64.b64encode(
        f"{WORDPRESS_USER}:{WORDPRESS_APP_PASSWORD}".encode("utf-8")
    ).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def _request(method: str, path: str, json: dict | None = None) -> dict:
    """WordPress REST APIを呼び出し、JSONを辞書で返す共通関数。"""
    url = f"{WORDPRESS_URL.rstrip('/')}/wp-json/wp/v2/{path.lstrip('/')}"
    headers = _auth_header()
    try:
        with httpx.Client(timeout=15.0, headers=headers) as client:
            res = client.request(method, url, json=json)
            if res.is_error:
                msg = (
                    f"WordPress APIエラー: status={res.status_code}, "
                    f"response={res.text}"
                )
                print(msg, file=sys.stderr)
                raise RuntimeError(msg)
            return res.json()
    except httpx.TimeoutException as e:
        msg = f"WordPress APIへの接続がタイムアウトしました: {e}"
        print(msg, file=sys.stderr)
        raise RuntimeError(msg) from e
    except httpx.RequestError as e:
        msg = f"WordPress APIへの接続に失敗しました: {e}"
        print(msg, file=sys.stderr)
        raise RuntimeError(msg) from e


def create_post(title: str, content: str, status: str = "draft") -> dict:
    """投稿を作成する（既定は下書き）。"""
    return _request(
        "POST",
        "posts",
        json={"title": title, "content": content, "status": status},
    )


def get_post(post_id: int) -> dict:
    """投稿を取得する。"""
    return _request("GET", f"posts/{post_id}")


def update_post(post_id: int, fields: dict) -> dict:
    """投稿を更新する（タイトル・本文・ステータスなど）。"""
    return _request("POST", f"posts/{post_id}", json=fields)