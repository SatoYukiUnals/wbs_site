# =====================================================================
# ステージ1：Node.js で Vue.js アプリをビルド
# =====================================================================
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --frozen-lockfile

COPY . .
RUN npm run build

# =====================================================================
# ステージ2：Nginx で静的ファイルを配信
# =====================================================================
FROM nginx:1.27-alpine

# ビルド成果物をコピー
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 設定をコピー
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
