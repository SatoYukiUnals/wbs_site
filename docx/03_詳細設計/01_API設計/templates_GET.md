# 【API設計書】テンプレート一覧API

## 1. 概要

テナント内のWBSテンプレート・タスクテンプレートの一覧を返す。自分が作成したものと共有テンプレートを含む。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/templates/`
- **認証:** 必要

## 3. クエリパラメータ

| パラメータ | 型 | 説明 |
|---|---|---|
| `type` | string | `wbs` または `task`（省略時は両方） |

## 4. レスポンス

```json
{
  "wbs_templates": [
    {
      "template_id": "uuid",
      "title": "開発フロー標準",
      "content": "フロントエンド実装\nバックエンド実装\nテスト確認",
      "is_shared": true,
      "created_by": "uuid"
    }
  ],
  "task_templates": [
    {
      "template_id": "uuid",
      "title": "バグ修正テンプレート",
      "content": "原因調査\n修正実装\n動作確認",
      "is_shared": false,
      "created_by": "uuid"
    }
  ]
}
```

## 5. 内部処理

1. JWT検証
2. `wbs_template`・`task_template` テーブルから `tenant_id` + (`is_shared=true` OR `created_by=自分`) で取得
3. `type` パラメータに応じてフィルタ
4. 返す
