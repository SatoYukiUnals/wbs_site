# 【API設計書】自動割り振りプレビューAPI

## 1. 概要

未担当タスクをメンバーへ均等割り振りした結果をプレビューとして返す。DBは変更しない。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/auto-assign/preview/`
- **認証:** 必要 / **権限:** admin 以上

## 3. リクエスト

```json
{
  "priority_order": ["uuid_layer1_task1", "uuid_layer1_task2"]
}
```

- `priority_order`: 第1層タスクIDを優先度順に並べたリスト（任意。省略時は `priority` フィールド順）

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "preview": [
    {
      "task_id": "uuid",
      "task_title": "1.1 ヒアリング",
      "assigned_user_id": "uuid",
      "assigned_username": "山田太郎"
    }
  ]
}
```

## 5. 内部処理 / ロジック

1. 権限チェック
2. プロジェクトメンバー一覧取得
3. 第1層タスクを優先度順に処理し、その配下タスクをメンバーへラウンドロビンで割り振り計算
4. DB変更なしでプレビュー結果を返す
