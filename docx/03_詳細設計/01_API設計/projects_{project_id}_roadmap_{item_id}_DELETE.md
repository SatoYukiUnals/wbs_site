# 【API設計書】ロードマップアイテム削除API

## 1. 概要

ロードマップアイテムを削除する。

## 2. エンドポイント

- **Method:** `DELETE`
- **Path:** `/api/v1/projects/{project_id}/roadmap/{item_id}/`
- **認証:** 必要 / **権限:** admin 以上

## 3. レスポンス

204 No Content

## 5. 内部処理

1. 権限チェック、アイテム存在確認
2. `roadmap_item` レコードを DELETE
3. 204 を返す
