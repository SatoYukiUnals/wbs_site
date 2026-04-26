# 【API設計書】タスク一括作成API

## 1. 概要

複数タスクを一括で作成する。主にテンプレート適用時に使用。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/bulk/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{
  "parent_task_id": "uuid または null",
  "tasks": [
    {"title": "フロントエンド実装"},
    {"title": "バックエンド実装"},
    {"title": "テスト確認"}
  ]
}
```

- 各 `title`: 必須
- 全タスクが `parent_task_id` の直下に作成される（階層数が5を超えてはならない）

## 4. レスポンス

### 成功 (201 Created)

```json
{
  "created_tasks": [
    {"task_id": "uuid", "title": "フロントエンド実装", "order": 1},
    {"task_id": "uuid", "title": "バックエンド実装", "order": 2}
  ]
}
```

### エラー

| 状況 | ステータス |
|---|---|
| 階層5層超過 | 400 |
| いずれかのタスクの title が空 | 400 |

## 5. 内部処理 / ロジック

1. 権限チェック
2. 階層チェック（親タスクの深さ確認）
3. 全タスクを `task` テーブルへ一括 INSERT（`order` は1始まりの連番）
4. 201 で返す
