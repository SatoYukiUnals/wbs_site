# 【API設計書】自動割り振り確定API

## 1. 概要

プレビュー結果を確認した管理者が承認し、担当者割り振りをDBに反映する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/auto-assign/confirm/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{
  "assignments": [
    {"task_id": "uuid", "user_id": "uuid"},
    {"task_id": "uuid", "user_id": "uuid"}
  ]
}
```

## 4. レスポンス

201 Created `{"log_id": "uuid", "assigned_count": 10}`

## 5. 内部処理

1. 権限チェック
2. 対象タスクの `task_assignee` を DELETE→INSERT で一括更新（トランザクション）
3. `auto_assign_log` に結果を JSON で記録
4. 201 で返す
