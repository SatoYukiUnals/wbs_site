# 【API設計書】ログインAPI

## 1. 概要

email・password を受け取り認証を行う。成功時は JWT（アクセストークン・リフレッシュトークン）とユーザー情報を返す。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/auth/login/`
- **認証:** 不要

## 3. リクエスト

### ボディ（JSON）

#### `email`

- **型:** `string` / **必須:** ✅

#### `password`

- **型:** `string` / **必須:** ✅

```json
{
  "email": "yamada@example.com",
  "password": "password123"
}
```

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "access": "<JWT access token>",
  "refresh": "<JWT refresh token>",
  "user_id": "uuid",
  "username": "山田太郎",
  "role": "master",
  "tenant_id": "uuid"
}
```

### エラー (4xx)

| 状況 | ステータス | メッセージ内容 |
|---|---|---|
| email / password 不一致 | 401 | メールアドレスまたはパスワードが正しくありません |
| 必須項目未入力 | 400 | 入力内容に不備があります |

## 5. 内部処理 / ロジック

1. **バリデーション**
   - `email`・`password` 必須チェック。エラー時：400 を返す
2. **認証**
   - `user` テーブルから `email` で検索（`deleted_at IS NULL`）
   - パスワードハッシュ照合
   - 不一致・未登録：401 を返す
3. **JWT発行**
   - simplejwt で `access` / `refresh` トークンを生成
   - ペイロードに `tenant_id`・`user_id`・`role` を含める
4. **レスポンス**
   - 200 OK でトークン・ユーザー情報を返す
