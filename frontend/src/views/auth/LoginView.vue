<script setup lang="ts">
// 01-01-04 ログイン画面
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({ email: '', password: '' })
const error = ref('')
const isLoading = ref(false)

/** ログインボタン押下時の処理 */
const handleSubmit = async () => {
  error.value = ''
  if (!form.email || !form.password) {
    error.value = 'メールアドレスとパスワードを入力してください'
    return
  }
  isLoading.value = true
  const ok = await authStore.login(form.email, form.password)
  isLoading.value = false
  if (ok) {
    router.push('/dashboard')
  } else {
    error.value = 'メールアドレスまたはパスワードが正しくありません'
  }
}
</script>

<template>
  <div id="login__container" class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white rounded-lg shadow p-8 w-full max-w-sm">
      <h1 class="text-2xl font-bold text-sky-900 mb-6 text-center">WBS管理</h1>

      <!-- エラーメッセージ -->
      <p v-if="error" class="text-red-600 text-sm mb-4 bg-red-50 p-3 rounded">
        {{ error }}
      </p>

      <form id="login__form" @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="login__email_input" class="block text-sm font-medium text-gray-700 mb-1">メールアドレス</label>
          <input
            id="login__email_input"
            v-model="form.email"
            type="email"
            data-testid="login-email"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="email@example.com"
          />
        </div>

        <div>
          <label for="login__password_input" class="block text-sm font-medium text-gray-700 mb-1">パスワード</label>
          <input
            id="login__password_input"
            v-model="form.password"
            type="password"
            data-testid="login-password"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="パスワード"
          />
        </div>

        <button
          id="login__submit_btn"
          type="submit"
          data-testid="login-submit"
          class="w-full bg-blue-600 text-white py-2 rounded font-medium text-sm hover:bg-blue-700 disabled:opacity-50"
          :disabled="isLoading"
        >
          {{ isLoading ? 'ログイン中...' : 'ログイン' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        アカウントをお持ちでない方は
        <router-link to="/register" class="text-blue-600 hover:underline">こちら</router-link>
      </p>
    </div>
  </div>
</template>
