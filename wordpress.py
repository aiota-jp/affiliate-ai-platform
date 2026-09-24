import os

import httpx
from dotenv import load_dotenv

load_dotenv()

WORDPRESS_URL = os.environ.get("WORDPRESS_URL", "").rstrip("/")
WORDPRESS_USER = os.environ.get("WORDPRESS_USER", "")
WORDPRESS_APP_PASSWORD = os.environ.get("WORDPRESS_APP_PASSWORD", "")


def _auth():
    if not WORDPRESS_URL or not WORDPRESS_USER or not WORDPRESS_APP_PASSWORD:
        raise RuntimeError("WordPress接続情報が未設定です。.env を確認してください。")
    return (WORDPRESS_USER, WORDPRESS_APP_PASSWORD)


def create_post(title: str, content: str, status: str = "draft") -> dict:
    with httpx.Client(timeout=20.0, auth=_auth()) as client:
        response = client.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/posts",
            json={"title": title, "content": content, "status": status},
        )
        response.raise_for_status()
        return response.json()


def get_post(post_id: int) -> dict:
    with httpx.Client(timeout=20.0, auth=_auth()) as client:
        response = client.get(f"{WORDPRESS_URL}/wp-json/wp/v2/posts/{post_id}")
        response.raise_for_status()
        return response.json()


def update_post(post_id: int, fields: dict) -> dict:
    with httpx.Client(timeout=20.0, auth=_auth()) as client:
        response = client.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/posts/{post_id}",
            json=fields,
        )
        response.raise_for_status()
        return response.json()
