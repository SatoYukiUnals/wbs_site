# 【API設計書】ダッシュボードAPI

## 1. 概要

ログインユーザーが参加しているプロジェクトの進捗サマリーと、自分の担当タスク一覧を返す。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/dashboard/`
- **認証:** 必要

## 3. レスポンス

```json
{
  "projects": [
    {
      "project_id": "uuid",
      "name": "ECサイトリニューアル",
      "progress": 40,
      "my_task_count": 5,
      "my_overdue_count": 1
    }
  ],
  "my_tasks": [
    {
      "task_id": "uuid",
      "title": "1.1 ヒアリング",
      "project_name": "ECサイトリニューアル",
      "status": "進行中",
      "end_date": "2026-04-07",
      "is_overdue": false
    }
  ]
}
```

## 5. 内部処理

1. JWT の `user_id`・`tenant_id` を取得
2. `project_member` からログインユーザーが参加しているプロジェクトを取得
3. 各プロジェクトの進捗率・自担当タスク数・期限超過タスク数を集計
4. 自分が担当しているタスクを `status != '完了'` でフィルタして取得
5. 返す
