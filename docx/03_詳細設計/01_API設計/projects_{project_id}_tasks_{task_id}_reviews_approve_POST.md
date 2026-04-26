# 【API設計書】レビュー承認API

## 1. 概要

タスクのレビューを承認し、タスクステータスを「完了」に変更する。担当者本人は実行不可。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/reviews/approve/`
- **認証:** 必要 / **権限:** 担当者以外のプロジェクトメンバー

## 3. リクエスト

```json
{"comment": "問題ありません（任意）"}
```

## 4. レスポンス

200 OK `{"review_id": "uuid", "status": "approved", "task_status": "完了"}`

### エラー

| 状況 | ステータス |
|---|---|
| 担当者本人 | 403 |
| タスクがレビュー待ち以外 | 400 |

## 5. 内部処理

1. 担当者本人でないことを確認
2. タスクが「レビュー待ち」であることを確認
3. トランザクション：`review.status=approved` UPDATE → `task.status=完了` UPDATE → `review_history` INSERT
4. 進捗率再集計
5. 200 で返す
