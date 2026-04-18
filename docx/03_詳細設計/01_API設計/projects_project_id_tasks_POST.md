# 【API設計書】タスク作成

## 1. 概要

指定プロジェクトにタスクを新規作成する。admin 以上のみ実行可能。`parent_task_id` を指定して子タスクとして作成可能。階層が5層を超える場合はエラー。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/`
- **認証:** JWT必須（プロジェクト内 admin 以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

### ボディ

#### `title`（タイトル）

- **型:** `string` / **必須:** ○
- 1〜200文字

#### `description`（説明）

- **型:** `string` / **必須:** -

#### `parent_task_id`（親タスクID）

- **型:** `integer` / **必須:** -
- 指定時：同プロジェクト内のタスクIDであること

#### `start_date`（開始日）

- **型:** `date` / **必須:** -
- YYYY-MM-DD

#### `end_date`（終了日）

- **型:** `date` / **必須:** -
- YYYY-MM-DD。`start_date` 以降であること

#### `estimated_hours`（工数）

- **型:** `number` / **必須:** -
- 0以上

#### `priority`（優先度）

- **型:** `string` / **必須:** -
- `高` / `中` / `低` のいずれか

#### `quarter_id`（クォーターID）

- **型:** `integer` / **必須:** -
- 同プロジェクト内のクォーターIDであること

## 4. レスポンス

### 成功 (201 Created)

```json
{
  "id": 10,
  "title": "新規タスク",
  "parent_task_id": 1,
  "depth": 2,
  "order": 5,
  "status": "未着手",
  "progress": 0,
  "priority": "中",
  "start_date": "2026-05-01",
  "end_date": "2026-05-15",
  "estimated_hours": 8,
  "quarter_id": 1,
  "assignees": []
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足 | 403 | `ERR_PERM_001` | この操作を行う権限がありません | |
| バリデーションエラー | 400 | `ERR_VAL_001` | 入力内容に不備があります | |
| 階層超過 | 400 | `ERR_VAL_008` | タスクの階層は5層までです | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証・権限確認**
   - `ProjectMember` でリクエスト元の `role` が `admin` 以上であることを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 権限不足：403 `ERR_PERM_001` を返す
2. **バリデーション**
   - `title` の存在・長さチェック
   - `start_date` ≤ `end_date` チェック
   - `priority`・`status` の値チェック
     - エラー時：400 `ERR_VAL_001` を返す
3. **階層チェック**（`parent_task_id` 指定時）
   - 親タスクが同 `project_id` 内に存在することを確認
   - 親タスクの depth を取得し、depth + 1 ≤ 5 であることを確認
     - 超過：400 `ERR_VAL_008` を返す
4. **DB操作**
   - `Task` レコードを INSERT（`status` = `未着手`・`progress` = 0・`order` = 同一親タスク内の末尾）
     - DBエラー：500 `ERR_SYS_500` を返す
5. **レスポンス生成**
   - 作成したタスク情報を返却
