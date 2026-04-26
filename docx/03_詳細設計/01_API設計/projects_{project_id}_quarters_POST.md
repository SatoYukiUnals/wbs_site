# 【API設計書】クォーター作成API

## 1. 概要

プロジェクト内にクォーターを新規作成する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/quarters/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{
  "title": "Q1",
  "start_date": "2026-04-01",
  "end_date": "2026-06-30"
}
```

- `title`: string, 必須, 1〜100文字
- `start_date`: date, 必須
- `end_date`: date, 必須, `start_date` より後

## 4. レスポンス

### 成功 (201 Created)

```json
{
  "quarter_id": "uuid",
  "title": "Q1",
  "start_date": "2026-04-01",
  "end_date": "2026-06-30",
  "progress": 0
}
```

### エラー

| 状況 | ステータス |
|---|---|
| end_date ≤ start_date | 400 |
| 権限不足 | 403 |

## 5. 内部処理 / ロジック

1. 権限チェック（admin 以上）
2. バリデーション（end_date > start_date）
3. `quarter` テーブルへ INSERT
4. 201 で返す
