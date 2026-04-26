# 【API設計書】テンプレート適用API

## 1. 概要

WBSテンプレートを指定タスクの配下に適用し、子タスクを一括生成する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/apply-template/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{"template_id": "uuid"}
```

## 4. レスポンス

201 Created

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
| テンプレートが存在しない・テナント外 | 404 |
| 階層5層超過 | 400 |
| 対象タスクがタスクテンプレートタイプ | 400 |

## 5. 内部処理

1. 権限チェック
2. `template_id` で `wbs_template` を検索（テナント確認・`is_shared` または 自分作成）
3. テンプレートが `task` タイプの場合は 400 を返す
4. 親タスクの階層チェック
5. `content` を改行で分割し、各行をタスクタイトルとして `task` テーブルへ INSERT
6. 201 で返す
