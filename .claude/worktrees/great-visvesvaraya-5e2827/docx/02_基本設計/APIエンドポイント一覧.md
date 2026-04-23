# APIエンドポイント一覧

**作成日：** 2026年4月12日  
**バージョン：** 1.0  
**ベースURL：** `/api/v1`

---

## 認証・ユーザー管理

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| POST | /auth/register/tenant/ | テナント作成＋マスターユーザー登録 | 不要 |
| POST | /auth/login/ | ログイン | 不要 |
| POST | /auth/logout/ | ログアウト | 全ユーザー |
| POST | /auth/token/refresh/ | トークンリフレッシュ | 不要 |
| GET | /auth/profile/ | プロフィール取得 | 全ユーザー |
| PUT | /auth/profile/ | プロフィール更新 | 全ユーザー |
| GET | /auth/users/ | テナント内ユーザー一覧 | マスターユーザー |
| POST | /auth/users/ | ユーザー作成 | マスターユーザー |
| PUT | /auth/users/{user_id}/ | ユーザー情報・ロール変更 | マスターユーザー |
| DELETE | /auth/users/{user_id}/ | ユーザー削除 | マスターユーザー |

---

## プロジェクト管理

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /projects/ | プロジェクト一覧 | 全ユーザー |
| POST | /projects/ | プロジェクト作成 | admin以上 |
| GET | /projects/{project_id}/ | プロジェクト詳細 | メンバー以上 |
| PUT | /projects/{project_id}/ | プロジェクト編集 | admin以上 |
| DELETE | /projects/{project_id}/ | プロジェクト削除（論理削除） | admin以上 |
| GET | /projects/{project_id}/members/ | メンバー一覧 | メンバー以上 |
| POST | /projects/{project_id}/members/ | メンバー追加 | admin以上 |
| PUT | /projects/{project_id}/members/{user_id}/ | メンバーロール変更 | admin以上 |
| DELETE | /projects/{project_id}/members/{user_id}/ | メンバー削除 | admin以上 |

---

## クォーター管理

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /projects/{project_id}/quarters/ | クォーター一覧 | メンバー以上 |
| POST | /projects/{project_id}/quarters/ | クォーター作成 | admin以上 |
| GET | /projects/{project_id}/quarters/{quarter_id}/ | クォーター詳細 | メンバー以上 |
| PUT | /projects/{project_id}/quarters/{quarter_id}/ | クォーター編集 | admin以上 |
| DELETE | /projects/{project_id}/quarters/{quarter_id}/ | クォーター削除 | admin以上 |

---

## WBS・タスク管理

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /projects/{project_id}/tasks/ | タスク一覧（ツリー構造・フィルター対応） | メンバー以上 |
| POST | /projects/{project_id}/tasks/ | タスク作成 | admin以上 |
| POST | /projects/{project_id}/tasks/bulk/ | タスク一括作成 | admin以上 |
| GET | /projects/{project_id}/tasks/{task_id}/ | タスク詳細 | メンバー以上 |
| PUT | /projects/{project_id}/tasks/{task_id}/ | タスク全項目編集 | admin以上 |
| PATCH | /projects/{project_id}/tasks/{task_id}/ | タスク部分編集（ステータス・進捗率・実績日） | メンバー以上（担当タスクのみ） |
| DELETE | /projects/{project_id}/tasks/{task_id}/ | タスク削除（子タスク含む論理削除） | admin以上 |
| PATCH | /projects/{project_id}/tasks/{task_id}/order/ | タスク並び替え | admin以上 |
| GET | /projects/{project_id}/tasks/{task_id}/assignees/ | 担当者一覧 | メンバー以上 |
| POST | /projects/{project_id}/tasks/{task_id}/assignees/ | 担当者追加 | admin以上 |
| DELETE | /projects/{project_id}/tasks/{task_id}/assignees/{user_id}/ | 担当者削除 | admin以上 |
| POST | /projects/{project_id}/tasks/{task_id}/apply-template/ | WBSテンプレート適用 | admin以上 |

---

## タスク自動割り振り

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| POST | /projects/{project_id}/auto-assign/preview/ | 自動割り振りプレビュー生成 | admin以上 |
| POST | /projects/{project_id}/auto-assign/confirm/ | 割り振り結果の確定 | admin以上 |
| GET | /projects/{project_id}/auto-assign/logs/ | 割り振り履歴一覧 | admin以上 |
| GET | /projects/{project_id}/auto-assign/logs/{log_id}/ | 割り振り履歴詳細 | admin以上 |

---

## ガントチャート

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /projects/{project_id}/gantt/ | ガントチャート用データ取得（クォーター＋タスク） | メンバー以上 |

---

## プロダクトロードマップ

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /projects/{project_id}/roadmap/ | ロードマップ取得（クォーター＋アイテム） | メンバー以上 |
| POST | /projects/{project_id}/roadmap/ | アイテム作成 | admin以上 |
| GET | /projects/{project_id}/roadmap/{item_id}/ | アイテム詳細 | メンバー以上 |
| PUT | /projects/{project_id}/roadmap/{item_id}/ | アイテム編集 | admin以上 |
| DELETE | /projects/{project_id}/roadmap/{item_id}/ | アイテム削除 | admin以上 |

---

## ダッシュボード・進捗管理

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /dashboard/ | 全プロジェクトサマリー | 全ユーザー |
| GET | /projects/{project_id}/dashboard/ | プロジェクト別ダッシュボード | メンバー以上 |

---

## レビュー管理

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /projects/{project_id}/reviews/ | レビュー一覧（プロジェクト内） | メンバー以上 |
| GET | /projects/{project_id}/tasks/{task_id}/reviews/ | タスクのレビュー情報取得 | メンバー以上 |
| POST | /projects/{project_id}/tasks/{task_id}/reviews/approve/ | 承認 | メンバー以上（担当者以外） |
| POST | /projects/{project_id}/tasks/{task_id}/reviews/reject/ | 差し戻し（複数指摘コメント） | メンバー以上（担当者以外） |
| PATCH | /projects/{project_id}/tasks/{task_id}/reviews/{review_id}/ | レビューステータス更新・コメント編集 | 指摘者 or 対応者（完了は不可） |
| GET | /projects/{project_id}/tasks/{task_id}/reviews/history/ | レビュー履歴 | メンバー以上 |

---

## 報告書管理

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /projects/{project_id}/reports/generate/ | 報告書内容の自動生成（DB保存なし） | メンバー以上 |
| POST | /projects/{project_id}/reports/export/pdf/ | 編集済み内容からPDF出力 | メンバー以上 |

---

## Excel出力

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /projects/{project_id}/export/excel/ | WBS全体のExcel出力（2シート） | 全ユーザー |
| GET | /projects/{project_id}/export/excel/?quarter_id={id} | クォーター単位のExcel出力 | 全ユーザー |

---

## テンプレート管理

| メソッド | エンドポイント | 説明 | 権限 |
|---------|--------------|------|------|
| GET | /templates/ | テンプレート一覧（個人＋共有） | 全ユーザー |
| POST | /templates/ | テンプレート作成 | 全ユーザー（共有はadmin以上） |
| GET | /templates/{template_id}/ | テンプレート詳細 | 全ユーザー |
| PUT | /templates/{template_id}/ | テンプレート編集 | 作成者 or admin以上 |
| DELETE | /templates/{template_id}/ | テンプレート削除 | 作成者 or admin以上 |

---

## エンドポイント数サマリー

| カテゴリ | エンドポイント数 |
|---------|--------------|
| 認証・ユーザー管理 | 10 |
| プロジェクト管理 | 9 |
| クォーター管理 | 5 |
| WBS・タスク管理 | 12 |
| タスク自動割り振り | 4 |
| ガントチャート | 1 |
| プロダクトロードマップ | 5 |
| ダッシュボード・進捗管理 | 2 |
| レビュー管理 | 6 |
| 報告書管理 | 2 |
| Excel出力 | 2 |
| テンプレート管理 | 5 |
| **合計** | **63** |

---

## 共通仕様

| 項目 | 内容 |
|------|------|
| 認証方式 | JWT Bearer Token（Authorizationヘッダー） |
| レスポンス形式 | JSON |
| 日付形式 | ISO 8601（YYYY-MM-DD） |
| 日時形式 | ISO 8601（YYYY-MM-DDTHH:mm:ssZ） |
| ページネーション | ?page=1&page_size=20 |
| フィルタリング | クエリパラメータ（?status=進行中&assignee={user_id}&quarter_id={id}） |
| エラーレスポンス | {error: "メッセージ", code: "エラーコード"} |

### HTTPステータスコード

| コード | 意味 |
|--------|------|
| 200 | OK |
| 201 | Created |
| 204 | No Content（削除成功） |
| 400 | Bad Request（バリデーションエラー） |
| 401 | Unauthorized（未認証） |
| 403 | Forbidden（権限不足） |
| 404 | Not Found |
| 500 | Internal Server Error |
