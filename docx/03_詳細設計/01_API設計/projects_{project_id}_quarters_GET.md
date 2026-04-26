# 【API設計書】クォーター一覧API

## 1. 概要

プロジェクト内のクォーター一覧を進捗率付きで取得する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/quarters/`
- **認証:** 必要 / **権限:** プロジェクトメンバー以上

## 3. リクエスト

パスパラメータ `project_id` のみ

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "quarters": [
    {
      "quarter_id": "uuid",
      "title": "Q1",
      "start_date": "2026-04-01",
      "end_date": "2026-06-30",
      "progress": 60
    }
  ]
}
```

## 5. 内部処理 / ロジック

1. プロジェクトメンバー確認
2. `quarter` テーブルから `project_id` でフィルタして取得（`start_date` 昇順）
3. レスポンス返却
