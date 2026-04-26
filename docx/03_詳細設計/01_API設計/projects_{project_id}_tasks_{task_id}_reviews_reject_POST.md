# 【API設計書】レビュー差し戻しAPI

## 1. 概要

指摘コメントを付けてタスクを差し戻し、タスクステータスを「進行中」に戻す。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/reject/`
- **認証:** 必要 / **権限:** 担当者以外のプロジェクトメンバー

## 3. リクエスト

```json
{
  "comments": ["仕様と異なります", "テストが不足しています"]
}
```

- `comments`: string[], 必須, 1件以上

## 4. レスポンス

200 OK `{"review_id": "uuid", "status": "rejected", "task_status": "進行中"}`

### エラー

| 状況 | ステータス |
|---|---|
| 担当者本人 | 403 |
| `comments` が0件 | 400 |
| タスクがレビュー待ち以外 | 400 |

## 5. 内部処理

1. 担当者本人でないことを確認
2. `comments` が1件以上あることを確認
3. トランザクション：`review.status=rejected` UPDATE → `review_comment` を件数分 INSERT → `task.status=進行中` UPDATE → `review_history` INSERT
4. 200 で返す
