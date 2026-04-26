# 【API設計書】タスク作成API

## 1. 概要

タスクを1件作成する。`parent_task_id` 指定時は階層（最大5層）チェックを行う。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{
  "title": "1.1 ヒアリング",
  "description": "ステークホルダーへのヒアリング",
  "parent_task_id": "uuid または null",
  "quarter_id": "uuid または null",
  "start_date": "2026-04-01",
  "end_date": "2026-04-07",
  "estimated_hours": 8.0,
  "priority": "高",
  "assignees": ["uuid1", "uuid2"]
}
```

- `title`: string, 必須, 1〜300文字
- `end_date`: `start_date` より後であること
- 階層: `parent_task_id` を再帰的にたどって 5層を超えてはならない

## 4. レスポンス

### 成功 (201 Created)

作成したタスクの全フィールドを返す

### エラー

| 状況 | ステータス |
|---|---|
| 階層5層超過 | 400 |
| end_date ≤ start_date | 400 |
| 担当者がプロジェクト外 | 400 |
| 権限不足 | 403 |

## 5. 内部処理 / ロジック

1. 権限チェック（admin 以上）
2. バリデーション（end_date > start_date）
3. 階層チェック：`parent_task_id` の祖先を再帰的にカウントし 5 を超えるなら 400
4. `task` テーブルへ INSERT
5. `task_assignee` レコードを担当者分 INSERT（トランザクション）
6. 201 で返す
