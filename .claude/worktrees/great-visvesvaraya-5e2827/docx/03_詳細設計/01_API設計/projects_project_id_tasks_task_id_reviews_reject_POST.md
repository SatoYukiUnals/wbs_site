# 【API設計書】レビュー差し戻し

## 1. 概要

レビュー待ち状態のタスクを差し戻す。指摘コメントが1件以上必須。担当者本人は実行不可。差し戻し時にタスクステータスを「進行中」に変更しレビュー履歴を記録する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/reject/`
- **認証:** JWT必須（プロジェクトメンバー以上、担当者以外）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

#### `task_id`（タスクID）

- **型:** `integer` / **必須:** ○

### ボディ

#### `comments`（指摘コメントリスト）

- **型:** `array` / **必須:** ○
- 1件以上。各要素は `string`（コメント本文）

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "task": {
    "id": 10,
    "status": "進行中"
  },
  "review": {
    "id": 1,
    "status": "rejected"
  },
  "comments": [
    {
      "id": 2,
      "body": "仕様と異なります"
    }
  ]
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 担当者本人 | 403 | `ERR_PERM_004` | 担当者本人はレビューできません | |
| コメント0件 | 400 | `ERR_VAL_009` | 指摘コメントを1件以上入力してください | |
| タスク未存在 | 404 | `ERR_DAT_404` | 対象のデータが見つかりませんでした | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証・メンバー確認**
   - `ProjectMember` でメンバーシップを確認
     - 未認証：401 `ERR_AUTH_002` を返す
2. **タスク・担当者確認**
   - `Task` を `task_id` AND `project_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
   - `TaskAssignee` でリクエスト元 `user_id` が担当者でないことを確認
     - 担当者本人：403 `ERR_PERM_004` を返す
3. **バリデーション**
   - `comments` が1件以上であることを確認
     - 0件：400 `ERR_VAL_009` を返す
4. **DB操作（トランザクション）**
   - `Review.status` を `rejected` に UPDATE
   - `ReviewComment` を件数分 INSERT（`author_id` = リクエスト元 `user_id`）
   - `Task.status` を `進行中` に UPDATE
   - `TaskStatusHistory` に INSERT
   - `ReviewHistory` に INSERT（`action` = `reject`）
     - DBエラー：500 `ERR_SYS_500` を返す
5. **レスポンス生成**
   - 更新後タスク・レビュー・コメント一覧を返却
