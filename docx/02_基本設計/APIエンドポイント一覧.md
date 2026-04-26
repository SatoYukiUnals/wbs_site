# APIエンドポイント一覧

- **最終更新日**：2026-04-26
- **バージョン**：v1.1

---

## 1. URL設計方針

- ベースパス：`/api/v1/`
- テナント分離はアプリケーション層（JWT の `tenant_id`）で行い、URLにテナントIDは含めない。
- リソース名は複数形のスネークケース（例：`/projects/`）。
- 認証が必要なエンドポイントは全てヘッダーに `Authorization: Bearer {access_token}` を付与する。

---

## 2. エンドポイント一覧

### 2.1 認証・ユーザー管理（機能01）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| POST | `/auth/register/tenant/` | テナント作成＋マスターユーザー登録 | 不要 | — |
| POST | `/auth/login/` | ログイン（JWT発行） | 不要 | — |
| POST | `/auth/logout/` | ログアウト（リフレッシュトークン無効化） | 必要 | 全ユーザー |
| POST | `/auth/token/refresh/` | アクセストークン再発行 | 不要 | — |
| GET | `/auth/profile/` | 自分のプロフィール取得 | 必要 | 全ユーザー |
| PUT | `/auth/profile/` | 自分のプロフィール更新（氏名・email） | 必要 | 全ユーザー |
| GET | `/auth/users/` | テナント内ユーザー一覧 | 必要 | master |
| POST | `/auth/users/invite/` | ユーザー招待（招待メール送信） | 必要 | master |
| POST | `/auth/invitations/{token}/accept/` | 招待受諾・ユーザー登録 | 不要 | — |
| PUT | `/auth/users/{user_id}/role/` | ユーザーロール変更 | 必要 | master |
| DELETE | `/auth/users/{user_id}/` | ユーザー削除 | 必要 | master |

---

### 2.2 プロジェクト管理（機能02）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| GET | `/projects/` | プロジェクト一覧（進捗率付き） | 必要 | 全ユーザー |
| POST | `/projects/` | プロジェクト新規作成 | 必要 | admin以上 |
| GET | `/projects/{project_id}/` | プロジェクト詳細 | 必要 | メンバー以上 |
| PUT | `/projects/{project_id}/` | プロジェクト情報更新 | 必要 | admin以上 |
| DELETE | `/projects/{project_id}/` | プロジェクト論理削除 | 必要 | admin以上 |
| GET | `/projects/{project_id}/members/` | メンバー一覧 | 必要 | メンバー以上 |
| POST | `/projects/{project_id}/members/` | メンバー追加 | 必要 | admin以上 |
| PUT | `/projects/{project_id}/members/{user_id}/` | メンバーロール変更 | 必要 | admin以上 |
| DELETE | `/projects/{project_id}/members/{user_id}/` | メンバー削除 | 必要 | admin以上 |

---

### 2.3 クォーター管理（機能03）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| GET | `/projects/{project_id}/quarters/` | クォーター一覧（進捗率付き） | 必要 | メンバー以上 |
| POST | `/projects/{project_id}/quarters/` | クォーター新規作成 | 必要 | admin以上 |
| GET | `/projects/{project_id}/quarters/{quarter_id}/` | クォーター詳細 | 必要 | メンバー以上 |
| PUT | `/projects/{project_id}/quarters/{quarter_id}/` | クォーター更新 | 必要 | admin以上 |
| DELETE | `/projects/{project_id}/quarters/{quarter_id}/` | クォーター削除 | 必要 | admin以上 |

---

### 2.4 WBS・タスク管理（機能04）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| GET | `/projects/{project_id}/tasks/` | タスク一覧（ツリー構造） | 必要 | メンバー以上 |
| POST | `/projects/{project_id}/tasks/` | タスク1件作成 | 必要 | admin以上 |
| POST | `/projects/{project_id}/tasks/bulk/` | タスク複数一括作成 | 必要 | admin以上 |
| GET | `/projects/{project_id}/tasks/{task_id}/` | タスク詳細 | 必要 | メンバー以上 |
| PUT | `/projects/{project_id}/tasks/{task_id}/` | タスク全項目更新 | 必要 | admin以上 |
| PATCH | `/projects/{project_id}/tasks/{task_id}/` | タスク部分更新（ステータス・進捗率） | 必要 | 担当者 or admin以上 |
| DELETE | `/projects/{project_id}/tasks/{task_id}/` | タスク論理削除（子タスク含む） | 必要 | admin以上 |
| PATCH | `/projects/{project_id}/tasks/{task_id}/order/` | タスク並び替え（order更新） | 必要 | admin以上 |
| POST | `/projects/{project_id}/tasks/{task_id}/assignees/` | 担当者追加 | 必要 | admin以上 |
| DELETE | `/projects/{project_id}/tasks/{task_id}/assignees/{user_id}/` | 担当者削除 | 必要 | admin以上 |
| GET | `/projects/{project_id}/recent/` | 直近のタスク一覧（期限切れ・今週開始予定・着手中） | 必要 | メンバー以上 |

---

### 2.5 タスク自動割り振り（機能05）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| POST | `/projects/{project_id}/auto-assign/preview/` | 自動割り振りプレビュー生成 | 必要 | admin以上 |
| POST | `/projects/{project_id}/auto-assign/confirm/` | 自動割り振り確定・保存 | 必要 | admin以上 |
| GET | `/projects/{project_id}/auto-assign/logs/` | 自動割り振り履歴一覧 | 必要 | admin以上 |

---

### 2.6 プロダクトロードマップ（機能06）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| GET | `/projects/{project_id}/roadmap/` | ロードマップアイテム一覧 | 必要 | メンバー以上 |
| POST | `/projects/{project_id}/roadmap/` | ロードマップアイテム作成 | 必要 | admin以上 |
| PUT | `/projects/{project_id}/roadmap/{item_id}/` | ロードマップアイテム更新 | 必要 | admin以上 |
| DELETE | `/projects/{project_id}/roadmap/{item_id}/` | ロードマップアイテム削除 | 必要 | admin以上 |

---

### 2.7 ガントチャート（機能07）※WBS画面に統合

> **統合**：ガントチャートは WBS一覧画面（04-01-00）のインライン表示に統合。専用エンドポイントは廃止し、タスク一覧API（`GET /projects/{project_id}/tasks/`）のレスポンスをそのまま利用する。

---

### 2.8 進捗・ステータス管理（機能08）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| GET | `/dashboard/` | 全プロジェクトの進捗サマリー | 必要 | 全ユーザー |
| GET | `/projects/{project_id}/progress/` | プロジェクト・クォーター・タスクの進捗詳細 | 必要 | メンバー以上 |

---

### 2.9 レビュー管理（機能09）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| GET | `/projects/{project_id}/tasks/{task_id}/reviews/` | レビュー情報・コメント取得 | 必要 | メンバー以上 |
| POST | `/projects/{project_id}/tasks/{task_id}/reviews/approve/` | レビュー承認 | 必要 | 担当者以外のメンバー |
| POST | `/projects/{project_id}/tasks/{task_id}/reviews/reject/` | レビュー差し戻し（指摘コメント必須） | 必要 | 担当者以外のメンバー |
| PATCH | `/projects/{project_id}/tasks/{task_id}/reviews/{review_id}/` | レビューステータス更新・コメント編集 | 必要 | 指摘者 or 対応者 |
| GET | `/projects/{project_id}/tasks/{task_id}/reviews/history/` | レビュー操作履歴 | 必要 | メンバー以上 |

---

### 2.10 報告書管理（機能10）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| GET | `/projects/{project_id}/reports/generate/` | 対象期間のデータを集計し報告書テキストを生成（DB保存なし） | 必要 | メンバー以上 |
| POST | `/projects/{project_id}/reports/export/pdf/` | 編集済み内容をPDFに変換してダウンロード | 必要 | メンバー以上 |

---

### 2.11 WBS Excel出力（機能11）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| POST | `/projects/{project_id}/export/excel/` | WBSをExcel（.xlsx）で出力・ダウンロード | 必要 | メンバー以上 |

---

### 2.12 テンプレート管理（機能12）

| メソッド | エンドポイント | 概要 | 認証 | 権限 |
|:---:|---|---|:---:|---|
| GET | `/templates/` | テンプレート一覧（WBS・タスク） | 必要 | メンバー以上 |
| POST | `/templates/` | テンプレート新規作成 | 必要 | メンバー以上 |
| PUT | `/templates/{template_id}/` | テンプレート更新 | 必要 | 作成者 or admin以上 |
| DELETE | `/templates/{template_id}/` | テンプレート削除 | 必要 | 作成者 or admin以上 |
| POST | `/projects/{project_id}/tasks/{task_id}/apply-template/` | WBSテンプレートを適用（子タスク一括生成） | 必要 | admin以上 |

---

## 3. エンドポイント数サマリー

| 機能 | エンドポイント数 |
|---|---|
| 01 認証・ユーザー管理 | 11 |
| 02 プロジェクト管理 | 9 |
| 03 クォーター管理 | 5 |
| 04 WBS・タスク管理 | 11 |
| 05 タスク自動割り振り | 3 |
| 06 プロダクトロードマップ | 4 |
| 07 ガントチャート | 0（WBS画面に統合） |
| 08 進捗・ステータス管理 | 2 |
| 09 レビュー管理 | 5 |
| 10 報告書管理 | 2 |
| 11 WBS Excel出力 | 1 |
| 12 テンプレート管理 | 5 |
| **合計** | **58** |
