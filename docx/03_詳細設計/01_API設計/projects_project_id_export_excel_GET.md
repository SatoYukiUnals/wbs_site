# 【API設計書】WBS Excel出力

## 1. 概要

指定プロジェクトのWBSを「タスク一覧シート」と「ガントチャートシート」の2シート構成でExcel（.xlsx）として出力する。`quarter_id` クエリパラメータ指定時はそのクォーターのタスクのみ出力。実績日は手動入力値を優先し、未入力時はTaskStatusHistoryから自動補完する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/export/excel/`
- **認証:** JWT必須（全ユーザー）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

### クエリパラメータ

#### `quarter_id`（クォーター絞り込み）

- **型:** `integer` / **必須:** -
- 指定時はそのクォーターのタスクのみ出力する

## 4. レスポンス

### 成功 (200 OK)

- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment; filename="{プロジェクト名}_WBS_{出力日}.xlsx"` （クォーター指定時は `_Q1` 等を付与）
- レスポンスボディ：Excelバイナリ

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
2. **データ取得**
   - `Task` を `project_id` + `quarter_id`（指定時）でフィルタして SELECT（階層順）
   - `actual_start_date` / `actual_end_date` が NULL のタスクは `TaskStatusHistory` で自動補完（「進行中」になった日・「完了」になった日）
   - `Quarter` を `project_id` でフィルタして SELECT
   - `TaskAssignee` JOIN で担当者情報を取得
     - DBエラー：500 `ERR_SYS_500` を返す
3. **①タスク一覧シート生成（openpyxl）**
   - 列：階層番号・タスク名・担当者・開始日・終了日・実績開始日・実績終了日・工数・ステータス・進捗率・クォーター
   - 階層をインデントで表現
4. **②ガントチャートシート生成（openpyxl）**
   - X軸：月単位（クォーター範囲）
   - 1タスク2行（予定行・実績行）
   - セル色：予定行 = ブルー（#BDD7EE）、実績行 = オレンジ（#FFD966）、遅延部分 = レッド（#FF4C4C）
     - 生成失敗：500 `ERR_SYS_500` を返す
5. **レスポンス生成**
   - Excelバイナリをダウンロードレスポンスとして返却
