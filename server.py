# server.py
import os

import db
from mcp_app import mcp

# importした時点で @mcp.tool() が実行され、Toolが登録される
import tools.product_tools    # noqa: F401  第2回
import tools.article_tools    # noqa: F401  第3回で追加
import tools.wordpress_tools  # noqa: F401  第3回で追加


def main() -> None:
    """DBを初期化し、指定されたTransportでMCP Serverを起動する。"""
    db.init_db()

    # ローカルのCodexではstdioを既定値として維持する。
    # VPS/Dockerではcompose.yamlからstreamable-httpを指定する。
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport == "stdio":
        mcp.run(transport="stdio")
        return

    if transport == "streamable-http":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        path = os.getenv("MCP_PATH", "/mcp")

        # DifyなどリモートのMCP Clientから利用するためのHTTP Transport。
        # stateless_http + json_response は、通常のTool呼び出しを行う
        # デプロイ用途で扱いやすい構成。
        mcp.run(
            transport="streamable-http",
            host=host,
            port=port,
            streamable_http_path=path,
            stateless_http=True,
            json_response=True,
        )
        return

    raise ValueError(
        "MCP_TRANSPORT は 'stdio' または 'streamable-http' を指定してください。"
    )


if __name__ == "__main__":
    main()
