# 【API設計書】テンプレート削除API

## 1. 概要

テンプレートを削除する。作成者または admin 以上のみ実行可能。

## 2. エンドポイント

- **Method:** `DELETE`
- **Path:** `/api/v1/templates/{template_id}/`
- **認証:** 必要 / **権限:** 作成者 or admin 以上

## 3. レスポンス

204 No Content

## 5. 内部処理

1. テンプレート存在・テナント確認
2. 作成者または admin 以上であることを確認
3. `wbs_template` または `task_template` レコードを DELETE
4. 204 を返す
