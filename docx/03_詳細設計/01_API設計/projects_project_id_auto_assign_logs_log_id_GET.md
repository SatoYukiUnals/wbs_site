# 【API設計書】自動割り振り履歴詳細取得

## 1. 概要

指定の自動割り振り履歴の詳細（割り振り内容の全タスクとユーザーの対応）を返す。admin 以上のみ閲覧可能。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/auto-assign/logs/{log_id}/`
- **認証:** JWT必須（プロジェクト内 admin 以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

#### `log_id`（ログID）

- **型:** `integer` / **必須:** ○

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "id": 5,
  "executed_by": {
    "user_id": 1,
    "username": "hanako"
  },
  "executed_at": "2026-04-17T10:00:00Z",
  "result": [
    {
      "task_id": 10,
      "task_title": "フロントエンド実装",
      "user_id": 2,
      "username": "taro"
    },
    {
      "task_id": 11,
      "task_title": "バックエンド実装",
      "user_id": 1,
      "username": "hanako"
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

1. **JWT検証・権限確認**
   - `ProjectMember` でリクエスト元の `role` が `admin` 以上であることを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 権限不足：403 `ERR_PERM_001` を返す
2. **データ取得**
   - `AutoAssignLog` を `log_id` AND `project_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
3. **result JSON パース**
   - `result` フィールドのJSONから task_id・user_id の対応を展開
   - タスクタイトル・ユーザー名を JOIN で取得
     - DBエラー：500 `ERR_SYS_500` を返す
4. **レスポンス生成**
   - 履歴詳細・割り振り内容を返却
