# 【API設計書】クォーター詳細API

## 1. 概要

指定クォーターの詳細情報を取得する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/quarters/{quarter_id}/`
- **認証:** 必要 / **権限:** プロジェクトメンバー以上

## 3. リクエスト

パスパラメータ: `project_id`, `quarter_id`

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "quarter_id": "uuid",
  "title": "Q1",
  "start_date": "2026-04-01",
  "end_date": "2026-06-30",
  "progress": 60
}
```

### エラー

| 状況 | ステータス |
|---|---|
| 存在しない | 404 |
| メンバーでない | 403 |

## 5. 内部処理 / ロジック

1. プロジェクトメンバー確認
2. `quarter` テーブルから `quarter_id` かつ `project_id` で検索
3. 返す
