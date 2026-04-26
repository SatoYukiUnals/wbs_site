# 【API設計書】タスク削除API

## 1. 概要

タスクと子孫タスクを再帰的に論理削除する。

## 2. エンドポイント

- **Method:** `DELETE`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

パスパラメータ: `project_id`, `task_id`

## 4. レスポンス

204 No Content

## 5. 内部処理 / ロジック

1. 権限チェック
2. 対象タスクとその子孫全タスクの `task_id` を再帰的に収集
3. 全タスクの `deleted_at` に現在時刻を UPDATE（バルク）
4. 進捗率再集計
5. 204 を返す
