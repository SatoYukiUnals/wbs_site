# API設計規約

REST APIを設計する際の統一ルールを定める。新規API追加時・既存API修正時は本規約に従い、食い違う場合はPRでレビューを受けること。

## 1. 基本方針

- **REST原則** に則り、リソース単位でURLを設計する
- リソース操作はHTTPメソッド（GET / POST / PUT / PATCH / DELETE）で表現する
- ステートレスに設計し、リクエストごとに認証情報を送る
- **冪等性**（同じリクエストを何度送っても同じ結果）を意識する

## 2. URL設計

### ■ 基本形式

```text
/api/v{バージョン}/{リソース名}/
/api/v{バージョン}/{リソース名}/{アクション名}/
```

- **末尾は必ずスラッシュ** で終える（`/api/v1/contracts/`）
- バージョンは `v1`・`v2` の形式で含める
- リソース名は **複数形** を使う（`contracts`、`partners`）
- 複数単語は **ケバブケース** で繋ぐ（`broadcast-groups`、`partner-responsible-persons`）

### ■ パスパラメータは原則使用しない

リソース特定のIDなどは **URLパスではなくクエリパラメータ or リクエストボディで渡す** ことを標準とする。
URL構造を単純に保ち、ルーティング設計の揺れを防ぐ。

| 操作 | URL | ID等の受け渡し |
| :--- | :--- | :--- |
| 一覧取得 | `GET /api/v1/contracts/` | 検索条件はクエリ |
| 詳細取得 | `GET /api/v1/contracts/detail/?id=123` | `?id=` をクエリで |
| 新規登録 | `POST /api/v1/contracts/` | ボディで送信 |
| 更新 | `PATCH /api/v1/contracts/?id=123` | `?id=` をクエリで、更新内容はボディ |
| 削除 | `DELETE /api/v1/contracts/?id=123` | `?id=` をクエリで |
| サブリソース | `GET /api/v1/contract-items/?contract_id=123` | 親IDをクエリで |

- 例外として、パスパラメータが不可避な外部仕様（OAuth・Webhook等）がある場合は個別にレビューで合意する
- パスパラメータを使いたくなった場合は、クエリで表現できないか先に検討する

### ■ 良い例／悪い例

| 区分 | URL | 説明 |
| :--- | :--- | :--- |
| OK | `/api/v1/contracts/` | 契約一覧・契約新規作成 |
| OK | `/api/v1/contracts/?id=123` | 契約IDで特定するのはクエリで |
| OK | `/api/v1/broadcast-groups/` | 配信先グループ（ケバブケース） |
| NG | `/api/v1/contracts/123/` | **パスパラメータはNG** |
| NG | `/api/v1/contracts/123/items/` | **ネストしたパスはNG**（`/contract-items/?contract_id=123`） |
| NG | `/api/v1/getContracts/` | 動詞を含めない（HTTPメソッドで表現） |
| NG | `/api/v1/contract/` | 単数形はNG |
| NG | `/api/v1/broadcastGroups/` | キャメルケースはNG |
| NG | `/api/v1/contracts` | 末尾スラッシュなしはNG |

### ■ 特殊操作（CRUD以外）

CRUDで表現できない操作は、**アクション名をサブパスに追加** して表現する（アクション対象のIDはクエリで渡す）。

| 操作 | URL例 |
| :--- | :--- |
| 承認 | `POST /api/v1/approval-requests/approve/?id=123` |
| 却下 | `POST /api/v1/approval-requests/reject/?id=123` |
| 複製 | `POST /api/v1/contracts/duplicate/?id=123` |
| CSV出力 | `GET /api/v1/contracts/export/` |
| 一括登録 | `POST /api/v1/contracts/bulk/` |

- アクション名は **動詞の原形・ケバブケース** で記述する
- 対象リソースのIDは **クエリパラメータ** で受ける

## 3. HTTPメソッドの使い分け

| メソッド | 用途 | 冪等性 | ボディ |
| :--- | :--- | :---: | :---: |
| `GET` | 取得（一覧・詳細） | ○ | 不可 |
| `POST` | 新規作成・アクション実行 | ×（※） | 可 |
| `PUT` | 全項目を置き換える更新 | ○ | 可 |
| `PATCH` | 一部項目のみ更新 | ○ | 可 |
| `DELETE` | 削除 | ○ | 基本なし |

- ※ POSTで冪等にしたい場合は `Idempotency-Key` ヘッダで対応する
- **検索は `GET`** で行う（POSTで検索条件を受けるのは禁止）
- **更新は原則 `PATCH`**（必要な項目のみ送る）

## 4. ステータスコード

### ■ 成功系

| コード | 意味 | 使う場面 |
| :--- | :--- | :--- |
| `200 OK` | 正常終了 | 取得・更新成功（レスポンスボディあり） |
| `201 Created` | 新規作成成功 | POSTで新規リソース作成 |
| `204 No Content` | 正常終了（ボディなし） | 削除成功 |

### ■ クライアントエラー系（4xx）

| コード | 意味 | 使う場面 |
| :--- | :--- | :--- |
| `400 Bad Request` | 入力不正 | バリデーションエラー |
| `401 Unauthorized` | 未認証 | ログインが必要 |
| `403 Forbidden` | 権限不足 | ログイン済みだがアクセス不可 |
| `404 Not Found` | リソース未存在 | 対象データなし |
| `409 Conflict` | 競合 | 楽観ロック失敗・重複登録 |
| `422 Unprocessable Entity` | 処理不能 | 形式は正しいがビジネスルール違反（任意） |

### ■ サーバーエラー系（5xx）

| コード | 意味 | 使う場面 |
| :--- | :--- | :--- |
| `500 Internal Server Error` | サーバーエラー | 予期しない例外 |
| `503 Service Unavailable` | サービス停止中 | メンテナンス中 |

## 5. リクエスト

### ■ クエリパラメータ（GET）

一覧取得・検索・ページングは **URLクエリ** で受ける。

```text
GET /api/v1/contracts/?status=ordered&page=2&page_size=20&ordering=-created_at
```

- パラメータ名は **snake_case**
- ソートは `ordering` パラメータ。降順は `-` プレフィックス（例：`-created_at`）
- ページングは `page` + `page_size`

### ■ リクエストボディ（POST / PUT / PATCH）

- **JSON** で送る（`Content-Type: application/json`）
- キー名は **snake_case**
- 日時は **ISO 8601（`YYYY-MM-DDTHH:mm:ssZ`）** で送る
- `null` と `""`（空文字）を明確に区別する

```json
{
  "order_no": "ORD-2024-001",
  "customer_id": 101,
  "amount": 5000,
  "ordered_at": "2024-04-01T14:30:45+09:00"
}
```

## 6. レスポンス

### ■ 成功時のレスポンス形式

**単一リソース**：

```json
{
  "id": 123,
  "order_no": "ORD-2024-001",
  "status": "ordered",
  "created_at": "2024-04-01T14:30:45+09:00",
  "updated_at": "2024-04-01T14:30:45+09:00"
}
```

**一覧**：

```json
{
  "total_count": 57,
  "contracts": [
    { "id": 1, "order_no": "ORD-001", ... },
    { "id": 2, "order_no": "ORD-002", ... }
  ]
}
```

| キー | 型 | 必須 | 内容 |
| :--- | :--- | :---: | :--- |
| `total_count` | number | ✅ | 全件数（検索条件を満たす総レコード数） |
| `{リソース名}` | array | ✅ | 結果の配列。キー名はリソース名の複数形（`contracts`、`orders`、`partners` 等） |

- キー名は **snake_case**
- 日時は **ISO 8601** で返す
- ページングは `next` / `previous` を返さず、**クライアント側でクエリを組み立てて** 次ページを取得する
- 結果配列のキー名は **固定の `results` ではなく、各APIでリソース名の複数形** を使用する

### ■ エラー時のレスポンス形式

エラーレスポンスは **全APIで統一フォーマット** とする。

```json
{
  "code": "ERR_VAL_001",
  "message": "入力内容に不備があります。",
  "details": [
    { "field": "order_no", "message": "注文番号を入力してください。" },
    { "field": "amount", "message": "金額は0以上で入力してください。" }
  ]
}
```

| キー | 型 | 必須 | 内容 |
| :--- | :--- | :---: | :--- |
| `code` | string | ✅ | メッセージID（`エラーメッセージ仕様書` 参照） |
| `message` | string | ✅ | ユーザー向けメッセージ |
| `details` | array | - | バリデーションエラー時のフィールド単位の詳細 |

- `message` は [エラーメッセージ.md](../02_ドキュメントガイドライン/エラーメッセージ.md) の方針に従う
- フィールド単位のエラーは `details` 配列で返す

## 7. ページネーション

- **オフセット方式**（`page` + `page_size`）を基本とする
- `page_size` は **既定値 20・最大 100**
- 大量データ取得（CSV出力等）は別エンドポイントで **ストリーミング or 全件取得** を設計する

## 8. フィルタリング・ソート

- フィルタは **クエリパラメータ** で渡す（`?status=ordered&customer_id=101`）
- 複数値は **カンマ区切り** or **同一パラメータ複数指定**（プロジェクトで統一）
- ソートは `ordering` パラメータ、複数指定時はカンマ区切り
- DRFの `FilterBackend` に委ねる

## 9. 認証・認可

- 認証は **Cookie（セッション）** または **Token（Bearer）** を使用する
- 認可は **API単位** で明示する（`permission_classes` で設定）
- 認可エラーは `403 Forbidden`、未認証は `401 Unauthorized` を返す
- 他ユーザーのデータにアクセスする場合は `404 Not Found` を返すこともある（情報漏洩対策）

## 10. バージョニング

- URLに `v1` を含める方式とする（例：`/api/v1/...`）
- 破壊的変更がある場合は `v2` を新設し、しばらく併存させる
- 非破壊的変更（項目追加など）は同一バージョン内で行う

## 11. 命名規則（JSON / パラメータ）

| 対象 | 規則 | 例 |
| :--- | :--- | :--- |
| URLパス | ケバブケース・複数形 | `/broadcast-groups/` |
| クエリパラメータ | snake_case | `?order_no=ORD-001&page_size=20` |
| JSONキー | snake_case | `"order_no"` |
| ID | 数値（UUIDは別途合意） | `123` |
| 日時 | ISO 8601 | `"2024-04-01T14:30:45+09:00"` |
| 真偽値 | `true`／`false` | `"is_active": true` |
| 列挙値 | snake_case の文字列 | `"status": "ordered"` |

## 12. その他

### ■ ヘッダー

- `Content-Type: application/json` を基本とする
- ファイルアップロードは `multipart/form-data`
- レスポンスヘッダに **トレースID（`X-Request-ID`）** を付与する（ログとの突合用）

### ■ CORS

- 許可するオリジンは **明示的に設定**（ワイルドカード禁止）
- プリフライト（OPTIONS）は 204 で返す

### ■ 禁止事項

- GET で更新系の操作を行う（冪等性違反）
- POST で検索条件を受ける（キャッシュ不可・共有不可）
- エラー時に 200 OK を返す
- レスポンスに機密情報（パスワード・トークン）を含める
- エラーメッセージに技術的な詳細（スタックトレース）を含める
- URLに動詞を含める（`/getContracts/`）
- 一貫性のないキー命名（同じAPI内で `userId` と `user_id` が混在）
