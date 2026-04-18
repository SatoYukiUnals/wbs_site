# 【API設計書】自動割り振り履歴一覧取得

## 1. 概要

指定プロジェクトの自動割り振り実行履歴一覧を返す。admin 以上のみ閲覧可能。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/auto-assign/logs/`
- **認証:** JWT必須（プロジェクト内 admin 以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "logs": [
    {
      "id": 5,
      "executed_by": {
        "user_id": 1,
        "username": "hanako"
      },
      "executed_at": "2026-04-17T10:00:00Z",
      "assigned_count": 8
    }
  ]
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足 | 403 | `ERR_PERM_001` | この操作を行う権限がありません | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証・権限確認**
   - `ProjectMember` でリクエスト元の `role` が `admin` 以上であることを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 権限不足：403 `ERR_PERM_001` を返す
2. **データ取得**
   - `AutoAssignLog` を `project_id` でフィルタして全件 SELECT（新しい順）
   - `User` を JOIN して実行者情報を取得
     - DBエラー：500 `ERR_SYS_500` を返す
3. **レスポンス生成**
   - 履歴一覧を返却
