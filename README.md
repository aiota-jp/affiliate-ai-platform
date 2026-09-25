# affiliate-ai-platform Series 2 Episode 4 Complete

第1回〜第4回までを1つに統合したVPS/Docker用ソースです。

## 含む機能
- Streamable HTTP MCP Server
- PostgreSQL
- Rakuten / Yahoo Provider
- ProductService
- Product / Article / WordPress MCP Tools
- 第3回 `save_article(product=...)` による商品UPSERT + 記事保存
- 第4回 Agent Harness
  - Validator
  - Retry基盤
  - State
  - Idempotency
  - Logging

## 初回
`.env.example` を `.env` にコピーし、実値を設定してください。

```bash
cp .env.example .env
sudo docker compose config
sudo docker compose up -d --build
sudo docker compose ps
sudo docker compose logs --tail=50 mcp
```

既存DBを利用する場合、`db.py` の `init_db()` は既存テーブルを削除しません。
ただし既存スキーマとの差異がある環境では、バックアップを取ってから確認してください。

## Dify
再ビルド後:
`連携 → ツール → MCP → Affiliate MCP Server → 更新`

第4回はまず `validate_product` から単体確認してください。

## 注意
- `.env` は同梱していません。
- PostgreSQL 5432 / MCP 8000 はホストへ公開していません。
- `proxy` Docker network は既存Nginx Proxy Manager側で作成済みの前提です。
- Retry基盤は含みますが、既存ProviderのHTTP呼び出しへはまだ強制適用していません。第4回の段階検証で組み込みます。


## MCP SDK 2.x

この完全版は MCP Python SDK 2.x を使用します。

```python
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("affiliate-mcp-server")
```

`FastMCP` は使用しません。

確認:

```bash
grep -R "FastMCP" -n . --exclude-dir=.git
```

何も表示されないことを確認してください。

## VPSへ反映後の再ビルド

```bash
cd /home/ubuntu/affiliate-ai-platform

sudo docker compose down
sudo docker compose build --no-cache mcp
sudo docker compose up -d

sudo docker compose ps
sudo docker compose logs --tail=50 mcp
```

正常時はMCPログに次の内容が表示されます。

```text
StreamableHTTP session manager started
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```
