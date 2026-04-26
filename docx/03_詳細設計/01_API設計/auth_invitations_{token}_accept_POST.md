# 【API設計書】招待受諾API

## 1. 概要

招待トークンを検証し、新規ユーザーを作成してテナントに登録する。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/auth/invitations/{token}/accept/`
- **認証:** 不要

## 3. リクエスト

### パスパラメータ

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `token` | string | ✅ | 招待トークン |

### ボディ（JSON）

#### `username`

- **型:** `string` / **必須:** ✅
- 1〜100文字

#### `password`

- **型:** `string` / **必須:** ✅
- 8文字以上

```json
{
  "username": "田中花子",
  "password": "password123"
}
```

## 4. レスポンス

### 成功 (201 Created)

```json
{
  "access": "<JWT access token>",
  "refresh": "<JWT refresh token>",
  "user_id": "uuid",
  "role": "member",
  "tenant_id": "uuid"
}
```

### エラー (4xx)

| 状況 | ステータス | メッセージ内容 |
|---|---|---|
| トークン無効・存在しない | 404 | 招待リンクが無効です |
| トークン期限切れ | 400 | 招待リンクの有効期限が切れています |
| パスワード8文字未満 | 400 | パスワードは8文字以上で設定してください |

## 5. 内部処理 / ロジック

1. **トークン検証**
   - `invitation` テーブルからトークンを検索
   - 存在しない：404 を返す
   - `expires_at` が過去：400 を返す
2. **バリデーション**
   - `password` 8文字以上チェック
3. **ユーザー作成**
   - `invitation.email`・`invitation.role`・`invitation.tenant_id` で `user` レコードを INSERT
4. **招待レコード削除**
   - 使用済み `invitation` レコードを DELETE
5. **JWT発行・レスポンス**
   - ログイン済み状態で JWT を返す
