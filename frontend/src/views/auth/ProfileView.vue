<script setup lang="ts">
// 01-03-03 プロフィール画面
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'

const authStore = useAuthStore()

const form = reactive({
  display_name: authStore.currentUser?.display_name ?? '',
  email: authStore.currentUser?.email ?? '',
})
const isLoading = ref(false)
const successMessage = ref('')
const errors = reactive({ display_name: '', email: '' })

/** バリデーション処理 */
const validate = (): boolean => {
  errors.display_name = form.display_name ? '' : '表示名は必須です'
  errors.email = form.email ? '' : 'メールアドレスは必須です'
  return !errors.display_name && !errors.email
}

/** プロフィール保存ボタン押下時の処理 */
const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  try {
    const updated = await api.auth.updateProfile(form.display_name)
    if (authStore.currentUser) {
      authStore.currentUser.display_name = updated.display_name
    }
    successMessage.value = 'プロフィールを更新しました'
    setTimeout(() => { successMessage.value = '' }, 3000)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div id="profile__container" class="max-w-md">
    <h1 class="text-xl font-bold text-sky-900 mb-6">プロフィール</h1>

    <div class="bg-white rounded-lg shadow p-6">
      <p v-if="successMessage" class="text-green-600 text-sm mb-4 bg-green-50 p-3 rounded">
        {{ successMessage }}
      </p>

      <form id="profile__form" @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="profile__display_name_input" class="block text-sm font-medium text-gray-700 mb-1">表示名 <span class="text-red-500">*</span></label>
          <input
            id="profile__display_name_input"
            v-model="form.display_name"
            type="text"
            data-testid="profile-display-name"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.display_name" class="text-red-500 text-xs mt-1">{{ errors.display_name }}</p>
        </div>

        <div>
          <label for="profile__email_input" class="block text-sm font-medium text-gray-700 mb-1">メールアドレス <span class="text-red-500">*</span></label>
          <input
            id="profile__email_input"
            v-model="form.email"
            type="email"
            data-testid="profile-email"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ロール</label>
          <p class="text-sm text-gray-600 py-2">{{ authStore.currentUser?.role }}</p>
        </div>

        <button
          id="profile__save_btn"
          type="submit"
          data-testid="profile-save"
          class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
          :disabled="isLoading"
        >
          {{ isLoading ? '保存中...' : '保存' }}
        </button>
      </form>
    </div>
  </div>
</template>
