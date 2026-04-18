# 【API設計書】レビュー履歴取得

## 1. 概要

指定タスクのレビュー操作履歴を時系列で返す（レビュー依頼・承認・差し戻しなどの操作ログ）。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/history/`
- **認証:** JWT必須（プロジェクトメンバー以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

#### `task_id`（タスクID）

- **型:** `integer` / **必須:** ○

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "history": [
    {
      "id": 1,
      "action": "request_review",
      "user_id": 1,
      "username": "hanako",
      "created_at": "2026-04-14T09:00:00Z"
    },
    {
      "id": 2,
      "action": "reject",
      "user_id": 2,
      "username": "taro",
      "created_at": "2026-04-15T10:00:00Z"
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

1. **JWT検証・メンバー確認**
   - `ProjectMember` でメンバーシップを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 非メンバー：403 `ERR_PERM_001` を返す
2. **タスク確認**
   - `Task` を `task_id` AND `project_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
3. **データ取得**
   - `ReviewHistory` を `task_id` でフィルタして SELECT（古い順）
   - `User` を JOIN してユーザー名を取得
     - DBエラー：500 `ERR_SYS_500` を返す
4. **レスポンス生成**
   - 履歴一覧を時系列で返却
