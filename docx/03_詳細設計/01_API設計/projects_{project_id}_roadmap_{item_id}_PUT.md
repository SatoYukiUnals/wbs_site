# 【API設計書】ロードマップアイテム更新API

## 1. 概要

ロードマップアイテムのタイトル・説明・クォーター・ステータスを更新する。

## 2. エンドポイント

- **Method:** `PUT`
- **Path:** `/api/v1/projects/{project_id}/roadmap/{item_id}/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

`roadmap_POST.md` と同一

## 4. レスポンス

200 OK で更新後のアイテム情報を返す

## 5. 内部処理

1. 権限チェック、アイテム存在確認
2. `roadmap_item` を UPDATE
3. 200 で返す
