# 【結合テスト：データ一覧】（対象：WBS Excel出力機能）

---

## 1. 事前作成データ

### ■ `テナント`（Case 1〜）

- **Case 1**：テスト用テナント

### ■ `ユーザー`（Case 2〜）

- **Case 2**：adminユーザー（`role` = `admin`）
- **Case 3**：memberユーザー（担当者として使用）

### ■ `プロジェクト`（Case 5〜）

- **Case 5**：Excel出力テスト用プロジェクト
  - `name` = Excelテスト用プロジェクト
  - `start_date` = `2026-01-01`、`end_date` = `2026-06-30`

### ■ `クォーター`（Case 8〜）

- **Case 8**：Q1（`start_date` = `2026-01-01`、`end_date` = `2026-03-31`）
- **Case 9**：Q2（`start_date` = `2026-04-01`、`end_date` = `2026-06-30`）

### ■ `タスク`（Case 10〜）

- **Case 10**：Q1タスク（実績日あり）
  - `title` = Q1タスクA
  - `quarter` = Case 8
  - `start_date` = `2026-01-01`、`end_date` = `2026-01-31`
  - `actual_start_date` = `2026-01-05`、`actual_end_date` = `2026-02-03`
  - 担当者：Case 3

- **Case 11**：Q1タスク（actual未入力・StatusHistoryで補完）
  - `title` = Q1タスクB
  - `quarter` = Case 8
  - `start_date` = `2026-02-01`、`end_date` = `2026-02-28`
  - `actual_start_date` = NULL、`actual_end_date` = NULL
  - StatusHistory：`status=進行中` の changed_at = `2026-02-05`、`status=完了` の changed_at = `2026-03-02`

- **Case 12**：Q2タスク
  - `title` = Q2タスクA
  - `quarter` = Case 9
  - `start_date` = `2026-04-01`、`end_date` = `2026-04-30`
