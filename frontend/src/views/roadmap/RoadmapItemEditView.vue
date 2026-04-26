<script setup lang="ts">
// 06-01-02 ロードマップアイテム編集画面
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { mockRoadmapItems, mockQuarters } from '@/mocks/data'
import type { RoadmapStatus } from '@/types'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId as string
const itemId = route.params.itemId as string

const item = mockRoadmapItems.find(i => i.id === itemId)
const quarters = mockQuarters.filter(q => q.project_id === projectId)

const form = reactive({
  title: item?.title ?? '',
  description: item?.description ?? '',
  quarter_id: item?.quarter_id ?? '',
  status: (item?.status ?? '計画中') as RoadmapStatus,
})
const errors = reactive({ title: '', quarter_id: '' })
const isLoading = ref(false)

const validate = (): boolean => {
  errors.title = form.title.trim() ? '' : 'タイトルは必須です'
  errors.quarter_id = form.quarter_id ? '' : 'クォーターを選択してください'
  return !errors.title && !errors.quarter_id
}

const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  await new Promise(r => setTimeout(r, 400))
  isLoading.value = false
  router.push(`/projects/${projectId}/roadmap`)
}
</script>

<template>
  <div class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}/roadmap`" class="text-blue-600 hover:underline text-sm">
        ← ロードマップ
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">アイテム編集</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">タイトル <span class="text-red-500">*</span></label>
          <input
            v-model="form.title"
            type="text"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.title" class="text-red-500 text-xs mt-1">{{ errors.title }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">説明</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">クォーター <span class="text-red-500">*</span></label>
            <select v-model="form.quarter_id" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              <option value="">選択してください</option>
              <option v-for="q in quarters" :key="q.id" :value="q.id">{{ q.title }}</option>
            </select>
            <p v-if="errors.quarter_id" class="text-red-500 text-xs mt-1">{{ errors.quarter_id }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">ステータス</label>
            <select v-model="form.status" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              <option value="計画中">計画中</option>
              <option value="進行中">進行中</option>
              <option value="完了">完了</option>
              <option value="保留">保留</option>
            </select>
          </div>
        </div>

        <div class="flex gap-2 pt-2">
          <button
            type="submit"
            :disabled="isLoading"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
          >
            {{ isLoading ? '保存中...' : '保存' }}
          </button>
          <router-link
            :to="`/projects/${projectId}/roadmap`"
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
          >
            キャンセル
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
