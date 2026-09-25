import os

from mcp_app import mcp

# Tool modules must be imported before mcp.run().
import tools.product_tools  # noqa: F401
import tools.article_tools  # noqa: F401
import tools.wordpress_tools  # noqa: F401
import tools.harness_tools  # noqa: F401
from db import init_db


if __name__ == "__main__":
    init_db()
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=os.getenv("MCP_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_PORT", "8000")),
            streamable_http_path=os.getenv("MCP_PATH", "/mcp"),
            stateless_http=True,
            json_response=True,
        )
    else:
        mcp.run(transport="stdio")
