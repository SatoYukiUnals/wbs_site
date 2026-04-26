<script setup lang="ts">
// 02-01-02 プロジェクト編集画面
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'

const router = useRouter()
const route = useRoute()

const projectId = route.params.projectId as string

const form = reactive({ name: '', description: '' })
const errors = reactive({ name: '' })
const isLoading = ref(true)

onMounted(async () => {
  const project = await api.projects.get(projectId)
  form.name = project.name
  form.description = project.description
  isLoading.value = false
})

/** バリデーション処理 */
const validate = (): boolean => {
  errors.name = form.name ? '' : 'プロジェクト名は必須です'
  return !errors.name
}

/** 保存ボタン押下時の処理 */
const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  try {
    await api.projects.update(projectId, form)
    router.push(`/projects/${projectId}`)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div id="project_edit__container" class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">プロジェクト編集</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <form id="project_edit__form" @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="project_edit__name_input" class="block text-sm font-medium text-gray-700 mb-1">プロジェクト名 <span class="text-red-500">*</span></label>
          <input
            id="project_edit__name_input"
            v-model="form.name"
            type="text"
            data-testid="project-name-input"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
        </div>

        <div>
          <label for="project_edit__description_textarea" class="block text-sm font-medium text-gray-700 mb-1">説明</label>
          <textarea
            id="project_edit__description_textarea"
            v-model="form.description"
            rows="3"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div class="flex gap-2 pt-2">
          <button
            id="project_edit__save_btn"
            type="submit"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            :disabled="isLoading"
          >
            {{ isLoading ? '保存中...' : '保存' }}
          </button>
          <router-link
            :to="`/projects/${projectId}`"
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
          >
            キャンセル
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
