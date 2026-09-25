from mcp_app import mcp
import wordpress

@mcp.tool()
def create_draft(title: str, content: str) -> dict:
    return wordpress.create_draft(title,content)

@mcp.tool()
def get_post(post_id: int) -> dict:
    return wordpress.get_post(post_id)

@mcp.tool()
def update_draft(post_id: int, title: str | None=None, content: str | None=None) -> dict:
    return wordpress.update_draft(post_id,title,content)
