# 【API設計書】タスク全項目更新API

## 1. 概要

タスクの全項目を更新する。admin 以上のみ実行可能。

## 2. エンドポイント

- **Method:** `PUT`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

`projects_{project_id}_tasks_POST.md` のボディと同一

## 4. レスポンス

200 OK で更新後のタスク情報を返す

## 5. 内部処理 / ロジック

1. 権限チェック（admin 以上）
2. バリデーション（end_date > start_date）
3. `task` を UPDATE
4. `task_assignee` を DELETE→INSERT で更新（トランザクション）
5. 進捗率を再集計（クォーター→プロジェクト順）
6. 200 で返す
