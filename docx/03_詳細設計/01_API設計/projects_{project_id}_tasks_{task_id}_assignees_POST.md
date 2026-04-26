# 【API設計書】担当者追加API

## 1. 概要

タスクに担当者を追加する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/assignees/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{"user_id": "uuid"}
```

## 4. レスポンス

201 Created `{"user_id": "uuid", "username": "山田太郎"}`

### エラー

| 状況 | ステータス |
|---|---|
| プロジェクト外ユーザー | 400 |
| 既に担当者 | 409 |

## 5. 内部処理

1. 権限チェック
2. ユーザーがプロジェクトメンバーか確認
3. `task_assignee` に INSERT
