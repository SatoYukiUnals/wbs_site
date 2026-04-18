# 【API設計書】タスク全項目編集

## 1. 概要

指定タスクの全項目を更新する。admin 以上のみ実行可能。タスクの更新後、クォーター・プロジェクトの進捗率を再集計する。

## 2. エンドポイント

- **Method:** `PUT`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/`
- **認証:** JWT必須（プロジェクト内 admin 以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

#### `task_id`（タスクID）

- **型:** `integer` / **必須:** ○

### ボディ

| フィールド | 型 | 必須 | バリデーション |
| :--- | :--- | :--- | :--- |
| `title` | string | ○ | 1〜200文字 |
| `description` | string | - | |
| `start_date` | date | - | YYYY-MM-DD |
| `end_date` | date | - | `start_date` 以降 |
| `actual_start_date` | date | - | YYYY-MM-DD |
| `actual_end_date` | date | - | YYYY-MM-DD |
| `estimated_hours` | number | - | 0以上 |
| `status` | string | - | 未着手/進行中/レビュー待ち/完了/保留 |
| `progress` | integer | - | 0〜100 |
| `priority` | string | - | 高/中/低 |
| `quarter_id` | integer | - | 同プロジェクト内のクォーターID |

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "id": 1,
  "title": "要件定義 更新済み",
  "status": "完了",
  "progress": 100,
  "quarter_progress": 75,
  "project_progress": 40
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足 | 403 | `ERR_PERM_001` | この操作を行う権限がありません | |
| バリデーションエラー | 400 | `ERR_VAL_001` | 入力内容に不備があります | |
| 対象未存在 | 404 | `ERR_DAT_404` | 対象のデータが見つかりませんでした | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証・権限確認**
   - `ProjectMember` でリクエスト元の `role` が `admin` 以上であることを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 権限不足：403 `ERR_PERM_001` を返す
2. **対象タスク確認**
   - `Task` を `task_id` AND `project_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
3. **バリデーション**
   - 各フィールドの型・値・前後関係チェック
     - エラー時：400 `ERR_VAL_001` を返す
4. **DB更新（トランザクション）**
   - `Task` レコードを UPDATE
   - `ステータス` 変更時：`TaskStatusHistory` に INSERT
   - クォーター進捗率を再集計（紐付きタスクの `progress` 平均）→ `Quarter.progress` を UPDATE
   - プロジェクト進捗率を再集計（全タスクの `progress` 平均）→ `Project.progress` を UPDATE
     - DBエラー：500 `ERR_SYS_500` を返す
5. **レスポンス生成**
   - 更新後タスク情報・クォーター進捗率・プロジェクト進捗率を返却
