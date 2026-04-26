<script setup lang="ts">
// 07-01-00 ダッシュボード画面
import { ref } from 'vue'
import { mockProjectSummaries, mockMyTasks } from '@/mocks/data'
import type { ProjectSummary, MyTask } from '@/types'

const projectSummaries = ref<ProjectSummary[]>(mockProjectSummaries)
const myTasks = ref<MyTask[]>(mockMyTasks)

/** ステータスに対応する色クラスを返す */
const statusColor = (status: string): string => {
  const map: Record<string, string> = {
    '未着手': 'bg-gray-100 text-gray-600',
    '進行中': 'bg-blue-100 text-blue-700',
    '完了': 'bg-green-100 text-green-700',
    'レビュー待ち': 'bg-yellow-100 text-yellow-700',
    '保留': 'bg-red-100 text-red-600',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-sky-900 mb-6">ダッシュボード</h1>

    <!-- プロジェクトサマリー -->
    <h2 class="text-sm font-semibold text-gray-600 mb-3">プロジェクト一覧</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <router-link
        v-for="p in projectSummaries"
        :key="p.id"
        :to="`/projects/${p.id}`"
        class="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow block"
      >
        <div class="flex items-center justify-between mb-3">
          <span class="font-medium text-sky-900">{{ p.name }}</span>
          <span v-if="p.delayed_count > 0" class="text-xs text-red-500 font-medium">
            遅延 {{ p.delayed_count }}件
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div class="bg-blue-500 h-2 rounded-full" :style="{ width: `${p.progress}%` }" />
        </div>
        <div class="flex items-center justify-between text-xs text-gray-500 mb-3">
          <span>進捗率</span>
          <span class="font-medium text-gray-700">{{ p.progress }}%</span>
        </div>
        <div class="flex gap-2 flex-wrap text-xs">
          <span v-for="(count, status) in p.status_counts" :key="status" :class="statusColor(status)" class="px-2 py-0.5 rounded-full">
            {{ status }}：{{ count }}
          </span>
        </div>
      </router-link>
    </div>

    <!-- 自分のタスク -->
    <h2 class="text-sm font-semibold text-gray-600 mb-3">自分のタスク</h2>
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full text-sm" data-testid="my-tasks-table">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">タスク名</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">プロジェクト</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">ステータス</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">進捗</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">終了日</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="task in myTasks"
            :key="task.id"
            data-testid="my-task-row"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3">
              <router-link
                :to="`/projects/${task.project_id}/tasks/${task.id}`"
                class="text-blue-600 hover:underline font-medium"
              >
                {{ task.title }}
              </router-link>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ task.project_name }}</td>
            <td class="px-4 py-3">
              <span :class="statusColor(task.status)" class="px-2 py-0.5 rounded-full text-xs">
                {{ task.status }}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-20 bg-gray-200 rounded-full h-1.5">
                  <div class="bg-blue-500 h-1.5 rounded-full" :style="{ width: `${task.progress}%` }" />
                </div>
                <span class="text-xs text-gray-500">{{ task.progress }}%</span>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ task.end_date ?? '未設定' }}</td>
          </tr>
          <tr v-if="myTasks.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">担当タスクはありません</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
