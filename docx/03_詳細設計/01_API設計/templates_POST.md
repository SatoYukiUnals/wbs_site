# 【API設計書】テンプレート作成API

## 1. 概要

WBSテンプレートまたはタスクテンプレートを新規作成する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/templates/`
- **認証:** 必要

## 3. リクエスト

```json
{
  "type": "wbs",
  "title": "開発フロー標準",
  "content": "フロントエンド実装\nバックエンド実装\nテスト確認",
  "is_shared": false
}
```

- `type`: `"wbs"` または `"task"`, 必須
- `title`: string, 必須
- `content`: string, 必須（改行区切り）
- `is_shared`: boolean, 任意（`true` は admin 以上のみ設定可）

## 4. レスポンス

201 Created でテンプレート情報を返す

## 5. 内部処理

1. `is_shared=true` の場合、admin 以上であることを確認
2. `type` に応じて `wbs_template` または `task_template` テーブルへ INSERT
3. 201 で返す
