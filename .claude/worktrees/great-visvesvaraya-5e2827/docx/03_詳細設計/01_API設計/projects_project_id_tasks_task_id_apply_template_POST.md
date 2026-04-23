# 【API設計書】WBSテンプレート適用

## 1. 概要

指定タスクの直下に、WBSテンプレートの内容を改行分割して子タスクを一括生成する。admin 以上のみ実行可能。親タスクの階層が5層目の場合はエラー（子タスクを追加できない）。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/tasks/{task_id}/apply-template/`
- **認証:** JWT必須（プロジェクト内 admin 以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

#### `task_id`（親タスクID）

- **型:** `integer` / **必須:** ○

### ボディ

#### `template_id`（テンプレートID）

- **型:** `integer` / **必須:** ○
- アクセス可能なテンプレート（自分の個人テンプレート or 共有テンプレート）であること

## 4. レスポンス

### 成功 (201 Created)

```json
{
  "tasks": [
    {
      "id": 20,
      "title": "フロントエンド実装",
      "parent_task_id": 5,
      "depth": 3,
      "status": "未着手",
      "progress": 0
    },
    {
      "id": 21,
      "title": "バックエンド実装",
      "parent_task_id": 5,
      "depth": 3,
      "status": "未着手",
      "progress": 0
    }
  ]
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足 | 403 | `ERR_PERM_001` | この操作を行う権限がありません | |
| 対象未存在 | 404 | `ERR_DAT_404` | 対象のデータが見つかりませんでした | タスク or テンプレート |
| 階層超過 | 400 | `ERR_VAL_008` | タスクの階層は5層までです | 親が5層目の場合 |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証・権限確認**
   - `ProjectMember` でリクエスト元の `role` が `admin` 以上であることを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 権限不足：403 `ERR_PERM_001` を返す
2. **親タスク確認**
   - `Task` を `task_id` AND `project_id` で SELECT
     - 未存在：404 `ERR_DAT_404` を返す
3. **階層チェック**
   - 親タスクの depth が 5 でないことを確認
     - depth == 5：400 `ERR_VAL_008` を返す
4. **テンプレート取得**
   - `Template` を `template_id` で SELECT
   - `is_shared = True` OR `created_by = user_id` であることを確認
     - 未存在 or アクセス不可：404 `ERR_DAT_404` を返す
5. **タイトル生成**
   - `template.content` を `\n` で分割して各行をタイトルとして抽出
6. **DB操作（トランザクション）**
   - 各行を `title` として子タスクを一括 INSERT（`parent_task_id` = `task_id`・`status` = `未着手`・`progress` = 0）
     - DBエラー：500 `ERR_SYS_500` を返す
7. **レスポンス生成**
   - 作成した子タスク一覧を返却
