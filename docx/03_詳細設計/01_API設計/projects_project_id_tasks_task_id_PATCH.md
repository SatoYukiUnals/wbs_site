# 【API設計書】タスク部分編集（ステータス・進捗率・実績日）

## 1. 概要

タスクのステータス・進捗率・実績日のみを更新する。メンバーは担当タスクのみ更新可能（担当外は403）。admin 以上は全タスク更新可能。更新後にクォーター・プロジェクト進捗率を再集計する。

## 2. エンドポイント

- **Method:** `PATCH`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/`
- **認証:** JWT必須（プロジェクトメンバー以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

#### `task_id`（タスクID）

- **型:** `integer` / **必須:** ○

### ボディ

#### `status`（ステータス）

- **型:** `string` / **必須:** -
- `未着手` / `進行中` / `レビュー待ち` / `完了` / `保留` のいずれか

#### `progress`（進捗率）

- **型:** `integer` / **必須:** -
- 0〜100

#### `actual_start_date`（実績開始日）

- **型:** `date` / **必須:** -
- YYYY-MM-DD

#### `actual_end_date`（実績終了日）

- **型:** `date` / **必須:** -
- YYYY-MM-DD

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "id": 1,
  "status": "完了",
  "progress": 100,
  "actual_start_date": "2026-04-02",
  "actual_end_date": "2026-04-28",
  "quarter_progress": 80,
  "project_progress": 45
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足（担当外） | 403 | `ERR_PERM_001` | この操作を行う権限がありません | memberの場合 |
| バリデーションエラー | 400 | `ERR_VAL_001` | 入力内容に不備があります | |
| 対象未存在 | 404 | `ERR_DAT_404` | 対象のデータが見つかりませんでした | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証**
   - `user_id`・`role` を取得
     - 無効：401 `ERR_AUTH_002` を返す
2. **対象タスク確認**
   - `Task` を `task_id` AND `project_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
3. **権限チェック**
   - `role` が `admin` 以上の場合：全タスク更新可能
   - `member` の場合：`TaskAssignee` で `task_id` AND `user_id` の存在確認
     - 担当外：403 `ERR_PERM_001` を返す
4. **バリデーション**
   - `progress` が 0〜100 の整数であることを確認
   - `status` の値チェック
     - エラー時：400 `ERR_VAL_001` を返す
5. **DB更新（トランザクション）**
   - `Task` の指定フィールドのみ UPDATE
   - `status` 変更時：`TaskStatusHistory` に INSERT
   - クォーター進捗率を再集計 → `Quarter.progress` を UPDATE
   - プロジェクト進捗率を再集計 → `Project.progress` を UPDATE
     - DBエラー：500 `ERR_SYS_500` を返す
6. **レスポンス生成**
   - 更新後タスク・クォーター進捗率・プロジェクト進捗率を返却
