# 【API設計書】タスク一覧API

## 1. 概要

プロジェクトのタスクをツリー構造（最大5層）で取得する。論理削除済みは除外。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/tasks/`
- **認証:** 必要 / **権限:** プロジェクトメンバー以上

## 3. リクエスト

### クエリパラメータ（任意）

| パラメータ | 型 | 説明 |
|---|---|---|
| `quarter_id` | UUID | 指定クォーターのタスクのみ取得 |
| `status` | string | ステータスでフィルタ |
| `assignee_id` | UUID | 担当者でフィルタ |

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "title": "1. 要件定義",
      "parent_task_id": null,
      "status": "完了",
      "priority": "高",
      "progress": 100,
      "start_date": "2026-04-01",
      "end_date": "2026-04-14",
      "estimated_hours": 40.0,
      "quarter_id": "uuid",
      "assignees": [{"user_id": "uuid", "username": "山田太郎"}],
      "order": 1,
      "children": [
        {
          "task_id": "uuid",
          "title": "1.1 ヒアリング",
          "parent_task_id": "uuid",
          "children": []
        }
      ]
    }
  ]
}
```

## 5. 内部処理 / ロジック

1. プロジェクトメンバー確認
2. `task` テーブルから `project_id` でフィルタ・`deleted_at IS NULL`
3. クエリパラメータがあればさらにフィルタ
4. `order` 昇順で取得し、`parent_task_id` を元に再帰的にツリーを構築
5. 各タスクに `task_assignee` から担当者情報を付与
6. レスポンス返却
