<script setup lang="ts">
// 01-01-01 テナント登録画面
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({ tenant_name: '', email: '', password: '', password_confirm: '' })
const errors = reactive({ tenant_name: '', email: '', password: '', password_confirm: '' })
const isLoading = ref(false)

/**
 * バリデーション処理
 * @returns バリデーション成功時はtrue
 */
const validate = (): boolean => {
  let ok = true
  errors.tenant_name = form.tenant_name ? '' : 'テナント名は必須です'
  errors.email = form.email ? '' : 'メールアドレスは必須です'
  errors.password = form.password ? '' : 'パスワードは必須です'
  errors.password_confirm = form.password_confirm === form.password ? '' : 'パスワードが一致しません'
  if (errors.tenant_name || errors.email || errors.password || errors.password_confirm) ok = false
  return ok
}

/**
 * テナント登録ボタン押下時の処理
 * バリデーション後、MOCKログインしてダッシュボードへ遷移する
 */
const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  authStore.login(form.email, form.password)
  isLoading.value = false
  router.push('/dashboard')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white rounded-lg shadow p-8 w-full max-w-md">
      <h1 class="text-2xl font-bold text-sky-900 mb-6 text-center">新規テナント登録</h1>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">テナント名 <span class="text-red-500">*</span></label>
          <input
            v-model="form.tenant_name"
            type="text"
            data-testid="register-tenant-name"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.tenant_name" class="text-red-500 text-xs mt-1">{{ errors.tenant_name }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">メールアドレス <span class="text-red-500">*</span></label>
          <input
            v-model="form.email"
            type="email"
            data-testid="register-email"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">パスワード <span class="text-red-500">*</span></label>
          <input
            v-model="form.password"
            type="password"
            data-testid="register-password"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.password" class="text-red-500 text-xs mt-1">{{ errors.password }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">パスワード（確認）<span class="text-red-500">*</span></label>
          <input
            v-model="form.password_confirm"
            type="password"
            data-testid="register-password-confirm"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.password_confirm" class="text-red-500 text-xs mt-1">{{ errors.password_confirm }}</p>
        </div>

        <button
          type="submit"
          data-testid="register-submit"
          class="w-full bg-blue-600 text-white py-2 rounded font-medium text-sm hover:bg-blue-700 disabled:opacity-50"
          :disabled="isLoading"
        >
          {{ isLoading ? '登録中...' : '登録する' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        すでにアカウントをお持ちの方は
        <router-link to="/login" class="text-blue-600 hover:underline">ログイン</router-link>
      </p>
    </div>
  </div>
</template>
