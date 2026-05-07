<script setup lang="ts">
// 01-02-05 ユーザー招待画面
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import type { UserRole } from '@/types'

const router = useRouter()

const form = reactive({ email: '', role: 'member' as UserRole })
const errors = reactive({ email: '', role: '' })
const isLoading = ref(false)
const successMessage = ref('')
const inviteToken = ref('')
const apiError = ref('')

const validate = (): boolean => {
  errors.email = form.email ? '' : 'メールアドレスは必須です'
  return !errors.email
}

const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  apiError.value = ''
  try {
    const res = await api.auth.invite(form.email, form.role)
    successMessage.value =
      `${form.email} の招待を作成しました（有効期限: ${new Date(res.expires_at).toLocaleString()}）`
    inviteToken.value = res.token
  } catch (err) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const e = err as any
    apiError.value =
      e.response?.data?.detail ??
      e.response?.data?.email?.[0] ??
      '招待の作成に失敗しました'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div id="user_invite__container" class="max-w-md">
    <div class="flex items-center gap-3 mb-6">
      <router-link to="/users" class="text-blue-600 hover:underline text-sm">
        ← ユーザー管理
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">ユーザー招待</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <!-- 成功メッセージ -->
      <div v-if="successMessage" class="mb-4 bg-green-50 p-3 rounded text-sm">
        <p class="text-green-700 mb-1">{{ successMessage }}</p>
        <p v-if="inviteToken" class="text-xs text-green-700 break-all">
          招待リンク：<code class="bg-white border border-green-200 px-1 rounded">/invitations/{{ inviteToken }}/accept/</code>
        </p>
      </div>
      <p v-if="apiError" class="text-sm text-red-600 mb-4 bg-red-50 p-3 rounded">{{ apiError }}</p>

      <form id="user_invite__form" @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="user_invite__email_input" class="block text-sm font-medium text-gray-700 mb-1">メールアドレス <span class="text-red-500">*</span></label>
          <input
            id="user_invite__email_input"
            v-model="form.email"
            type="email"
            data-testid="invite-email"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="invite@example.com"
          />
          <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
        </div>

        <div>
          <label for="user_invite__role_select" class="block text-sm font-medium text-gray-700 mb-1">ロール</label>
          <select
            id="user_invite__role_select"
            v-model="form.role"
            data-testid="invite-role"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="admin">管理者</option>
            <option value="member">メンバー</option>
          </select>
        </div>

        <div class="flex gap-2 pt-2">
          <button
            id="user_invite__submit_btn"
            type="submit"
            data-testid="invite-submit"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            :disabled="isLoading"
          >
            {{ isLoading ? '送信中...' : '招待メール送信' }}
          </button>
          <router-link to="/users" class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50">
            キャンセル
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
