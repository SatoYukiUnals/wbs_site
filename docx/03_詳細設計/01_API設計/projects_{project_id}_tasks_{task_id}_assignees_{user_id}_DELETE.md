# 【API設計書】担当者削除API

## 1. 概要

タスクから担当者を除外する。

## 2. エンドポイント

- **Method:** `DELETE`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/assignees/{user_id}/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

パスパラメータ: `project_id`, `task_id`, `user_id`

## 4. レスポンス

204 No Content

### エラー

| 状況 | ステータス |
|---|---|
| 担当者が存在しない | 404 |

## 5. 内部処理

1. 権限チェック
2. `task_assignee` レコードを DELETE
3. 204 を返す
