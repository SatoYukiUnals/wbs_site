# 【API設計書】レビュー情報取得API

## 1. 概要

タスクの現在のレビュー状況・コメント・操作履歴を取得する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. レスポンス

```json
{
  "review": {
    "review_id": "uuid",
    "status": "差し戻し",
    "reviewer_id": "uuid",
    "reviewer_name": "田中花子"
  },
  "comments": [
    {
      "comment_id": "uuid",
      "body": "実装が仕様と異なります",
      "author_id": "uuid",
      "author_name": "田中花子",
      "created_at": "2026-04-10T10:00:00Z"
    }
  ],
  "history": [
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
2. `review` テーブルから `task_id` で検索
3. `review_comment`・`review_history` を JOIN して返す
