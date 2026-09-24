from mcp_app import mcp
import wordpress


@mcp.tool()
def create_draft(title: str, content: str) -> dict:
    if not title.strip():
        raise ValueError("記事タイトルを指定してください。")
    post = wordpress.create_post(title=title, content=content, status="draft")
    return {"post_id": post.get("id"), "status": post.get("status")}


@mcp.tool()
def get_post(post_id: int) -> dict:
    post = wordpress.get_post(post_id)
    return {
        "post_id": post.get("id"),
        "status": post.get("status"),
        "title": (post.get("title") or {}).get("rendered", ""),
    }


@mcp.tool()
def update_draft(
    post_id: int,
    title: str | None = None,
    content: str | None = None,
) -> dict:
    current = wordpress.get_post(post_id)
    if current.get("status") != "draft":
        raise ValueError(
            f"下書き以外の投稿は更新できません。現在のstatus={current.get('status')}"
        )

    fields = {}
    if title is not None:
        fields["title"] = title
    if content is not None:
        fields["content"] = content
    if not fields:
        raise ValueError("更新するタイトルまたは本文を指定してください。")

    post = wordpress.update_post(post_id, fields)
    return {"post_id": post.get("id"), "status": post.get("status")}
