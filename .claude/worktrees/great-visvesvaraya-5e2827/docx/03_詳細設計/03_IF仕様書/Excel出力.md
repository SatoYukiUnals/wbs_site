# 【インターフェイス仕様書】Excel出力

## 1. 処理概要

- **出力の目的**：プロジェクトのタスク一覧とガントチャートをExcel形式でエクスポートし、オフライン参照・外部共有に使用する。
- **出力形式**：Excel（.xlsx、openpyxl使用、シート1枚のみ：左側にタスク情報列、右側にガントチャート日付列を配置）
- **対象データ範囲**：指定プロジェクトの全タスク（クォーターID指定時はそのクォーターの期間に開始日または終了日が含まれるタスクに絞り込み）
- **実行タイミング**：`GET /api/v1/projects/{project_id}/export/excel/` 呼び出し時（Excel出力設定画面のダウンロードボタン押下）
- **ファイル名**：`WBS_{プロジェクト名}_{YYYYMMDD}.xlsx`
- **ソート順**：`order`（並び順）昇順、階層順（親タスク → 子タスク）

---

## 2. 項目一覧

### シート1：WBS（タスク情報 + ガントチャート）

1シートで構成。左側（固定列）にタスク情報、右側（可変列）にガントチャートの日付列を並べる。

#### 左側：タスク情報列（固定）

| No | 項目名 | 物理名 | 型 | 必須 | 繰り返し | 参照先テーブル | 参照先カラム | 変換・抽出ロジック | 備考 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 階層レベル | `level` | `integer` | ○ | ○ | `tasks` | `parent_task_id` | 親タスクを再帰的にたどり、深さを算出（ルートタスク=1） | インデント表現に使用、非表示列 |
| 2 | タスクNo | `task_no` | `string` | ○ | ○ | `tasks` | `order` | 階層パスを「1.1.2」形式で生成 | |
| 3 | タスク名 | `title` | `string` | ○ | ○ | `tasks` | `title` | そのまま出力 | 階層レベルに応じてインデント（スペース×2×level） |
| 4 | ステータス | `status` | `string` | ○ | ○ | `tasks` | `status` | `not_started`→「未着手」/ `in_progress`→「進行中」/ `completed`→「完了」/ `on_hold`→「保留」に変換 | |
| 5 | 進捗率 | `progress_rate` | `integer` | ○ | ○ | `tasks` | `progress_rate` | そのまま出力（%表示） | |
| 6 | 開始日 | `start_date` | `string` | - | ○ | `tasks` | `start_date` | `YYYY/MM/DD` 形式に変換（NULL時は空欄） | |
| 7 | 終了日 | `end_date` | `string` | - | ○ | `tasks` | `end_date` | `YYYY/MM/DD` 形式に変換（NULL時は空欄） | |
| 8 | 担当者 | `assignees` | `string` | - | ○ | `task_assignees` / `users` | `user_id` / `username` | `task_id` でJOINし、ユーザー名を「、」区切りで結合 | 複数名対応 |
| 9 | 説明 | `description` | `string` | - | ○ | `tasks` | `description` | そのまま出力（NULL時は空欄） | |

#### 右側：ガントチャート日付列（可変）

| No | 項目名 | 物理名 | 型 | 必須 | 繰り返し | 参照先テーブル | 参照先カラム | 変換・抽出ロジック | 備考 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | 日付列（バー） | `gantt_bar` | `string` | - | ○ | `tasks` | `start_date`, `end_date` | 出力期間の各日付列に対して、開始〜終了の範囲内は「■」、進捗率に応じた済み部分は「●」を出力 | 列数は出力期間の日数分 |

---

## 3. 備考

- タスクが0件の場合、シート1はヘッダー行のみ、シート2は日付ヘッダー行のみ出力する。
- ガントチャートシートの日付列は出力期間の開始日〜終了日の日数分生成する。クォーター指定時はクォーター期間、未指定時はプロジェクトの開始日〜終了日を使用する。
- シート1の親タスク行は背景色を薄グレーで塗りつぶし、視覚的に区別する（openpyxlのFill設定）。
- ステータスに応じてセル背景色を設定する（完了: 薄緑、保留: 薄黄）。
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`、Content-Disposition: `attachment; filename="WBS_xxx_YYYYMMDD.xlsx"` でレスポンスを返す。
