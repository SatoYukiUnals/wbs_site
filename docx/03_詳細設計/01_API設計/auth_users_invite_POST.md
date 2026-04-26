# 【API設計書】ユーザー招待API

## 1. 概要

email・ロールを指定して招待トークンを生成し、招待メールを送信する。master のみ実行可能。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/auth/users/invite/`
- **認証:** 必要（Bearer トークン）
- **権限:** master のみ

## 3. リクエスト

### ボディ（JSON）

#### `email`

- **型:** `string` / **必須:** ✅
- RFC5322 形式。同テナント内に未登録であること

#### `role`

- **型:** `string` / **必須:** ✅
- `admin` または `member`

```json
{
  "email": "tanaka@example.com",
  "role": "member"
}
```

## 4. レスポンス

### 成功 (201 Created)

```json
{
  "invitation_id": "uuid",
  "email": "tanaka@example.com",
  "role": "member"
}
```

### エラー (4xx)

| 状況 | ステータス | メッセージ内容 |
|---|---|---|
| email 既登録 | 409 | このメールアドレスは既に登録されています |
| ロール値不正 | 400 | 入力内容に不備があります |
| 権限不足 | 403 | この操作を行う権限がありません |
| 認証なし | 401 | 認証情報がありません |

## 5. 内部処理 / ロジック

1. **権限チェック**
   - `role=master` のみ実行可。それ以外：403 を返す
2. **バリデーション**
   - `email` 形式・同テナント内重複チェック。重複：409 を返す
   - `role` が `admin` または `member` か確認
3. **招待レコード作成**
   - ランダムトークンを生成し `invitation` テーブルに INSERT
   - 有効期限：72時間後
4. **メール送信**
   - 招待URLを本文に含むメールを送信（URL: `/invite/accept/?token={token}`）
5. **レスポンス**
   - 招待情報を返す
