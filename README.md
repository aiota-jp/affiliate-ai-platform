# affiliate-ai-platform — シリーズ② 第2回

第1回のVPS/Docker/MCP/PostgreSQL/Dify構成をそのまま含み、
第2回の ProductService + Provider を統合した完全版ソースです。

## 第2回で追加されたもの

- `models/product.py` — 共通Productモデル
- `providers/base.py` — Providerインターフェース
- `providers/rakuten_provider.py`
- `providers/yahoo_provider.py`
- `services/product_service.py`
- `search_products(keyword, provider, hits)` のProvider対応
- `products.provider`
- `UNIQUE(provider, item_code)`
- `.env.example` の `YAHOO_APP_ID`

## 既存 `.env` を使う場合

VPS上の第1回 `.env` は上書きせず、次だけ追記してください。

```env
YAHOO_APP_ID=発行されたClient ID
```

## 検証順

```text
provider=rakuten
provider=yahoo
provider=all
```

`provider=all, hits=5` は、楽天最大5件 + Yahoo最大5件です。

Yahoo!の商品検索APIで返る通常の `url` は、現段階では
`affiliate_url` とみなしていません。
