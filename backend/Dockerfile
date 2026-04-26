# =====================================================================
# Django + Gunicorn 本番イメージ
# ※ バックエンド実装フェーズ（実装②）で詳細を追記する
# =====================================================================
FROM python:3.12-slim

# Python バイトコードキャッシュを無効化・標準出力をバッファなしに設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# システム依存パッケージ（PostgreSQL クライアント・WeasyPrint 依存）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 依存パッケージをインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Django static ファイルを収集（本番用）
RUN python manage.py collectstatic --no-input

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
