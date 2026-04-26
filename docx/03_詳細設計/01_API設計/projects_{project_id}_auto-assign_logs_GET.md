# 【API設計書】自動割り振り履歴API

## 1. 概要

プロジェクトの自動割り振り履歴を一覧取得する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/auto-assign/logs/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

パスパラメータのみ

## 4. レスポンス

```json
{
  "logs": [
    {
      "log_id": "uuid",
      "executed_by": "uuid",
      "executed_username": "山田太郎",
      "executed_at": "2026-04-10T10:00:00Z",
      "assigned_count": 10
    }
  ]
}
```

## 5. 内部処理

1. 権限チェック
2. `auto_assign_log` から `project_id` でフィルタ・`executed_at` 降順で返す
