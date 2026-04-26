# 【API設計書】ロードマップアイテム作成API

## 1. 概要

ロードマップアイテムを新規作成する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/roadmap/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{
  "title": "認証機能リリース",
  "description": "JWT認証の実装完了",
  "quarter_id": "uuid または null",
  "status": "未着手"
}
```

## 4. レスポンス

201 Created でアイテム情報を返す

## 5. 内部処理

1. 権限チェック
2. `roadmap_item` テーブルへ INSERT（`order` は末尾に追加）
3. 201 で返す
