import os
import httpx


def _auth():
    return (os.environ["WORDPRESS_USER"], os.environ["WORDPRESS_APP_PASSWORD"])


def create_draft(title: str, content: str) -> dict:
    response=httpx.post(
        f'{os.environ["WORDPRESS_URL"].rstrip("/")}/wp-json/wp/v2/posts',
        auth=_auth(), json={"title":title,"content":content,"status":"draft"}, timeout=30.0
    )
    response.raise_for_status()
    return response.json()


def get_post(post_id: int) -> dict:
    response=httpx.get(
        f'{os.environ["WORDPRESS_URL"].rstrip("/")}/wp-json/wp/v2/posts/{post_id}',
        auth=_auth(), timeout=30.0
    )
    response.raise_for_status()
    return response.json()


def update_draft(post_id: int, title: str | None=None, content: str | None=None) -> dict:
    payload={}
    if title is not None: payload["title"]=title
    if content is not None: payload["content"]=content
    response=httpx.post(
        f'{os.environ["WORDPRESS_URL"].rstrip("/")}/wp-json/wp/v2/posts/{post_id}',
        auth=_auth(), json=payload, timeout=30.0
    )
    response.raise_for_status()
    return response.json()
