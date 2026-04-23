# 【API設計書】ガントチャートデータ取得

## 1. 概要

指定プロジェクトのガントチャート描画に必要なデータ（クォーター・タスク一覧・担当者・日程）を返す。閲覧専用。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/gantt/`
- **認証:** JWT必須（プロジェクトメンバー以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

### クエリパラメータ

#### `quarter_id`（クォーター絞り込み）

- **型:** `integer` / **必須:** -
- 指定時はそのクォーターのタスクのみ返す

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "project": {
    "id": 1,
    "name": "新規システム開発",
    "start_date": "2026-04-01",
    "end_date": "2026-09-30"
  },
  "quarters": [
    {
      "id": 1,
      "title": "Q1",
      "start_date": "2026-04-01",
      "end_date": "2026-06-30"
    }
  ],
  "tasks": [
    {
      "id": 1,
      "title": "要件定義",
      "parent_task_id": null,
      "depth": 1,
      "start_date": "2026-04-01",
      "end_date": "2026-04-30",
      "actual_start_date": "2026-04-02",
      "actual_end_date": null,
      "progress": 80,
      "status": "進行中",
      "assignees": [{"user_id": 1, "username": "hanako"}]
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
2. **プロジェクト確認**
   - `Project` を `project_id` AND `tenant_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
3. **データ取得**
   - `Quarter` を `project_id` でフィルタして全件 SELECT
   - `Task` を `project_id` + `quarter_id`（指定時）でフィルタして SELECT
   - `TaskAssignee` JOIN で担当者情報を取得
     - DBエラー：500 `ERR_SYS_500` を返す
4. **レスポンス生成**
   - プロジェクト情報・クォーター・タスク一覧を返却
