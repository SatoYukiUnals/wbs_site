# IF-01-01 WBS Excel出力

## 基本情報

| 項目 | 内容 |
| :--- | :--- |
| **IFID** | IF-01-01 |
| **IF名** | WBS Excel出力 |
| **出力形式** | Excel（xlsx）、2シート構成 |
| **文字コード** | UTF-8 |
| **実行タイミング** | 10-01-04 Excel出力設定画面の「Excel出力」ボタン押下時 |

---

## 目的

WBSのタスク情報を Excel（.xlsx）形式でエクスポートする。①タスク一覧シートと②ガントチャートシートの2シート構成で出力し、予定・実績の比較を色で表現する。

---

## 対象データ

- 対象プロジェクトの全タスク（出力単位=プロジェクト全体の場合）
- 出力単位=クォーター指定の場合は、対象クォーターに紐づくタスクのみ
- 論理削除済み（`deleted_at IS NOT NULL`）のタスクは除外

---

## 機能仕様

### ■ シート①：タスク一覧

| No | 項目名 | 物理名 | 型 | 繰り返し |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 階層番号 | wbs_no | string | - |
| 2 | タスク名 | title | string | - |
| 3 | 担当者 | assignees | string | - |
| 4 | 予定開始日 | start_date | date | - |
| 5 | 予定終了日 | end_date | date | - |
| 6 | 実績開始日 | actual_start_date | date | - |
| 7 | 実績終了日 | actual_end_date | date | - |
| 8 | 工数（時間） | estimated_hours | number | - |
| 9 | ステータス | status | string | - |
| 10 | 進捗率 | progress | number | - |
| 11 | クォーター | quarter_title | string | - |

#### ▶ 備考

| 項目名 | 備考 |
| :--- | :--- |
| 担当者 | 複数担当者はカンマ区切りで結合して出力 |
| 実績開始日/実績終了日 | `task.actual_start_date` が NULL の場合、`task_status_history` の「進行中」初回変更日/「完了」変更日でフォールバック |
| 階層番号 | WBS番号（例：1.2.3）を文字列で出力 |

### ■ シート②：ガントチャート

| No | 項目名 | 物理名 | 型 | 繰り返し |
| :--- | :--- | :--- | :--- | :--- |
| 1 | タスク名 | title | string | - |
| 2 | 予定行（月単位セル） | start_date〜end_date | date | 1 |
| 3 | 実績行（月単位セル） | actual_start_date〜actual_end_date | date | 2 |

#### ▶ 備考

| 項目名 | 備考 |
| :--- | :--- |
| 月単位X軸 | クォーター期間（未設定時はプロジェクト期間）を月単位に分割して列ヘッダーを生成 |
| 1タスク=2行 | 1行目が予定、2行目が実績 |

### ■ 書式（Excel出力）

| 項目名 | フォント | 文字サイズ | 太字 | 文字色 | 背景色 | セル幅 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ヘッダー行（シート①） | 游ゴシック | 10 | ✅ | #FFFFFF | #2E75B6 | 自動 |
| ヘッダー行（シート②） | 游ゴシック | 10 | ✅ | #FFFFFF | #2E75B6 | 20px |
| 予定セル（シート②） | - | - | - | - | #BDD7EE（薄いブルー） | - |
| 実績セル（シート②・予定内） | - | - | - | - | #FFD966（薄いオレンジ） | - |
| 実績セル（シート②・予定超過分） | - | - | - | - | #FF4C4C（レッド） | - |

### ■ 変換・抽出ロジック

| 項目名 | ロジック |
| :--- | :--- |
| 実績開始日 | `task.actual_start_date` が NULL なら `task_status_history` で `status='進行中'` の最古 `changed_at` を使用 |
| 実績終了日 | `task.actual_end_date` が NULL なら `task_status_history` で `status='完了'` の最新 `changed_at` を使用 |
| 担当者 | `task_assignee` → `user.display_name` をカンマ区切りで結合 |
| 階層番号 | `parent_task_id` をたどり、最上位から順に連番を付与（例：`1.2.3`） |
| ガントチャートX軸 | `quarter.start_date`〜`quarter.end_date` を月ごとに分割。クォーター未指定時は `project.start_date`〜`project.end_date` |
| セル塗りつぶし | 予定：`start_date`〜`end_date` の月列を `#BDD7EE` / 実績：`actual_start`〜`actual_end` の月列を `#FFD966`（`end_date` 超過分は `#FF4C4C`） |

---

## 参照テーブル

### ■ `task`

| 項目名 | カラム | データ型 |
| :--- | :--- | :--- |
| タスクID | `id` | `UUID` |
| タスク名 | `title` | `VARCHAR` |
| 親タスクID | `parent_task_id` | `UUID` |
| 予定開始日 | `start_date` | `DATE` |
| 予定終了日 | `end_date` | `DATE` |
| 実績開始日 | `actual_start_date` | `DATE` |
| 実績終了日 | `actual_end_date` | `DATE` |
| 工数（時間） | `estimated_hours` | `NUMERIC` |
| ステータス | `status` | `VARCHAR` |
| 進捗率 | `progress` | `INTEGER` |
| クォーターID | `quarter_id` | `UUID` |
| 論理削除 | `deleted_at` | `TIMESTAMP` |

### ■ `task_assignee`

| 項目名 | カラム | データ型 |
| :--- | :--- | :--- |
| タスクID | `task_id` | `UUID` |
| ユーザーID | `user_id` | `UUID` |

### ■ `task_status_history`

| 項目名 | カラム | データ型 |
| :--- | :--- | :--- |
| タスクID | `task_id` | `UUID` |
| ステータス | `status` | `VARCHAR` |
| 変更日時 | `changed_at` | `TIMESTAMP` |

### ■ `quarter`

| 項目名 | カラム | データ型 |
| :--- | :--- | :--- |
| クォーターID | `id` | `UUID` |
| クォーター名 | `title` | `VARCHAR` |
| 開始日 | `start_date` | `DATE` |
| 終了日 | `end_date` | `DATE` |

### ■ `user`

| 項目名 | カラム | データ型 |
| :--- | :--- | :--- |
| ユーザーID | `id` | `UUID` |
| 表示名 | `display_name` | `VARCHAR` |

---

## 備考

- タスクが0件の場合、シート①はヘッダー行のみ出力。シート②は「対象タスクなし」をA1セルに記載。
- ガントチャートのX軸（月数）の上限は36ヶ月とし、超過時はエラーメッセージを返す。
- ファイル名規則：`{プロジェクト名}_WBS_{出力日 YYYYMMDD}.xlsx`（クォーター指定時は `_{クォーター名}` を付与）
- openpyxl を使用して生成する。
