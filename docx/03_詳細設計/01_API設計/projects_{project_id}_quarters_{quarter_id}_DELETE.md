# 【API設計書】クォーター削除API

## 1. 概要

クォーターを削除する。紐づくタスクの `quarter_id` は NULL になる。

## 2. エンドポイント

- **Method:** `DELETE`
- **Path:** `/api/v1/projects/{project_id}/quarters/{quarter_id}/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

パスパラメータ: `project_id`, `quarter_id`

## 4. レスポンス

204 No Content

## 5. 内部処理 / ロジック

1. 権限チェック
2. `quarter` レコードを DELETE
3. 紐づく `task.quarter_id` を NULL に UPDATE
4. 204 を返す
