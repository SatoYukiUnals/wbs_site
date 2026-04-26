<script setup lang="ts">
// 01-02-05 ユーザー招待画面
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { UserRole } from '@/types'

const router = useRouter()

const form = reactive({ email: '', role: 'member' as UserRole })
const errors = reactive({ email: '', role: '' })
const isLoading = ref(false)
const successMessage = ref('')

/**
 * バリデーション処理
 * @returns バリデーション成功時はtrue
 */
const validate = (): boolean => {
  errors.email = form.email ? '' : 'メールアドレスは必須です'
  return !errors.email
}

/**
 * 招待メール送信ボタン押下時の処理
 * バリデーション後、MOCKで成功メッセージを表示してユーザー管理画面へ遷移する
 */
const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  // MOCK：非同期処理をシミュレート
  await new Promise(r => setTimeout(r, 500))
  isLoading.value = false
  successMessage.value = `${form.email} に招待メールを送信しました`
  setTimeout(() => router.push('/users'), 1500)
}
</script>

<template>
  <div class="max-w-md">
    <div class="flex items-center gap-3 mb-6">
      <router-link to="/users" class="text-blue-600 hover:underline text-sm">
        ← ユーザー管理
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">ユーザー招待</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <!-- 成功メッセージ -->
      <p v-if="successMessage" class="text-green-600 text-sm mb-4 bg-green-50 p-3 rounded">
        {{ successMessage }}
      </p>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">メールアドレス <span class="text-red-500">*</span></label>
          <input
            v-model="form.email"
            type="email"
            data-testid="invite-email"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="invite@example.com"
          />
          <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ロール</label>
          <select
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
