# 【インターフェイス仕様書】PDF報告書出力

## 1. 処理概要

- **出力の目的**：プロジェクトの進捗状況をPDF形式の報告書として出力し、ステークホルダーへの報告・提出に使用する。
- **出力形式**：PDF（WeasyPrint または ReportLab を使用）
- **対象データ範囲**：指定プロジェクトの指定期間（`start_date`〜`end_date`）に開始日または終了日が含まれるタスク。ステータスを問わず全タスクを対象とする。
- **実行タイミング**：`POST /api/v1/projects/{project_id}/reports/export-pdf/` 呼び出し時（報告書作成画面のPDF出力ボタン押下）
- **ファイル名**：`Report_{プロジェクト名}_{YYYYMMDD}.pdf`
- **ソート順**：`order`（並び順）昇順

---

## 2. 項目一覧

### セクション1：表紙

| No | 項目名 | 物理名 | 型 | 必須 | 繰り返し | 参照先テーブル | 参照先カラム | 変換・抽出ロジック | 備考 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | プロジェクト名 | `project_name` | `string` | ○ | - | `projects` | `name` | そのまま出力 | |
| 2 | 報告期間 | `report_period` | `string` | ○ | - | リクエストパラメータ | `start_date`, `end_date` | `YYYY年MM月DD日 〜 YYYY年MM月DD日` 形式に変換 | |
| 3 | 出力日 | `export_date` | `string` | ○ | - | システム日付 | - | `YYYY年MM月DD日` 形式に変換 | |
| 4 | 作成者 | `created_by` | `string` | ○ | - | `users` | `username` | JWTの `user_id` からユーザー名を取得 | |

### セクション2：プロジェクトサマリー

| No | 項目名 | 物理名 | 型 | 必須 | 繰り返し | 参照先テーブル | 参照先カラム | 変換・抽出ロジック | 備考 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 全体進捗率 | `overall_progress` | `integer` | ○ | - | `tasks` | `progress_rate` | 対象タスクの `progress_rate` 平均値（小数点以下切り捨て） | % |
| 2 | 総タスク数 | `total_tasks` | `integer` | ○ | - | `tasks` | `id` | COUNT | |
| 3 | 完了タスク数 | `completed_tasks` | `integer` | ○ | - | `tasks` | `status` | `status = 'completed'` の COUNT | |
| 4 | 進行中タスク数 | `in_progress_tasks` | `integer` | ○ | - | `tasks` | `status` | `status = 'in_progress'` の COUNT | |
| 5 | 未着手タスク数 | `not_started_tasks` | `integer` | ○ | - | `tasks` | `status` | `status = 'not_started'` の COUNT | |
| 6 | 期限超過タスク数 | `overdue_tasks` | `integer` | ○ | - | `tasks` | `end_date`, `status` | `end_date < 本日` かつ `status != 'completed'` の COUNT | |

### セクション3：タスク一覧

| No | 項目名 | 物理名 | 型 | 必須 | 繰り返し | 参照先テーブル | 参照先カラム | 変換・抽出ロジック | 備考 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | タスクNo | `task_no` | `string` | ○ | ○ | `tasks` | `order` | 階層パスを「1.1.2」形式で生成 | |
| 2 | タスク名 | `title` | `string` | ○ | ○ | `tasks` | `title` | そのまま出力。階層レベルに応じてインデント表現 | |
| 3 | ステータス | `status` | `string` | ○ | ○ | `tasks` | `status` | `not_started`→「未着手」/ `in_progress`→「進行中」/ `completed`→「完了」/ `on_hold`→「保留」に変換 | |
| 4 | 進捗率 | `progress_rate` | `integer` | ○ | ○ | `tasks` | `progress_rate` | そのまま出力（% 付き） | |
| 5 | 開始日 | `start_date` | `string` | - | ○ | `tasks` | `start_date` | `YYYY/MM/DD` 形式（NULL時は「-」） | |
| 6 | 終了日 | `end_date` | `string` | - | ○ | `tasks` | `end_date` | `YYYY/MM/DD` 形式（NULL時は「-」） | |
| 7 | 担当者 | `assignees` | `string` | - | ○ | `task_assignees` / `users` | `user_id` / `username` | `task_id` でJOINし、ユーザー名を「、」区切りで結合 | |

### セクション4：メンバー別進捗

| No | 項目名 | 物理名 | 型 | 必須 | 繰り返し | 参照先テーブル | 参照先カラム | 変換・抽出ロジック | 備考 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | ユーザー名 | `username` | `string` | ○ | ○ | `users` | `username` | プロジェクトメンバーの一覧 | |
| 2 | 担当タスク数 | `assigned_count` | `integer` | ○ | ○ | `task_assignees` | `user_id` | 対象期間内の担当タスク数 COUNT | |
| 3 | 完了タスク数 | `completed_count` | `integer` | ○ | ○ | `tasks` / `task_assignees` | `status` | 対象ユーザーの `status = 'completed'` の COUNT | |
| 4 | 平均進捗率 | `avg_progress` | `integer` | ○ | ○ | `tasks` / `task_assignees` | `progress_rate` | 対象ユーザー担当タスクの `progress_rate` 平均（小数点以下切り捨て） | % |

---

## 3. 備考

- タスクが0件の場合、セクション3は「対象期間内にタスクはありません」と出力する。
- 用紙サイズ：A4縦。ページ番号をフッターに出力する（例: `1 / 3`）。
- Content-Type: `application/pdf`、Content-Disposition: `attachment; filename="Report_xxx_YYYYMMDD.pdf"` でレスポンスを返す。
- セクション2の全体進捗率はプログレスバー（横棒グラフ）として視覚的に出力する。
- 期限超過タスクはセクション3でテキストを赤色で出力する。
