# 【API設計書】プロジェクト進捗詳細API

## 1. 概要

プロジェクト・クォーター・担当者別の進捗詳細を返す。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/progress/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. レスポンス

```json
{
  "project_progress": 40,
  "quarters": [
    {"quarter_id": "uuid", "title": "Q1", "progress": 60}
  ],
  "by_status": {
    "未着手": 10,
    "進行中": 8,
    "レビュー待ち": 2,
    "完了": 5,
    "保留": 1
  },
  "by_assignee": [
    {"user_id": "uuid", "username": "山田太郎", "task_count": 6, "completed_count": 3}
  ]
}
```

## 5. 内部処理

1. プロジェクトメンバー確認
2. `project.progress` を返す
3. `quarter` テーブルから進捗一覧を取得
4. `task` テーブルからステータス別集計・担当者別集計を行う
5. レスポンス返却
