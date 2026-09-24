import os

import db
from mcp_app import mcp

import tools.product_tools
import tools.article_tools
import tools.wordpress_tools


def main() -> None:
    db.init_db()

    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport == "stdio":
        mcp.run(transport="stdio")
        return

    if transport == "streamable-http":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        path = os.getenv("MCP_PATH", "/mcp")

        mcp.run(
            transport="streamable-http",
            host=host,
            port=port,
            streamable_http_path=path,
            stateless_http=True,
            json_response=True,
        )
        return

    raise ValueError(f"Unsupported MCP_TRANSPORT: {transport}")


if __name__ == "__main__":
    main()
