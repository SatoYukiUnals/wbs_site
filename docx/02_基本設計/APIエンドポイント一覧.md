# APIエンドポイント一覧

WBS管理ソフトの REST API エンドポイントを一覧化する。URL 構造・HTTP メソッド・認可は [API設計規約](../00_ルール/04_開発規約/03_API設計規約.md) に従う。

- **作成日**：2026-04-23
- **バージョン**：1.0
- **API ベース**：`/api/v1/`
- **認証**：JWT Bearer Token（`Authorization: Bearer <access_token>`）
- **エンドポイント総数**：77

---

## 1. 設計方針（規約の再掲）

- URL は **リソース複数形・ケバブケース・末尾スラッシュ** とする（例：`/api/v1/auto-assign-logs/`）
- **パスパラメータは使わず**、特定 ID はクエリ `?id=123`、サブリソース絞り込みは `?parent_id=123`
- 詳細取得は `GET /api/v1/{resource}/detail/?id=X`
- 特殊アクションはサブパス `/action/?id=X` 形式
- 一覧レスポンスは `{ total_count, <resource_plural>: [...] }` 形式
- 全エンドポイントで JSON（ファイルダウンロードを除く）
- エラーレスポンスは `{ code, message, details? }` の統一形式

---

## 2. カテゴリ別件数

| # | カテゴリ | 件数 |
|---|---------|:---:|
| 01 | 認証・ユーザー管理 | 11 |
| 02 | プロジェクト管理 | 9 |
| 03 | クォーター管理 | 5 |
| 04 | WBS・タスク管理 | 12 |
| 05 | 自動割り振り | 5 |
| 06 | ガントチャート | 1 |
| 07 | ロードマップ | 5 |
| 08 | ダッシュボード | 2 |
| 09 | レビュー管理 | 7 |
| 10 | 報告書管理 | 9 |
| 11 | Excel 出力 | 1 |
| 12 | テンプレート管理 | 10 |
| **合計** |  | **77** |

---

## 3. エンドポイント一覧

### 3.1 認証・ユーザー管理

| # | メソッド | URL | 認証 | 認可 | 概要 |
|---|:--------:|-----|:----:|------|------|
| 1 | POST | `/api/v1/tenants/register/` | 不要 | ー | テナント登録 + 初期 master ユーザー作成 |
| 2 | POST | `/api/v1/auth/login/` | 不要 | ー | ユーザー名/メール・パスワードでログイン、JWT 発行 |
| 3 | POST | `/api/v1/auth/logout/` | 必要 | 全員 | リフレッシュトークン失効 |
| 4 | POST | `/api/v1/auth/token-refresh/` | 不要※ | ー | リフレッシュトークンで新しいアクセストークン発行 |
| 5 | GET | `/api/v1/auth/profile/` | 必要 | 全員 | 自身のプロフィール取得 |
| 6 | PATCH | `/api/v1/auth/profile/` | 必要 | 全員 | 自身のプロフィール（氏名・メール・パスワード）更新 |
| 7 | GET | `/api/v1/users/` | 必要 | master, admin | テナント内ユーザー一覧 |
| 8 | GET | `/api/v1/users/detail/?id=X` | 必要 | master, admin | ユーザー詳細 |
| 9 | POST | `/api/v1/users/` | 必要 | master, admin | ユーザー新規登録 |
| 10 | PATCH | `/api/v1/users/?id=X` | 必要 | master, admin | ユーザー情報更新（ロール変更含む） |
| 11 | DELETE | `/api/v1/users/?id=X` | 必要 | master, admin | ユーザー削除（論理削除） |

※ `token-refresh` は Bearer ではなく、リフレッシュトークンをリクエストボディで受け取る。

### 3.2 プロジェクト管理

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 12 | GET | `/api/v1/projects/` | 全員（自身が参加するもの） | プロジェクト一覧 |
| 13 | GET | `/api/v1/projects/detail/?id=X` | プロジェクトメンバー | プロジェクト詳細 |
| 14 | POST | `/api/v1/projects/` | master, admin | プロジェクト新規作成 |
| 15 | PATCH | `/api/v1/projects/?id=X` | master, プロジェクト admin | プロジェクト更新 |
| 16 | DELETE | `/api/v1/projects/?id=X` | master, プロジェクト admin | プロジェクト削除 |
| 17 | GET | `/api/v1/project-members/?project_id=X` | プロジェクトメンバー | メンバー一覧 |
| 18 | POST | `/api/v1/project-members/` | master, プロジェクト admin | メンバー追加 |
| 19 | PATCH | `/api/v1/project-members/?id=X` | master, プロジェクト admin | メンバーロール変更 |
| 20 | DELETE | `/api/v1/project-members/?id=X` | master, プロジェクト admin | メンバー削除 |

### 3.3 クォーター管理

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 21 | GET | `/api/v1/quarters/?project_id=X` | プロジェクトメンバー | クォーター一覧 |
| 22 | GET | `/api/v1/quarters/detail/?id=X` | プロジェクトメンバー | クォーター詳細 |
| 23 | POST | `/api/v1/quarters/` | master, プロジェクト admin | クォーター作成 |
| 24 | PATCH | `/api/v1/quarters/?id=X` | master, プロジェクト admin | クォーター更新 |
| 25 | DELETE | `/api/v1/quarters/?id=X` | master, プロジェクト admin | クォーター削除 |

### 3.4 WBS・タスク管理

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 26 | GET | `/api/v1/tasks/?project_id=X` | プロジェクトメンバー | タスク一覧（階層構造で返却） |
| 27 | GET | `/api/v1/tasks/detail/?id=X` | プロジェクトメンバー | タスク詳細（担当者・ステータス履歴・レビュー含む） |
| 28 | POST | `/api/v1/tasks/` | プロジェクトメンバー | タスク新規作成 |
| 29 | PATCH | `/api/v1/tasks/?id=X` | プロジェクトメンバー | タスク更新（部分更新） |
| 30 | DELETE | `/api/v1/tasks/?id=X` | プロジェクトメンバー | タスク削除（子タスクも論理削除） |
| 31 | POST | `/api/v1/tasks/bulk/` | プロジェクトメンバー | タスク一括作成（改行区切り／テンプレート適用） |
| 32 | PATCH | `/api/v1/tasks/reorder/` | プロジェクトメンバー | 並び順・親変更（ドラッグ&ドロップ） |
| 33 | POST | `/api/v1/tasks/apply-template/?id=X` | プロジェクトメンバー | 指定タスクの配下に WBS テンプレートを適用 |
| 34 | GET | `/api/v1/task-assignees/?task_id=X` | プロジェクトメンバー | タスク担当者一覧 |
| 35 | POST | `/api/v1/task-assignees/` | プロジェクトメンバー | タスクに担当者を追加 |
| 36 | DELETE | `/api/v1/task-assignees/?id=X` | プロジェクトメンバー | タスク担当者を削除 |
| 37 | GET | `/api/v1/task-status-history/?task_id=X` | プロジェクトメンバー | タスクのステータス変更履歴 |

### 3.5 自動割り振り

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 38 | POST | `/api/v1/auto-assign/preview/` | master, プロジェクト admin | 割り振り結果をプレビュー生成（preview ログ作成） |
| 39 | POST | `/api/v1/auto-assign/confirm/?id=X` | master, プロジェクト admin | プレビュー結果を確定して task_assignee へ反映 |
| 40 | POST | `/api/v1/auto-assign/cancel/?id=X` | master, プロジェクト admin | プレビューをキャンセル |
| 41 | GET | `/api/v1/auto-assign-logs/?project_id=X` | master, プロジェクト admin | 自動割り振り履歴 |
| 42 | GET | `/api/v1/auto-assign-logs/detail/?id=X` | master, プロジェクト admin | 自動割り振り履歴の詳細 |

### 3.6 ガントチャート

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 43 | GET | `/api/v1/gantt/?project_id=X&from=YYYY-MM-DD&to=YYYY-MM-DD` | プロジェクトメンバー | ガント表示用データ（タスク・クォーター区切り含む） |

### 3.7 プロダクトロードマップ

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 44 | GET | `/api/v1/roadmap-items/?project_id=X` | プロジェクトメンバー | ロードマップアイテム一覧 |
| 45 | GET | `/api/v1/roadmap-items/detail/?id=X` | プロジェクトメンバー | アイテム詳細 |
| 46 | POST | `/api/v1/roadmap-items/` | master, プロジェクト admin | アイテム作成 |
| 47 | PATCH | `/api/v1/roadmap-items/?id=X` | master, プロジェクト admin | アイテム更新 |
| 48 | DELETE | `/api/v1/roadmap-items/?id=X` | master, プロジェクト admin | アイテム削除 |

### 3.8 ダッシュボード

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 49 | GET | `/api/v1/dashboard/` | 全員 | 全プロジェクト横断の進捗サマリ |
| 50 | GET | `/api/v1/dashboard/project/?project_id=X` | プロジェクトメンバー | プロジェクト別のダッシュボード（担当者別・ステータス別集計） |

### 3.9 レビュー管理

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 51 | GET | `/api/v1/reviews/?project_id=X&status=pending` | プロジェクトメンバー | レビュー一覧（プロジェクト単位） |
| 52 | GET | `/api/v1/reviews/?task_id=X` | プロジェクトメンバー | タスクに紐づくレビュー一覧 |
| 53 | POST | `/api/v1/reviews/` | プロジェクトメンバー | レビュー依頼作成（タスクを `review` ステータスに遷移） |
| 54 | POST | `/api/v1/reviews/approve/?id=X` | 担当者本人以外のプロジェクトメンバー | レビュー承認（タスクを `done` に遷移） |
| 55 | POST | `/api/v1/reviews/reject/?id=X` | 担当者本人以外のプロジェクトメンバー | レビュー差し戻し（タスクを `in_progress` に戻す） |
| 56 | PATCH | `/api/v1/reviews/?id=X` | レビュー実施者本人 | レビューコメント編集 |
| 57 | GET | `/api/v1/review-history/?task_id=X` | プロジェクトメンバー | レビュー履歴（依頼・承認・差し戻し・コメント） |

### 3.10 報告書管理

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 58 | GET | `/api/v1/reports/?project_id=X` | プロジェクトメンバー | 報告書一覧 |
| 59 | GET | `/api/v1/reports/detail/?id=X` | プロジェクトメンバー | 報告書詳細（プレビュー用データ） |
| 60 | POST | `/api/v1/reports/generate/` | master, プロジェクト admin | 期間指定で報告書を生成 |
| 61 | DELETE | `/api/v1/reports/?id=X` | master, プロジェクト admin | 報告書削除 |
| 62 | GET | `/api/v1/reports/export-pdf/?id=X` | プロジェクトメンバー | 報告書 PDF ダウンロード |
| 63 | GET | `/api/v1/report-schedules/?project_id=X` | プロジェクトメンバー | 定期レポートスケジュール一覧 |
| 64 | POST | `/api/v1/report-schedules/` | master, プロジェクト admin | 定期レポートスケジュール作成 |
| 65 | PATCH | `/api/v1/report-schedules/?id=X` | master, プロジェクト admin | スケジュール更新 |
| 66 | DELETE | `/api/v1/report-schedules/?id=X` | master, プロジェクト admin | スケジュール削除 |

### 3.11 WBS Excel 出力

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 67 | GET | `/api/v1/wbs-export/?project_id=X&quarter_id=Y` | プロジェクトメンバー | WBS を .xlsx でダウンロード |

### 3.12 テンプレート管理

| # | メソッド | URL | 認可 | 概要 |
|---|:--------:|-----|------|------|
| 68 | GET | `/api/v1/wbs-templates/` | 全員 | WBS テンプレート一覧 |
| 69 | GET | `/api/v1/wbs-templates/detail/?id=X` | 全員（共有化未のものは作成者のみ） | WBS テンプレート詳細 |
| 70 | POST | `/api/v1/wbs-templates/` | 全員 | WBS テンプレート作成 |
| 71 | PATCH | `/api/v1/wbs-templates/?id=X` | 作成者 or master, admin | WBS テンプレート更新 |
| 72 | DELETE | `/api/v1/wbs-templates/?id=X` | 作成者 or master, admin | WBS テンプレート削除 |
| 73 | GET | `/api/v1/task-templates/` | 全員 | タスクテンプレート一覧 |
| 74 | GET | `/api/v1/task-templates/detail/?id=X` | 全員（共有化未のものは作成者のみ） | タスクテンプレート詳細 |
| 75 | POST | `/api/v1/task-templates/` | 全員 | タスクテンプレート作成 |
| 76 | PATCH | `/api/v1/task-templates/?id=X` | 作成者 or master, admin | タスクテンプレート更新 |
| 77 | DELETE | `/api/v1/task-templates/?id=X` | 作成者 or master, admin | タスクテンプレート削除 |

---

## 4. 共通レスポンス

### 4.1 成功時

**単一リソース**：

```json
{
  "id": 123,
  "name": "プロジェクトA",
  "created_at": "2026-04-23T09:00:00+09:00"
}
```

**一覧**：

```json
{
  "total_count": 57,
  "projects": [
    { "id": 1, "name": "..." },
    { "id": 2, "name": "..." }
  ]
}
```

一覧の配列キーはリソース名の複数形（`projects`、`tasks`、`users` 等）。

### 4.2 エラー時

全エンドポイントで統一形式。

```json
{
  "code": "ERR_VAL_001",
  "message": "入力内容に不備があります。",
  "details": [
    { "field": "name", "message": "プロジェクト名は必須です。" }
  ]
}
```

---

## 5. 共通クエリパラメータ

| パラメータ | 型 | 既定 | 最大 | 内容 |
|-----------|----|------|------|------|
| `page` | number | 1 | - | ページ番号（1始まり） |
| `page_size` | number | 20 | 100 | 1ページあたり件数 |
| `ordering` | string | ー | - | ソート（降順は `-` プレフィックス。例：`-created_at`） |
| `search` | string | ー | - | 検索ワード（対象カラムは各 API 個別） |

---

## 6. 認可マトリクス（ロール × API 分類）

| API 分類 | master | admin | member |
|---------|:------:|:-----:|:------:|
| テナント登録・ログイン | - | - | - |
| プロフィール（自分） | ✅ | ✅ | ✅ |
| ユーザー管理（他者） | ✅ | ✅ | ❌ |
| プロジェクト CRUD | ✅ | ✅※ | ❌※ |
| プロジェクトメンバー管理 | ✅ | ✅※ | ❌ |
| クォーター CRUD | ✅ | ✅※ | ❌ |
| タスク CRUD | ✅ | ✅※ | ✅※ |
| 自動割り振り実行 | ✅ | ✅※ | ❌ |
| ガント閲覧 | ✅ | ✅※ | ✅※ |
| ロードマップ CRUD | ✅（編集） | ✅※（編集） | ✅※（閲覧のみ） |
| レビュー実施 | ✅※ | ✅※ | ✅※ |
| 報告書作成 | ✅ | ✅※ | ❌ |
| 報告書閲覧 | ✅ | ✅ | ✅※ |
| Excel 出力 | ✅ | ✅ | ✅※ |
| テンプレート共有化 | ✅ | ✅ | ❌ |
| テンプレート自作 | ✅ | ✅ | ✅ |

※ プロジェクト参加必須（`project_member` レコード存在）

---

## 7. 改版履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 1.0 | 2026-04-23 | 初版作成（77エンドポイント・API設計規約準拠） |
