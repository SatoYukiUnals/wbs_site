# 【総合テスト：シナリオ】SCN-05 権限制御・テナント分離

## 1. シナリオ概要

- **目的**：ロール別のアクセス制御と、テナント間のデータ分離が全操作を通じて徹底されていることを検証する。
- **前提条件**：テナントA（master・admin・member各1名、プロジェクト1件）、テナントB（master1名、プロジェクト1件）が存在する。
- **実行ユーザー**：ロールを切り替えながら検証する。

---

## 2. テストシナリオ

### Step 1：memberユーザーの操作制限

| 操作 | エンドポイント | 期待結果 |
| :--- | :--- | :--- |
| プロジェクト作成 | `POST /api/v1/projects/` | `403 Forbidden` |
| プロジェクト編集 | `PUT /api/v1/projects/1/` | `403 Forbidden` |
| プロジェクト削除 | `DELETE /api/v1/projects/1/` | `403 Forbidden` |
| タスク作成 | `POST /api/v1/projects/1/tasks/` | `403 Forbidden` |
| タスク削除 | `DELETE /api/v1/projects/1/tasks/1/` | `403 Forbidden` |
| ユーザー作成 | `POST /api/v1/auth/users/` | `403 Forbidden` |
| タスク進捗更新（担当者） | `PATCH /api/v1/projects/1/tasks/2/` | `200 OK`（許可） |

---

### Step 2：adminユーザーの操作制限

| 操作 | エンドポイント | 期待結果 |
| :--- | :--- | :--- |
| プロジェクト作成 | `POST /api/v1/projects/` | `201 Created`（許可） |
| タスク作成・編集・削除 | 各エンドポイント | `200/201/204`（許可） |
| ユーザー作成 | `POST /api/v1/auth/users/` | `403 Forbidden` |
| ユーザー削除 | `DELETE /api/v1/auth/users/{id}/` | `403 Forbidden` |

---

### Step 3：テナントBのプロジェクトIDへのアクセス

- **操作**：テナントAのadminユーザーで、テナントBのプロジェクトIDを各エンドポイントに指定する。
- **確認**：
  - [ ] `GET /api/v1/projects/{テナントBのproject_id}/` → `404 Not Found`。
  - [ ] `GET /api/v1/projects/{テナントBのproject_id}/tasks/` → `404 Not Found`。
  - [ ] `DELETE /api/v1/projects/{テナントBのproject_id}/` → `404 Not Found`。
  - [ ] テナントBのデータがいかなる一覧APIにも表示されない。

---

### Step 4：期限切れJWTでのアクセス

- **操作**：アクセストークン有効期限（15分）後に、同トークンでAPIアクセスを試みる。
- **確認**：
  - [ ] `401 Unauthorized` / `ERR_AUTH_002` が返却される。

---

### Step 5：リフレッシュトークンによるトークン更新

- **操作**：`POST /api/v1/auth/token/refresh/` にリフレッシュトークンを送信する。
- **確認**：
  - [ ] 新しいアクセストークンが返却される。
  - [ ] 新しいアクセストークンで通常のAPIアクセスが成功する。

---

### Step 6：ブラウザ動作確認（Chrome最新版）

| 画面 | 確認事項 |
| :--- | :--- |
| ログイン画面 | フォームのバリデーションエラーが表示される |
| WBS一覧画面 | タスクのドラッグ＆ドロップ並び替えが動作する |
| ガントチャート画面 | Canvas/SVGのガントバーが正常描画される |
| Excel出力 | ダウンロードダイアログが表示される |
| PDF出力 | ダウンロードダイアログが表示される |

---

## 3. 備考

- Step3のテナント分離テストは、意図的に他テナントIDを指定したリクエストを発行して検証する。
- Step4は `settings.py` の `ACCESS_TOKEN_LIFETIME` を短縮した環境で実施するか、JWT署名を検証する。
