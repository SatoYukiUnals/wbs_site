# 【API設計書】テンプレート一覧取得

## 1. 概要

ログイン中ユーザーがアクセス可能なテンプレート一覧を返す。自分が作成した個人テンプレートと、共有テンプレート（`is_shared = True`）を合わせて返す。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/templates/`
- **認証:** JWT必須（全ユーザー）

## 3. リクエスト

### クエリパラメータ

#### `type`（テンプレート種別フィルタ）

- **型:** `string` / **必須:** -
- `wbs` または `task` のいずれか

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "templates": [
    {
      "id": 1,
      "title": "標準開発フロー",
      "type": "wbs",
      "is_shared": true,
      "created_by": {
        "user_id": 1,
        "username": "hanako"
      }
    },
    {
      "id": 2,
      "title": "バグ対応テンプレート",
      "type": "task",
      "is_shared": false,
      "created_by": {
        "user_id": 1,
        "username": "hanako"
      }
    }
  ]
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証**
   - `user_id`・`tenant_id` を取得
     - 無効：401 `ERR_AUTH_002` を返す
2. **データ取得**
   - `Template` テーブルを `(is_shared = True AND tenant_id = JWTのtenant_id) OR created_by = user_id` + `type`フィルタ（指定時）で SELECT
   - `User` を JOIN して作成者情報を取得
     - DBエラー：500 `ERR_SYS_500` を返す
3. **レスポンス生成**
   - テンプレート一覧を返却
