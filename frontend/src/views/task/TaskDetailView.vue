<script setup lang="ts">
// 04-01-03 タスク詳細・編集画面
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { mockTasks, mockQuarters } from '@/mocks/data'
import type { TaskStatus, TaskKind } from '@/types'

const route = useRoute()
const router = useRouter()
const taskId = route.params.taskId as string

/** ツリーからIDで検索（再帰） */
const findTask = (tasks: typeof mockTasks, id: string): typeof mockTasks[0] | undefined => {
  for (const t of tasks) {
    if (t.id === id) return t
    if (t.children) {
      const found = findTask(t.children as typeof mockTasks, id)
      if (found) return found
    }
  }
}

const task = findTask(mockTasks, taskId)
const projectId = task?.project_id ?? ''
const quarters = mockQuarters.filter(q => q.project_id === projectId)
const isLoading = ref(false)

const form = reactive({
  title: task?.title ?? '',
  description: task?.description ?? '',
  status: (task?.status ?? 'Todo') as TaskStatus,
  progress: task?.progress ?? 0,
  start_date: task?.start_date ?? '',
  end_date: task?.end_date ?? '',
  estimated_hours: task?.estimated_hours ?? '',
  quarter_id: task?.quarter_id ?? '',
  task_kind: (task?.task_kind ?? null) as TaskKind | null,
})

const errors = reactive({ title: '' })

const validate = (): boolean => {
  errors.title = form.title.trim() ? '' : 'タスク名は必須です'
  return !errors.title
}

/** 保存処理（MOCK） */
const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  await new Promise(r => setTimeout(r, 400))
  isLoading.value = false
  router.push(`/projects/${projectId}/wbs`)
}

/** ステータスに対応する色クラス */
const statusColor = (status: string): string => {
  const map: Record<string, string> = {
    'Todo':       'bg-green-100 text-green-700',
    'InProgress': 'bg-yellow-100 text-yellow-700',
    'InReview':   'bg-red-100 text-red-700',
    'Done':       'bg-purple-100 text-purple-700',
    'OnHold':     'bg-gray-100 text-gray-600',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}
</script>

<template>
  <div v-if="!task" class="text-gray-500 py-8 text-center">
    タスクが見つかりません
  </div>

  <div v-else class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}/wbs`" class="text-blue-600 hover:underline text-sm">
        ← WBS
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">タスク詳細</h1>
      <span :class="statusColor(form.status)" class="px-2 py-0.5 rounded-full text-xs ml-auto">
        {{ form.status }}
      </span>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- タスク名 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">タスク名 <span class="text-red-500">*</span></label>
          <input
            v-model="form.title"
            type="text"
            data-testid="task-title-input"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.title" class="text-red-500 text-xs mt-1">{{ errors.title }}</p>
        </div>

        <!-- 説明 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">説明</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- ステータス -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ステータス</label>
          <select
            v-model="form.status"
            data-testid="task-status-select"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
          >
            <option value="Todo">Todo</option>
            <option value="InProgress">InProgress</option>
            <option value="InReview">InReview</option>
            <option value="Done">Done</option>
            <option value="OnHold">OnHold</option>
          </select>
        </div>

        <!-- タスク種別 -->
        <div v-if="task.task_type === 'task'">
          <label class="block text-sm font-medium text-gray-700 mb-1">タスク種別</label>
          <select v-model="form.task_kind" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
            <option :value="null">未設定</option>
            <option value="実装">実装</option>
            <option value="ドキュメント作成">ドキュメント作成</option>
            <option value="レビュー依頼">レビュー依頼</option>
            <option value="レビュー修正">レビュー修正</option>
          </select>
        </div>

        <!-- 開始日・終了日 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">開始日</label>
            <input v-model="form.start_date" type="date" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">終了日</label>
            <input v-model="form.end_date" type="date" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
          </div>
        </div>

        <!-- 見積時間・クォーター -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">見積時間（h）</label>
            <input
              v-model.number="form.estimated_hours"
              type="number"
              min="0"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">クォーター</label>
            <select v-model="form.quarter_id" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              <option value="">未設定</option>
              <option v-for="q in quarters" :key="q.id" :value="q.id">{{ q.title }}</option>
            </select>
          </div>
        </div>

        <!-- 担当者（MOCK表示のみ） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">担当者</label>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="a in task.assignees"
              :key="a.id"
              class="bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full"
            >
              {{ a.name }}
            </span>
            <span v-if="task.assignees.length === 0" class="text-sm text-gray-400">未割り当て</span>
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
            :to="`/projects/${projectId}/wbs`"
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
          >
            キャンセル
          </router-link>
        </div>
      </form>
    </div>

  </div>
</template>
