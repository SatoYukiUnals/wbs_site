# 【API設計書】タスク部分更新API

## 1. 概要

タスクのステータス・進捗率を部分更新する。担当者は自分のタスクのみ更新可能。

## 2. エンドポイント

- **Method:** `PATCH`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/`
- **認証:** 必要 / **権限:** 担当者 or admin 以上

## 3. リクエスト

```json
{
  "status": "進行中",
  "progress": 50
}
```

- `status`: string, 任意, 「未着手 / 進行中 / レビュー待ち / 完了 / 保留」のいずれか
- `progress`: integer, 任意, 0〜100

## 4. レスポンス

200 OK で更新後のタスク情報を返す

### エラー

| 状況 | ステータス |
|---|---|
| 担当外かつ admin でない | 403 |
| `progress` が 0〜100 外 | 400 |

## 5. 内部処理 / ロジック

1. 権限チェック：admin 以上 または `task_assignee` に自分が含まれること
2. バリデーション（progress 0〜100）
3. 指定フィールドのみ UPDATE
4. ステータス変更時は `task_status_history` に INSERT
5. 進捗率再集計
6. 200 で返す
