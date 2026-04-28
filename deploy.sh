#!/bin/bash
# ============================================================
# ConoHa VPS デプロイスクリプト
#
# 使い方:
#   ./deploy.sh                                      # main をデプロイ
#   ./deploy.sh feature/xxx                          # ブランチ指定
#   ./deploy.sh feature/xxx --reset                  # DB リセット付き
#   ./deploy.sh feature/xxx --reset --seed seeds/demo.py
#
# オプション:
#   --reset         DB を削除して再作成（マイグレーションもやり直し）
#   --seed <file>   リセット後に実行するデータ生成スクリプトのパス
#                   ※ VPS 上のプロジェクトルートからの相対パス
# ============================================================

set -e

# ──────────────────────────────────────────
# 設定（自分の環境に合わせて変更）
# ──────────────────────────────────────────
SSH_HOST="root@160.251.180.32"
SSH_KEY="~/.ssh/id_ed25519"
REMOTE_DIR="/var/www/wbs_site"
COMPOSE_FILE="docker-compose.prod.yml"
DB_SERVICE="db"
WEB_SERVICE="backend"
HTPASSWD_LOCAL="./frontend/.htpasswd"
HTPASSWD_REMOTE="frontend/.htpasswd"

# ──────────────────────────────────────────
# 引数パース
# ──────────────────────────────────────────
BRANCH=${1:-main}
DO_RESET=false
SEED_FILE=""

shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reset)
      DO_RESET=true
      shift
      ;;
    --seed)
      SEED_FILE="$2"
      shift 2
      ;;
    *)
      echo "不明なオプション: $1"
      exit 1
      ;;
  esac
done

if [[ -n "$SEED_FILE" && "$DO_RESET" == false ]]; then
  echo "⚠️  --seed は --reset と一緒に使ってください"
  exit 1
fi

# ──────────────────────────────────────────
# 確認プロンプト
# ──────────────────────────────────────────
echo "========================================"
echo "  デプロイ先 : $SSH_HOST"
echo "  ブランチ   : $BRANCH"
echo "  DB リセット: $DO_RESET"
[[ -n "$SEED_FILE" ]] && echo "  データ生成 : $SEED_FILE"
echo "========================================"

if [[ "$DO_RESET" == true ]]; then
  echo ""
  echo "⚠️  DB リセットを実行します。全データが削除されます。"
fi

read -p "デプロイを実行しますか？ [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "キャンセルしました"
  exit 0
fi

# ──────────────────────────────────────────
# .htpasswd アップロード
# ──────────────────────────────────────────
echo ""
echo "▶ .htpasswd をアップロードしています..."

if [[ -f "$HTPASSWD_LOCAL" ]]; then
  scp -i "$SSH_KEY" "$HTPASSWD_LOCAL" "$SSH_HOST:$REMOTE_DIR/$HTPASSWD_REMOTE"
  echo "✅ .htpasswd をアップロードしました"
else
  echo "⚠️  $HTPASSWD_LOCAL が見つかりません。Basic 認証なしでデプロイします"
fi

# ──────────────────────────────────────────
# デプロイ実行
# ──────────────────────────────────────────
echo ""
echo "▶ VPS に接続してデプロイを開始します..."

ssh -i "$SSH_KEY" "$SSH_HOST" \
  DO_RESET="$DO_RESET" \
  SEED_FILE="$SEED_FILE" \
  BRANCH="$BRANCH" \
  REMOTE_DIR="$REMOTE_DIR" \
  COMPOSE_FILE="$COMPOSE_FILE" \
  DB_SERVICE="$DB_SERVICE" \
  WEB_SERVICE="$WEB_SERVICE" \
  'bash -s' << 'ENDSSH'

set -e

echo ""
echo "── [1/6] プロジェクトディレクトリへ移動"
cd "$REMOTE_DIR"

echo ""
echo "── [2/6] ブランチ取得・切り替え: $BRANCH"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

if [ "$DO_RESET" = "true" ]; then
  echo ""
  echo "── [3/6] DB リセット"
  docker compose -f "$COMPOSE_FILE" stop "$WEB_SERVICE" "$DB_SERVICE"
  docker compose -f "$COMPOSE_FILE" rm -f "$DB_SERVICE"
  docker volume ls -q | grep postgres_data | xargs -r docker volume rm || true
  docker compose -f "$COMPOSE_FILE" up -d "$DB_SERVICE"
  echo "DB 起動待機中 (10秒)..."
  sleep 10
  echo "DB リセット完了"
else
  echo ""
  echo "── [3/6] DB リセット: スキップ"
fi

echo ""
echo "── [4/6] Docker イメージをビルドして起動"
docker compose -f "$COMPOSE_FILE" up -d --build

echo ""
echo "── [5/6] 静的ファイル収集（migrate は entrypoint.sh が実行）"
# migrate は entrypoint.sh がコンテナ起動時に流すため、ここでは実行しない
# （二重実行で UniqueViolation のレースが発生するため）
docker compose -f "$COMPOSE_FILE" exec -T "$WEB_SERVICE" python manage.py collectstatic --noinput

if [ -n "$SEED_FILE" ]; then
  echo ""
  echo "── [6/6] データ生成: $SEED_FILE"
  docker compose -f "$COMPOSE_FILE" exec -T "$WEB_SERVICE" python "$SEED_FILE"
else
  echo ""
  echo "── [6/6] データ生成: スキップ"
fi

echo ""
echo "✅ デプロイ完了！ブランチ: $BRANCH"
ENDSSH

echo ""
echo "========================================"
echo "  ✅ 完了 : http://${SSH_HOST#*@} でアクセスできます"
echo "========================================"
