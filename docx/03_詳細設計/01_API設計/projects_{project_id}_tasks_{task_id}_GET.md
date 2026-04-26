# 【API設計書】タスク詳細API

## 1. 概要

タスクの全情報（担当者・ステータス履歴含む）を取得する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/`
- **認証:** 必要 / **権限:** プロジェクトメンバー以上

## 3. リクエスト

パスパラメータ: `project_id`, `task_id`

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "task_id": "uuid",
  "title": "1.1 ヒアリング",
  "description": "説明",
  "parent_task_id": "uuid",
  "quarter_id": "uuid",
  "status": "進行中",
  "priority": "高",
  "progress": 50,
  "start_date": "2026-04-01",
  "end_date": "2026-04-07",
  "estimated_hours": 8.0,
  "assignees": [{"user_id": "uuid", "username": "山田太郎"}],
  "order": 1,
  "created_at": "2026-04-01T09:00:00Z"
}
```

## 5. 内部処理 / ロジック

1. プロジェクトメンバー確認
2. `task` テーブルから `task_id` かつ `project_id` で検索・`deleted_at IS NULL`
3. `task_assignee` JOINして担当者情報を付与
4. 返す
