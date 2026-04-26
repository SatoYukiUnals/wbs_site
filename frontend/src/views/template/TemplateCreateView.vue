<script setup lang="ts">
// 11-01-01 テンプレート登録画面
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import type { TemplateType } from '@/types'

const router = useRouter()

const form = reactive({
  title: '',
  type: 'wbs' as TemplateType,
  content: '',
  is_shared: false,
})
const errors = reactive({ title: '', content: '' })
const isLoading = ref(false)

const validate = (): boolean => {
  errors.title = form.title.trim() ? '' : 'テンプレート名は必須です'
  errors.content = form.content.trim() ? '' : 'テンプレート内容は必須です'
  return !errors.title && !errors.content
}

const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  await api.templates.create({ title: form.title, type: form.type, content: form.content, is_shared: form.is_shared })
  isLoading.value = false
  router.push('/templates')
}
</script>

<template>
  <div id="template_create__container" class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <router-link to="/templates" class="text-blue-600 hover:underline text-sm">
        ← テンプレート一覧
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">テンプレート登録</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <form id="template_create__form" @submit.prevent="handleSubmit" class="space-y-4">
        <!-- テンプレート名 -->
        <div>
          <label for="template_create__title_input" class="block text-sm font-medium text-gray-700 mb-1">テンプレート名 <span class="text-red-500">*</span></label>
          <input
            id="template_create__title_input"
            v-model="form.title"
            type="text"
            data-testid="template-title-input"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.title" class="text-red-500 text-xs mt-1">{{ errors.title }}</p>
        </div>

        <!-- 種別・共有 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="template_create__type_select" class="block text-sm font-medium text-gray-700 mb-1">種別</label>
            <select id="template_create__type_select" v-model="form.type" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              <option value="wbs">WBS</option>
              <option value="task">タスク</option>
            </select>
          </div>
          <div class="flex items-end pb-2">
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input id="template_create__is_shared_input" v-model="form.is_shared" type="checkbox" class="rounded" />
              テナント全体に共有する
            </label>
          </div>
        </div>

        <!-- テンプレート内容 -->
        <div>
          <label for="template_create__content_textarea" class="block text-sm font-medium text-gray-700 mb-1">テンプレート内容 <span class="text-red-500">*</span></label>
          <textarea
            id="template_create__content_textarea"
            v-model="form.content"
            rows="10"
            data-testid="template-content-input"
            placeholder="テンプレートの内容を入力してください..."
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
          />
          <p v-if="errors.content" class="text-red-500 text-xs mt-1">{{ errors.content }}</p>
        </div>

        <div class="flex gap-2 pt-2">
          <button
            id="template_create__save_btn"
            type="submit"
            :disabled="isLoading"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
          >
            {{ isLoading ? '保存中...' : '保存' }}
          </button>
          <router-link
            to="/templates"
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
          >
            キャンセル
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
