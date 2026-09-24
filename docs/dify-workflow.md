# シリーズ② 第3回 Dify Workflow 設定メモ

第3回では商品選定・キーワード選定・記事生成はDifyのLLMノードで実行します。
OpenAI APIキーはMCP Serverの `.env` には追加せず、Difyのモデルプロバイダー設定で管理します。

## Workflow

```text
ユーザー入力
├─ keyword
└─ provider
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

## SEARCH_PRODUCTS

```text
keyword  = ユーザー入力.keyword
provider = ユーザー入力.provider
hits     = 5
```

## SELECT_PRODUCT

`SEARCH_PRODUCTS.json` から1商品を選び、少なくとも次の値を保持します。

```json
{
  "provider": "",
  "item_code": "",
  "name": "",
  "price": 0,
  "url": "",
  "affiliate_url": null,
  "image_urls": [],
  "catchcopy": null,
  "description": null,
  "genre_id": null,
  "review_count": 0,
  "review_average": 0,
  "selection_reason": ""
}
```

## SELECT_KEYWORD

```json
{
  "primary_keyword": "",
  "secondary_keywords": ["", "", ""],
  "search_intent": ""
}
```

## GENERATE_ARTICLE

商品情報に存在しない事実を作らず、Markdownの記事下書きを生成します。
SAVE_ARTICLEへ渡しやすいよう、記事タイトルと本文を別々に取得できる構成を推奨します。

## SAVE_ARTICLE

第3回版 `save_article` は次を受け取れます。

```text
title
keyword
content
product
status = draft
```

`product` に SELECT_PRODUCT の商品オブジェクトを渡すと、
MCP Server側で `products` へUPSERTした後、同一トランザクションで
`articles` へ記事を保存します。

既存互換として `product_id` を直接指定することもできます。
