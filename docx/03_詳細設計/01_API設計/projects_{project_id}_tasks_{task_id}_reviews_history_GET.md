# 【API設計書】レビュー履歴API

## 1. 概要

タスクのレビュー操作履歴を時系列で取得する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/history/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. レスポンス

```json
{
  "history": [
    {
      "action": "request_review",
      "user_id": "uuid",
      "username": "山田太郎",
      "created_at": "2026-04-09T15:00:00Z"
    },
    {
      "action": "reject",
      "user_id": "uuid",
      "username": "田中花子",
      "created_at": "2026-04-10T10:00:00Z"
    }
  ]
}
```

## 5. 内部処理

1. プロジェクトメンバー確認
2. `review_history` テーブルから `task_id` でフィルタ・`created_at` 昇順で返す
