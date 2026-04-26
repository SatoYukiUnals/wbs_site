# 【API設計書】クォーター更新API

## 1. 概要

クォーターのタイトル・期間を更新する。

## 2. エンドポイント

- **Method:** `PUT`
- **Path:** `/api/v1/projects/{project_id}/quarters/{quarter_id}/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

`projects_{project_id}_quarters_POST.md` のボディと同一

## 4. レスポンス

200 OK で更新後のクォーター情報を返す

## 5. 内部処理 / ロジック

1. 権限チェック
2. バリデーション（end_date > start_date）
3. `quarter` テーブルを UPDATE
4. 200 で返す
