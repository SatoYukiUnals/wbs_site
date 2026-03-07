# wbs_site
WBS（Work Breakdown Structure）管理Webサイト

Django + Vue 3 + TypeScript + Docker で構築されています。

## 技術スタック

- **バックエンド**: Django 4.2 + Django REST Framework
- **フロントエンド**: Vue 3 + TypeScript + Vite
- **データベース**: PostgreSQL 15
- **コンテナ**: Docker / Docker Compose

## プロジェクト構成

```
wbs_site/
├── docker-compose.yml
├── .env.example
├── backend/                # Django バックエンド
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/             # Django 設定
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── wbs/                # WBS アプリ
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
└── frontend/               # Vue フロントエンド
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.vue
        ├── api/            # API クライアント
        ├── types/          # TypeScript 型定義
        └── components/     # Vue コンポーネント
```

## セットアップ

### 1. 環境変数ファイルの作成

```bash
cp .env.example .env
# .env を編集して適切な値を設定してください
```

### 2. Docker コンテナの起動

```bash
docker-compose up --build
```

### 3. データベースのマイグレーション（初回のみ）

```bash
docker-compose exec backend python manage.py migrate
```

### 4. スーパーユーザーの作成（任意）

```bash
docker-compose exec backend python manage.py createsuperuser
```

## アクセス

| サービス | URL |
|---------|-----|
| フロントエンド | http://localhost:3000 |
| バックエンド API | http://localhost:8000/api/wbs/ |
| Django 管理画面 | http://localhost:8000/admin/ |

## API エンドポイント

| メソッド | URL | 説明 |
|---------|-----|------|
| GET | `/api/wbs/` | WBSアイテム一覧取得 |
| POST | `/api/wbs/` | WBSアイテム作成 |
| GET | `/api/wbs/{id}/` | WBSアイテム詳細取得 |
| PUT | `/api/wbs/{id}/` | WBSアイテム更新 |
| PATCH | `/api/wbs/{id}/` | WBSアイテム部分更新 |
| DELETE | `/api/wbs/{id}/` | WBSアイテム削除 |

## WBSアイテムのフィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| title | string | タイトル（必須） |
| description | string | 説明 |
| status | string | ステータス (not_started/in_progress/completed/on_hold) |
| priority | number | 優先度 (1=低/2=中/3=高) |
| assignee | string | 担当者 |
| start_date | date | 開始日 |
| end_date | date | 終了日 |
| progress | number | 進捗率 (0-100) |
| parent | number | 親タスクID（階層構造） |
| order | number | 表示順序 |
