# 【API設計書】報告書PDF出力

## 1. 概要

フロントエンドで編集済みの報告書内容を受け取り、PDFバイナリとして返す。WeasyPrint または ReportLab を使用してHTMLベースのPDFを生成する。DBへの保存は行わない。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/reports/export/pdf/`
- **認証:** JWT必須（プロジェクトメンバー以上）

## 3. リクエスト

### パスパラメータ

#### `project_id`（プロジェクトID）

- **型:** `integer` / **必須:** ○

### ボディ

#### `sections`（報告書セクション）

- **型:** `object` / **必須:** ○

| フィールド | 型 | 必須 | 内容 |
| :--- | :--- | :--- | :--- |
| `overview` | string | ○ | プロジェクト概要 |
| `summary` | string | ○ | 進捗サマリー |
| `quarters` | string | - | クォーター別進捗 |
| `tasks` | string | - | タスク一覧 |
| `delayed` | string | - | 遅延タスク |
| `reviews` | string | - | レビュー状況 |

#### `title`（報告書タイトル）

- **型:** `string` / **必須:** -
- 省略時はプロジェクト名から自動生成

## 4. レスポンス

### 成功 (200 OK)

- `Content-Type: application/pdf`
- `Content-Disposition: attachment; filename="{プロジェクト名}_報告書_{日付}.pdf"`
- レスポンスボディ：PDFバイナリ

### エラー (4xx / 5xx)

| 状況 | ステータス | エラーコード | メッセージ内容 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 未認証 | 401 | `ERR_AUTH_002` | 認証が必要です | |
| 権限不足 | 403 | `ERR_PERM_001` | この操作を行う権限がありません | |
| バリデーションエラー | 400 | `ERR_VAL_001` | 入力内容に不備があります | |
| PDF生成失敗 | 500 | `ERR_SYS_500` | システムエラーが発生しました | |

## 5. 内部処理 / ロジック

1. **JWT検証・メンバー確認**
   - `ProjectMember` でメンバーシップを確認
     - 未認証：401 `ERR_AUTH_002` を返す
     - 非メンバー：403 `ERR_PERM_001` を返す
2. **バリデーション**
   - `sections.overview`・`sections.summary` の存在チェック
     - エラー時：400 `ERR_VAL_001` を返す
3. **HTML組み立て**
   - 各セクションのテキストをHTMLテンプレートに埋め込み
4. **PDF生成**
   - WeasyPrint または ReportLab でHTMLからPDFバイナリを生成
     - 生成失敗：500 `ERR_SYS_500` を返す
5. **レスポンス生成**
   - PDFバイナリをダウンロードレスポンスとして返却
