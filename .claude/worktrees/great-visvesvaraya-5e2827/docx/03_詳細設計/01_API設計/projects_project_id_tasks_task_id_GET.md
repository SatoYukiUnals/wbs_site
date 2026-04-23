# 【API設計書】タスク詳細取得

## 1. 概要

指定タスクの詳細情報を返す。担当者・子タスク一覧を含む。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/`
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
  "title": "要件定義",
  "description": "詳細説明",
  "parent_task_id": null,
  "depth": 1,
  "order": 1,
  "status": "進行中",
  "progress": 50,
  "priority": "高",
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "actual_start_date": "2026-04-02",
  "actual_end_date": null,
  "estimated_hours": 40,
  "quarter_id": 1,
  "assignees": [
    {"user_id": 1, "username": "hanako"}
  ],
  "children": [
    {"id": 2, "title": "ヒアリング", "status": "完了", "progress": 100}
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
2. **データ取得**
   - `Task` を `task_id` AND `project_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
   - `TaskAssignee` JOIN で担当者情報を取得
   - 直属の子タスク（`parent_task_id = task_id`）を SELECT
     - DBエラー：500 `ERR_SYS_500` を返す
3. **レスポンス生成**
   - タスク詳細・担当者・子タスク一覧を返却
