# 【API設計書】テナント登録API

## 1. 概要

テナント名・email・password を受け取り、Tenant レコードと master ロールの User レコードをアトミックに作成する。成功時は JWT（アクセストークン・リフレッシュトークン）を返す。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/auth/register/tenant/`
- **認証:** 不要

## 3. リクエスト

### ボディ（JSON）

#### `tenant_name`（テナント名）

- **型:** `string` / **必須:** ✅
- 1〜100文字。他テナントと重複不可。

#### `username`（ユーザー表示名）

- **型:** `string` / **必須:** ✅
- 1〜100文字。

#### `email`（メールアドレス）

- **型:** `string` / **必須:** ✅
- RFC5322 形式。同テナント内で重複不可（新規テナントのため実質ユニーク）。

#### `password`（パスワード）

- **型:** `string` / **必須:** ✅
- 8文字以上。

```json
{
  "tenant_name": "株式会社サンプル",
  "username": "山田太郎",
  "email": "yamada@example.com",
  "password": "password123"
}
```

## 4. レスポンス

### 成功 (201 Created)

```json
{
  "access": "<JWT access token>",
  "refresh": "<JWT refresh token>",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "role": "master"
}
```

### エラー (4xx / 5xx)

| 状況 | ステータス | メッセージ内容 |
|---|---|---|
| テナント名重複 | 400 | テナント名は既に使用されています |
| email 形式不正 | 400 | 正しいメールアドレスを入力してください |
| パスワード8文字未満 | 400 | パスワードは8文字以上で設定してください |
| DBエラー | 500 | システムエラーが発生しました |

## 5. 内部処理 / ロジック

1. **バリデーション**
   - `tenant_name` 重複チェック（`tenant` テーブル SELECT）
   - `email` 形式チェック
   - `password` 8文字以上チェック
   - エラー時：400 を返す
2. **DB操作（トランザクション）**
   - `tenant` レコードを INSERT
   - `user` レコードを `role=master` で INSERT（`tenant_id` を付与）
   - どちらかが失敗した場合ロールバックし 500 を返す
3. **JWT発行**
   - simplejwt で `access` / `refresh` トークンを生成
   - ペイロードに `tenant_id`・`user_id`・`role` を含める
4. **レスポンス**
   - 201 Created でトークン・tenant_id・user_id・role を返す
