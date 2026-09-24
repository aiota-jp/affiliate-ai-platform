# tools/wordpress_tools.py
from mcp_app import mcp
import wordpress


@mcp.tool()
def create_draft(title: str, content: str) -> dict:
    """WordPressに下書き記事を作成する（公開はしない）。"""
    if not title.strip():
        raise ValueError("記事タイトルを指定してください。")
    post = wordpress.create_post(title=title, content=content, status="draft")
    return {"post_id": post.get("id"), "status": post.get("status")}


@mcp.tool()
def get_post(post_id: int) -> dict:
    """WordPressの投稿を取得する。"""
    post = wordpress.get_post(post_id)
    return {
        "post_id": post.get("id"),
        "status": post.get("status"),
        "title": (post.get("title") or {}).get("rendered", ""),
    }


@mcp.tool()
def update_draft(post_id: int, title: str | None = None,
                 content: str | None = None) -> dict:
    """WordPressの下書きを更新する（タイトル・本文）。"""
    # 公開済みの投稿を誤って書き換えないよう、下書きかどうかを先に確認する。
    current = wordpress.get_post(post_id)
    if current.get("status") != "draft":
        raise ValueError(
            f"下書き以外の投稿は更新できません。現在のstatus={current.get('status')}"
        )

    fields: dict = {}
    if title is not None:
        fields["title"] = title
    if content is not None:
        fields["content"] = content
    if not fields:
        raise ValueError("更新するタイトルまたは本文を指定してください。")
    post = wordpress.update_post(post_id, fields)
    return {"post_id": post.get("id"), "status": post.get("status")}