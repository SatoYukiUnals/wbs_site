# 【結合テスト：データ一覧】（対象：WBS・タスク管理機能）

> テスト実施前に事前作成しておく前提データを定義する。

---

## 1. 事前作成データ

### ■ `テナント`（Case 1〜）

- **Case 1**：テスト用テナント

### ■ `ユーザー`（Case 2〜）

- **Case 2**：adminユーザー
  - `role` = `admin`

- **Case 3**：memberユーザー（Case 10 の担当者）
  - `role` = `member`

### ■ `プロジェクト`（Case 5〜）

- **Case 5**：WBSテスト用プロジェクト
  - `name` = WBSテスト用プロジェクト
  - `start_date` = `2026-04-01`
  - `end_date` = `2026-12-31`
  - メンバー：Case 2（admin）、Case 3（member）

### ■ `タスク`（Case 10〜）

- **Case 10**：編集・ステータス更新テスト用タスク（階層1）
  - `title` = テストタスクA
  - `status` = 未着手
  - `progress` = 0
  - `priority` = 高
  - `project` = Case 5
  - 担当者：Case 3

- **Case 11**：Case 10 の子タスク（階層2）
  - `title` = テストタスクA-1
  - `parent_task_id` = Case 10
  - `status` = 未着手

- **Case 13**：並び替えテスト用タスク（Case 10 と同階層）
  - `title` = テストタスクB
  - `status` = 未着手
  - `project` = Case 5

- **Case 14**：削除テスト用タスク（親）
  - `title` = 削除テスト用タスク（親）
  - `project` = Case 5

- **Case 15**：Case 14 の子タスク
  - `title` = 削除テスト用タスク（子）
  - `parent_task_id` = Case 14

- **Case 16**：5層目タスク（階層上限テスト用）
  - 階層1〜5 の連続した親子タスクを作成する
  - 最下層（5層目）のタスク
  - `title` = 5層目タスク
  - `project` = Case 5
