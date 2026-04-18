# 【API設計書】プロジェクト作成

## 1. 概要

新規プロジェクトを作成する。admin以上のみ実行可能。作成者は自動的にそのプロジェクトのメンバー（admin）として登録される。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/`
- **認証:** JWT必須（admin以上）

## 3. リクエスト

### ボディ

#### `name`（プロジェクト名）

- **型:** `string` / **必須:** ○
- 1〜200文字

#### `description`（説明）

- **型:** `string` / **必須:** -
- 最大1000文字

#### `start_date`（開始日）

- **型:** `date` / **必須:** -
- YYYY-MM-DD。`end_date` 以前であること

#### `end_date`（終了日）

- **型:** `date` / **必須:** -
- YYYY-MM-DD。`start_date` 以降であること

## 4. レスポンス

### 成功 (201 Created)

```json
{
  "id": 2,
  "name": "新規システム開発",
  "description": "説明テキスト",
  "start_date": "2026-04-01",
  "end_date": "2026-09-30",
  "progress": 0,
  "created_by": 1,
  "created_at": "2026-04-17T00:00:00Z"
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足 | 403 | `ERR_PERM_001` | この操作を行う権限がありません | |
| バリデーションエラー | 400 | `ERR_VAL_001` | 入力内容に不備があります | |
| サーバーエラー | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証・権限チェック**
   - `role` が `admin` または `master` であることを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 権限不足：403 `ERR_PERM_001` を返す
2. **バリデーション**
   - `name` の存在・長さチェック
   - `start_date` ≤ `end_date` チェック（両方指定時）
     - エラー時：400 `ERR_VAL_001` を返す
3. **DB操作（トランザクション）**
   - `Project` レコードを INSERT（`tenant_id` = JWTの `tenant_id`・`created_by` = `user_id`・`progress` = 0）
   - 作成者を `ProjectMember` に INSERT（`role` = `admin`）
     - DBエラー：500 `ERR_SYS_500` を返す
4. **レスポンス生成**
   - 作成したプロジェクト情報を返却
