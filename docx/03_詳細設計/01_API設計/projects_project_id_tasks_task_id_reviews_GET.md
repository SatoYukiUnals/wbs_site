# 【API設計書】タスクのレビュー情報取得

## 1. 概要

指定タスクのレビュー情報（ステータス・コメント一覧）を返す。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/`
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
  "id": 1,
  "task_id": 10,
  "status": "rejected",
  "reviewer_id": 2,
  "comments": [
    {
      "id": 1,
      "body": "hanako 2026-04-15 10:00\n仕様と異なります",
      "author_id": 2,
      "author_name": "taro",
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
   - `Review` を `task_id` で SELECT
   - `ReviewComment` を `review_id` で SELECT（新しい順）
   - `User` を JOIN してコメント作成者名を取得
     - DBエラー：500 `ERR_SYS_500` を返す
4. **レスポンス生成**
   - レビュー情報・コメント一覧を返却
