<script setup lang="ts">
// 03-01-02 クォーター編集画面
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId as string
const quarterId = route.params.quarterId as string

const form = reactive({ title: '', start_date: '', end_date: '' })
const errors = reactive({ title: '', end_date: '' })
const isLoading = ref(true)

onMounted(async () => {
  const quarters = await api.quarters.list(projectId)
  const quarter = quarters.find(q => q.id === quarterId)
  if (quarter) {
    form.title = quarter.title
    form.start_date = quarter.start_date
    form.end_date = quarter.end_date
  }
  isLoading.value = false
})

/** バリデーション処理 */
const validate = (): boolean => {
  errors.title = form.title ? '' : 'クォーター名は必須です'
  if (form.start_date && form.end_date && form.end_date < form.start_date) {
    errors.end_date = '終了日は開始日より後の日付を入力してください'
  } else {
    errors.end_date = ''
  }
  return !errors.title && !errors.end_date
}

/** 保存ボタン押下時の処理 */
const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  try {
    await api.quarters.update(projectId, quarterId, form)
    router.push(`/projects/${projectId}/quarters`)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div id="quarter_edit__container" class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}/quarters`" class="text-blue-600 hover:underline text-sm">
        ← クォーター管理
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">クォーター編集</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <form id="quarter_edit__form" @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="quarter_edit__title_input" class="block text-sm font-medium text-gray-700 mb-1">クォーター名 <span class="text-red-500">*</span></label>
          <input
            id="quarter_edit__title_input"
            v-model="form.title"
            type="text"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.title" class="text-red-500 text-xs mt-1">{{ errors.title }}</p>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="quarter_edit__start_date_input" class="block text-sm font-medium text-gray-700 mb-1">開始日</label>
            <input
              id="quarter_edit__start_date_input"
              v-model="form.start_date"
              type="date"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label for="quarter_edit__end_date_input" class="block text-sm font-medium text-gray-700 mb-1">終了日</label>
            <input
              id="quarter_edit__end_date_input"
              v-model="form.end_date"
              type="date"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
            <p v-if="errors.end_date" class="text-red-500 text-xs mt-1">{{ errors.end_date }}</p>
          </div>
        </div>

        <div class="flex gap-2 pt-2">
          <button
            id="quarter_edit__save_btn"
            type="submit"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            :disabled="isLoading"
          >
            {{ isLoading ? '保存中...' : '保存' }}
          </button>
          <router-link
            :to="`/projects/${projectId}/quarters`"
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
          >
            キャンセル
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
