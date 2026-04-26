# 【API設計書】ガントチャートデータ取得API

## 1. 概要

ガントチャート描画に必要なクォーター一覧とタスク一覧（開始日・終了日・進捗率・ステータス）を返す。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/gantt/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. レスポンス

```json
{
  "quarters": [
    {"quarter_id": "uuid", "title": "Q1", "start_date": "2026-04-01", "end_date": "2026-06-30"}
  ],
  "tasks": [
    {
      "task_id": "uuid",
      "title": "1.1 ヒアリング",
      "parent_task_id": null,
      "start_date": "2026-04-01",
      "end_date": "2026-04-07",
      "progress": 50,
      "status": "進行中",
      "order": 1
    }
  ]
}
```

## 5. 内部処理

1. プロジェクトメンバー確認
2. `quarter` テーブルから `project_id` でフィルタして取得
3. `task` テーブルから `project_id`・`deleted_at IS NULL` でフィルタして取得
4. タスクは `order` 昇順で返す（start_date が NULL のものも含む）
