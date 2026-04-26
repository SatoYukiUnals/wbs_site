# 【API設計書】直近のタスク一覧API

## 1. 概要

プロジェクト内の直近タスク（期限切れ・今週開始予定・着手中）を抽出・集計してグループ別に返す。
フロントエンドはレスポンスをそのまま表示する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/recent/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. リクエスト

### パスパラメータ

| パラメータ | 型 | 説明 |
|---|---|---|
| `project_id` | UUID | 対象プロジェクトID |

### クエリパラメータ（任意）

| パラメータ | 型 | 説明 |
|---|---|---|
| `status` | string | ステータスでフィルタ（Todo / InProgress / InReview / Done / OnHold） |
| `assignee_id` | UUID | 担当者でフィルタ |

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "overdue": [
    {
      "task_id": "uuid",
      "wbs_no": "1.2.1",
      "title": "API実装",
      "status": "InProgress",
      "assignees": [{"user_id": "uuid", "username": "山田太郎"}],
      "start_date": "2026-04-01",
      "end_date": "2026-04-10",
      "actual_start_date": "2026-04-02",
      "actual_end_date": null
    }
  ],
  "starting_this_week": [
    {
      "task_id": "uuid",
      "wbs_no": "1.3.1",
      "title": "フロントエンド実装",
      "status": "Todo",
      "assignees": [{"user_id": "uuid", "username": "鈴木花子"}],
      "start_date": "2026-04-27",
      "end_date": "2026-05-10",
      "actual_start_date": null,
      "actual_end_date": null
    }
  ],
  "in_progress": [
    {
      "task_id": "uuid",
      "wbs_no": "1.1.2",
      "title": "DB設計",
      "status": "InProgress",
      "assignees": [{"user_id": "uuid", "username": "山田太郎"}],
      "start_date": "2026-04-15",
      "end_date": "2026-05-15",
      "actual_start_date": "2026-04-15",
      "actual_end_date": null
    }
  ]
}
```

### グループ定義

| キー | 内容 |
|------|------|
| `overdue` | `end_date` ≤ 今日 かつ 未完了のタスク |
| `starting_this_week` | `start_date` が今日から1週間以内 かつ 未完了のタスク |
| `in_progress` | `actual_start_date` が入力済み かつ 未完了のタスク |

### エラー

| ステータスコード | 内容 |
|---|---|
| 401 | 認証エラー |
| 403 | プロジェクトメンバーでない |
| 404 | プロジェクトが存在しない |

## 5. 内部処理 / ロジック

1. プロジェクトメンバー確認
2. `task` テーブルから対象タスクを抽出
   - 前提条件：`start_date` IS NOT NULL AND `end_date` IS NOT NULL AND `actual_end_date` IS NULL AND `status` ≠ `'Done'` AND `deleted_at` IS NULL
3. クエリパラメータがあればさらにフィルタ（`status`, `assignee_id`）
4. 各タスクに `task_assignee` から担当者情報を付与
5. ソート：`end_date` 昇順 → `actual_start_date` 昇順
6. 以下の条件でグループに振り分け
   - `overdue`：`end_date` ≤ today
   - `starting_this_week`：today ≤ `start_date` ≤ today + 7日
   - `in_progress`：`actual_start_date` IS NOT NULL
7. レスポンス返却
