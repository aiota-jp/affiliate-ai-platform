# mcp_app.py
from mcp.server.mcpserver import MCPServer

# 各 tools/*.py と server.py はこの mcp を共有する（循環import回避）。
mcp = MCPServer("affiliate-mcp-server")