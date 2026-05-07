<script setup lang="ts">
// 01-01-01 テナント登録画面
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, setTokens } from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  tenant_name: '',
  username: '',
  email: '',
  password: '',
  password_confirm: '',
})
const errors = reactive({
  tenant_name: '',
  username: '',
  email: '',
  password: '',
  password_confirm: '',
})
const isLoading = ref(false)
const apiError = ref('')

const validate = (): boolean => {
  errors.tenant_name = form.tenant_name ? '' : 'テナント名は必須です'
  errors.username = form.username ? '' : 'マスターユーザー名は必須です'
  errors.email = form.email ? '' : 'メールアドレスは必須です'
  errors.password = form.password.length >= 8
    ? '' : 'パスワードは8文字以上で入力してください'
  errors.password_confirm = form.password_confirm === form.password
    ? '' : 'パスワードが一致しません'
  return !(errors.tenant_name || errors.username || errors.email
    || errors.password || errors.password_confirm)
}

const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  apiError.value = ''
  try {
    const res = await api.auth.registerTenant({
      tenant_name: form.tenant_name,
      username: form.username,
      email: form.email,
      password: form.password,
    })
    // トークン保存とログイン状態の反映
    setTokens(res.access, res.refresh)
    authStore.currentUser = res.user
    authStore.isLoggedIn = true
    router.push('/dashboard')
  } catch (err) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const e = err as any
    const data = e.response?.data ?? {}
    apiError.value =
      data.detail ??
      data.tenant_name?.[0] ??
      data.email?.[0] ??
      data.username?.[0] ??
      data.password?.[0] ??
      'テナント登録に失敗しました'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div id="tenant_register__container" class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white rounded-lg shadow p-8 w-full max-w-md">
      <h1 class="text-2xl font-bold text-sky-900 mb-6 text-center">新規テナント登録</h1>

      <form id="tenant_register__form" @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="tenant_register__tenant_name_input" class="block text-sm font-medium text-gray-700 mb-1">テナント名 <span class="text-red-500">*</span></label>
          <input
            id="tenant_register__tenant_name_input"
            v-model="form.tenant_name"
            type="text"
            data-testid="register-tenant-name"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.tenant_name" class="text-red-500 text-xs mt-1">{{ errors.tenant_name }}</p>
        </div>

        <div>
          <label for="tenant_register__username_input" class="block text-sm font-medium text-gray-700 mb-1">マスターユーザー名 <span class="text-red-500">*</span></label>
          <input
            id="tenant_register__username_input"
            v-model="form.username"
            type="text"
            data-testid="register-username"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="例: 山田太郎"
          />
          <p v-if="errors.username" class="text-red-500 text-xs mt-1">{{ errors.username }}</p>
        </div>

        <div>
          <label for="tenant_register__email_input" class="block text-sm font-medium text-gray-700 mb-1">メールアドレス <span class="text-red-500">*</span></label>
          <input
            id="tenant_register__email_input"
            v-model="form.email"
            type="email"
            data-testid="register-email"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
        </div>

        <div>
          <label for="tenant_register__password_input" class="block text-sm font-medium text-gray-700 mb-1">パスワード（8文字以上）<span class="text-red-500">*</span></label>
          <input
            id="tenant_register__password_input"
            v-model="form.password"
            type="password"
            autocomplete="new-password"
            data-testid="register-password"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.password" class="text-red-500 text-xs mt-1">{{ errors.password }}</p>
        </div>

        <div>
          <label for="tenant_register__password_confirm_input" class="block text-sm font-medium text-gray-700 mb-1">パスワード（確認）<span class="text-red-500">*</span></label>
          <input
            id="tenant_register__password_confirm_input"
            v-model="form.password_confirm"
            type="password"
            autocomplete="new-password"
            data-testid="register-password-confirm"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.password_confirm" class="text-red-500 text-xs mt-1">{{ errors.password_confirm }}</p>
        </div>

        <p v-if="apiError" class="text-sm text-red-600 bg-red-50 p-3 rounded">{{ apiError }}</p>

        <button
          id="tenant_register__submit_btn"
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
