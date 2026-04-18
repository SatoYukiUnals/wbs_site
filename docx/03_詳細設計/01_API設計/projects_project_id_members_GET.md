# 【API設計書】プロジェクトメンバー一覧取得

## 1. 概要

指定プロジェクトのメンバー一覧（ユーザー情報・ロール）を返す。プロジェクトメンバーのみ閲覧可能。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/members/`
- **認証:** JWT必須（プロジェクトメンバー以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "members": [
    {
      "user_id": 1,
      "username": "hanako",
      "email": "hanako@example.com",
      "role": "admin"
    },
    {
      "user_id": 2,
      "username": "taro",
      "email": "taro@example.com",
      "role": "member"
    }
  ]
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足 | 403 | `ERR_PERM_001` | この操作を行う権限がありません | |
| 対象未存在 | 404 | `ERR_DAT_404` | 対象のデータが見つかりませんでした | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証**
   - `tenant_id`・`user_id` を取得
     - 無効：401 `ERR_AUTH_002` を返す
2. **プロジェクト取得**
   - `Project` を `project_id` AND `tenant_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
3. **メンバー確認**
   - リクエスト元が `ProjectMember` に存在することを確認
     - 非メンバー：403 `ERR_PERM_001` を返す
4. **データ取得**
   - `ProjectMember` と `User` を JOIN して一覧取得
     - DBエラー：500 `ERR_SYS_500` を返す
5. **レスポンス生成**
   - メンバー一覧を返却
