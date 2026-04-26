import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      // Docker コンテナ内からホストへポートを公開するために全インターフェースでリッスン
      host: '0.0.0.0',
      // /api/ をバックエンドコンテナへプロキシ
      // Docker 外で開発する場合は frontend/.env.local に VITE_API_PROXY=http://localhost:8000 を設定
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY || 'http://backend:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
