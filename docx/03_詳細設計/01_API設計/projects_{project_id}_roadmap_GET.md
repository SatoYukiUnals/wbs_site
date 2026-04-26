# 【API設計書】ロードマップ一覧API

## 1. 概要

プロジェクトのロードマップアイテムをクォーター情報と共に返す。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/roadmap/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. レスポンス

```json
{
  "roadmap_items": [
    {
      "item_id": "uuid",
      "title": "認証機能リリース",
      "description": "説明",
      "quarter_id": "uuid",
      "quarter_title": "Q1",
      "status": "完了",
      "order": 1
    }
  ]
}
```

## 5. 内部処理

1. プロジェクトメンバー確認
2. `roadmap_item` テーブルから `project_id` でフィルタ・`quarter.title` JOINして `order` 昇順で返す
