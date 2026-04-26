<script setup lang="ts">
// 02-01-01 プロジェクト登録画面
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const form = reactive({ name: '', description: '', start_date: '', end_date: '' })
const errors = reactive({ name: '', end_date: '' })
const isLoading = ref(false)

/**
 * バリデーション処理
 * @returns バリデーション成功時はtrue
 */
const validate = (): boolean => {
  errors.name = form.name ? '' : 'プロジェクト名は必須です'
  // 終了日が開始日より前のチェック
  if (form.start_date && form.end_date && form.end_date < form.start_date) {
    errors.end_date = '終了日は開始日より後の日付を入力してください'
  } else {
    errors.end_date = ''
  }
  return !errors.name && !errors.end_date
}

/**
 * 保存ボタン押下時の処理
 * MOCK：バリデーション後、プロジェクト一覧へ遷移する
 */
const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  await new Promise(r => setTimeout(r, 400))
  isLoading.value = false
  router.push('/projects')
}
</script>

<template>
  <div class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <router-link to="/projects" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト一覧
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">プロジェクト登録</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">プロジェクト名 <span class="text-red-500">*</span></label>
          <input
            v-model="form.name"
            type="text"
            data-testid="project-name-input"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">説明</label>
          <textarea
            v-model="form.description"
            rows="3"
            data-testid="project-description-input"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">開始日</label>
            <input
              v-model="form.start_date"
              type="date"
              data-testid="project-start-date"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">終了日</label>
            <input
              v-model="form.end_date"
              type="date"
              data-testid="project-end-date"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p v-if="errors.end_date" class="text-red-500 text-xs mt-1">{{ errors.end_date }}</p>
          </div>
        </div>

        <div class="flex gap-2 pt-2">
          <button
            type="submit"
            data-testid="project-save"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            :disabled="isLoading"
          >
            {{ isLoading ? '保存中...' : '保存' }}
          </button>
          <router-link to="/projects" class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50">
            キャンセル
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
