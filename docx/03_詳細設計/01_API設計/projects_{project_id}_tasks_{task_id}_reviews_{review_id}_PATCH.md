# 【API設計書】レビュー更新API

## 1. 概要

レビューのステータスを変更・コメントを編集する。完了済みレビューは操作不可。

## 2. エンドポイント

- **Method:** `PATCH`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/{review_id}/`
- **認証:** 必要

## 3. リクエスト

```json
{
  "status": "確認待ち",
  "comment_id": "uuid",
  "comment_body": "修正しました"
}
```

## 4. レスポンス

200 OK で更新後のレビュー情報を返す

### エラー

| 状況 | ステータス |
|---|---|
| レビューが「完了」 | 403 |
| 権限外（指摘者・対応者以外） | 403 |

## 5. 内部処理

1. レビューが「完了」でないことを確認
2. 操作者が指摘者または対応者であることを確認
3. `status` が指定されていれば `review.status` を UPDATE・`review_history` に INSERT
4. `comment_body` が指定されていれば `review_comment.body` を UPDATE（先頭に「ユーザー名 日時」を付与）
5. 200 で返す
