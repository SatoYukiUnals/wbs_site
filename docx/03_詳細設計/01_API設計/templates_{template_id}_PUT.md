# 【API設計書】テンプレート更新API

## 1. 概要

テンプレートの名前・内容・共有設定を更新する。作成者または admin 以上のみ実行可能。

## 2. エンドポイント

- **Method:** `PUT`
- **Path:** `/api/v1/templates/{template_id}/`
- **認証:** 必要 / **権限:** 作成者 or admin 以上

## 3. リクエスト

`templates_POST.md` のボディと同一（`type` は変更不可）

## 4. レスポンス

200 OK でテンプレート情報を返す

## 5. 内部処理

1. テンプレート存在・テナント確認（同テナント内のみ）
2. 作成者または admin 以上であることを確認
3. `title`・`content`・`is_shared` を UPDATE
4. 200 で返す
