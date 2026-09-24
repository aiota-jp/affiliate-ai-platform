# affiliate-ai-platform — シリーズ② 第3回

第1回・第2回の構成をすべて含み、第3回のDify Workflowから
記事下書きをPostgreSQLへ保存できるようにした統合版ソースです。

## 第2回までに含まれるもの

- Linux VPS + Docker + Streamable HTTP MCP
- PostgreSQL
- `Product` 共通モデル
- `RakutenProvider`
- `YahooProvider`
- `ProductService`
- `search_products(keyword, provider, hits)`
- `provider=rakuten / yahoo / all`
- `UNIQUE(provider, item_code)`

## 第3回で追加・更新したもの

- `services/article_service.py`
- `tools/article_tools.py` の `save_article` をDify Workflow向けに拡張
- SELECT_PRODUCTの商品オブジェクトを `product` として保存可能
- 商品UPSERT + 記事INSERTを同一トランザクションで実行
- `docs/dify-workflow.md`

商品選定・キーワード選定・記事生成そのものはDifyのLLMノードで行うため、
Python側へOpenAI API呼び出しコードは追加していません。

## 既存 `.env`

第2回の `.env` をそのまま利用します。OpenAI APIキーはDify側で管理します。

```env
YAHOO_APP_ID=発行されたClient ID
```

## VPS反映

```bash
cd /home/ubuntu/affiliate-ai-platform
sudo docker compose config
sudo docker compose up -d --build
sudo docker compose ps
sudo docker compose logs -f mcp
```

MCP Tool定義が変わるため、再ビルド後はDifyの
「連携 → ツール → MCP → Affiliate MCP Server」でToolリストを更新してください。

## 第3回 Workflow

```text
ユーザー入力
 ↓
SEARCH_PRODUCTS
 ↓
SELECT_PRODUCT
 ↓
SELECT_KEYWORD
 ↓
GENERATE_ARTICLE
 ↓
SAVE_ARTICLE
 ↓
出力
```
