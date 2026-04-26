# 【API設計書】プロフィール取得API

## 1. 概要

ログイン中のユーザー自身のプロフィール情報を取得する。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/auth/profile/`
- **認証:** 必要（Bearer トークン）

## 3. リクエスト

パラメータなし

## 4. レスポンス

### 成功 (200 OK)

```json
{
  "user_id": "uuid",
  "username": "山田太郎",
  "email": "yamada@example.com",
  "role": "master",
  "tenant_id": "uuid",
  "tenant_name": "株式会社サンプル"
}
```

### エラー (4xx)

| 状況 | ステータス | メッセージ内容 |
|---|---|---|
| 認証なし | 401 | 認証情報がありません |

## 5. 内部処理 / ロジック

1. **JWT検証**
   - ペイロードから `user_id`・`tenant_id` を取得
2. **データ取得**
   - `user` テーブルから `user_id`・`tenant_id` で検索
   - `tenant` テーブルから `tenant_name` を取得
3. **レスポンス**
   - ユーザー情報・テナント名を返す
