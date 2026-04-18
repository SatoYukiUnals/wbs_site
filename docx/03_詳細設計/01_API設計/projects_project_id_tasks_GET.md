# 【API設計書】タスク一覧取得

## 1. 概要

指定プロジェクトのタスク一覧をツリー構造で返す。担当者・ステータス・クォーターによるフィルタリングに対応。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/tasks/`
- **認証:** JWT必須（プロジェクトメンバー以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

### クエリパラメータ

#### `status`（ステータスフィルタ）

- **型:** `string` / **必須:** -
- `未着手` / `進行中` / `レビュー待ち` / `完了` / `保留` のいずれか

#### `assignee`（担当者フィルタ）

- **型:** `integer` / **必須:** -
- `user_id`

#### `quarter_id`（クォーターフィルタ）

- **型:** `integer` / **必須:** -

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "要件定義",
      "parent_task_id": null,
      "depth": 1,
      "order": 1,
      "status": "完了",
      "progress": 100,
      "priority": "高",
      "start_date": "2026-04-01",
      "end_date": "2026-04-15",
      "estimated_hours": 16,
      "quarter_id": 1,
      "assignees": [{"user_id": 1, "username": "hanako"}],
      "children": [
        {
          "id": 2,
          "title": "ヒアリング",
          "parent_task_id": 1,
          "depth": 2,
          "order": 1,
          "status": "完了",
          "progress": 100,
          "children": []
        }
      ]
    }
  ]
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足 | 403 | `ERR_PERM_001` | この操作を行う権限がありません | |
| 対象未存在 | 404 | `ERR_DAT_404` | 対象のデータが見つかりませんでした | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証・メンバー確認**
   - `ProjectMember` でメンバーシップを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 非メンバー：403 `ERR_PERM_001` を返す
2. **クエリパラメータ検証**
   - `status` の値チェック（指定時）
3. **データ取得**
   - `Task` テーブルを `project_id` + フィルタ条件で SELECT
   - `TaskAssignee` を JOIN して担当者情報を取得
     - DBエラー：500 `ERR_SYS_500` を返す
4. **ツリー構造化**
   - `parent_task_id` をもとに再帰的にネストして `children` を構築
5. **レスポンス生成**
   - ツリー構造のタスク一覧を返却
