# 【API設計書】レビュー承認

## 1. 概要

レビュー待ち状態のタスクを承認する。担当者本人は実行不可。承認時にタスクステータスを「完了」に変更し、レビュー履歴を記録する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/approve/`
- **認証:** JWT必須（プロジェクトメンバー以上、担当者以外）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

#### `task_id`（タスクID）

- **型:** `integer` / **必須:** ○

### ボディ

#### `comment`（承認コメント）

- **型:** `string` / **必須:** -
- 任意のコメント（1件まで）

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "task": {
    "id": 10,
    "status": "完了"
  },
  "review": {
    "id": 1,
    "status": "approved"
  }
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 担当者本人 | 403 | `ERR_PERM_004` | 担当者本人はレビューできません | |
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
3. **DB操作（トランザクション）**
   - `Review.status` を `approved` に UPDATE
   - コメント指定時：`ReviewComment` を INSERT
   - `Task.status` を `完了` に UPDATE
   - `TaskStatusHistory` に INSERT
   - `ReviewHistory` に INSERT（`action` = `approve`）
   - クォーター・プロジェクト進捗率を再集計
     - DBエラー：500 `ERR_SYS_500` を返す
4. **レスポンス生成**
   - 更新後タスク・レビュー情報を返却
