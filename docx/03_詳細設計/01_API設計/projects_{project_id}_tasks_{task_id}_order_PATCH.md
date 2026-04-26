# 【API設計書】タスク並び替えAPI

## 1. 概要

ドラッグ&ドロップ後の新しい `order` 値でタスクの表示順を更新する。

## 2. エンドポイント

- **Method:** `PATCH`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/order/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{
  "order": 3,
  "parent_task_id": "uuid または null"
}
```

## 4. レスポンス

200 OK `{"task_id": "uuid", "order": 3}`

## 5. 内部処理 / ロジック

1. 権限チェック
2. `task.order` と `task.parent_task_id` を UPDATE
3. 同一親配下の他タスクの `order` を再計算・UPDATE
4. 200 で返す
