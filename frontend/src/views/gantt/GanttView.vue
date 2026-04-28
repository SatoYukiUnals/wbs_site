<script setup lang="ts">
// 05-01-00 ガントチャート画面
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import type { Task, ViewUnit } from '@/types'

const route = useRoute()
const projectId = route.params.projectId as string

const viewUnit = ref<ViewUnit>('month')

/** プロジェクト内のルートタスク一覧 */
const tasks = ref<Task[]>([])

onMounted(async () => {
  tasks.value = await api.tasks.list(projectId)
})

/** 表示期間（2026-04〜2026-12） */
const months = ['4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

/** タスクバーの開始列・幅をmonth単位で計算 */
const getBarStyle = (task: Task) => {
  if (!task.start_date || !task.end_date) return null
  const start = new Date(task.start_date)
  const end = new Date(task.end_date)
  // 基準: 2026-04-01 を列0とする
  const baseDate = new Date('2026-04-01')
  const totalDays = 273 // 9ヶ月分の近似

  const startOffset = Math.max(0, (start.getTime() - baseDate.getTime()) / (1000 * 60 * 60 * 24))
  const duration = Math.max(1, (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))

  const left = (startOffset / totalDays) * 100
  const width = (duration / totalDays) * 100
  return { left: `${Math.min(left, 95)}%`, width: `${Math.min(width, 100 - left)}%` }
}

/** メンバーカラーパレット（予定バー用） */
const BAR_COLORS_500 = ['bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-amber-500', 'bg-rose-500', 'bg-cyan-500', 'bg-indigo-500', 'bg-teal-500']

import type { ProjectMember } from '@/types'
const members = ref<ProjectMember[]>([])
onMounted(async () => {
  members.value = await api.projects.listMembers(projectId)
})

const memberColorIdx = (userId: string): number => {
  const idx = members.value.findIndex(m => m.user_id === userId)
  return idx >= 0 ? idx % BAR_COLORS_500.length : BAR_COLORS_500.length - 1
}

const barColor = (task: Task): string => {
  const uid = task.assignees[0]?.id
  return uid ? BAR_COLORS_500[memberColorIdx(uid)] : 'bg-gray-500'
}

/** 実績バーのスタイル（actual_start_date が設定されている場合） */
const getActualBarStyle = (task: Task) => {
  if (!task.actual_start_date) return null
  const start = new Date(task.actual_start_date)
  const end = task.actual_end_date ? new Date(task.actual_end_date) : new Date()
  const baseDate = new Date('2026-04-01')
  const totalDays = 273

  const startOffset = Math.max(0, (start.getTime() - baseDate.getTime()) / (1000 * 60 * 60 * 24))
  const duration = Math.max(1, (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))

  const left = (startOffset / totalDays) * 100
  const width = (duration / totalDays) * 100
  return { left: `${Math.min(left, 95)}%`, width: `${Math.min(width, 100 - left)}%` }
}
</script>

<template>
  <div id="gantt__container">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">ガントチャート</h1>
    </div>

    <!-- ツールバー -->
    <div id="gantt__toolbar" class="flex items-center gap-3 mb-4">
      <div class="flex border rounded overflow-hidden text-sm">
        <button
          id="gantt__month_btn"
          :class="viewUnit === 'month' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
          class="px-3 py-1.5"
          @click="viewUnit = 'month'"
        >月</button>
        <button
          id="gantt__week_btn"
          :class="viewUnit === 'week' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
          class="px-3 py-1.5 border-l"
          @click="viewUnit = 'week'"
        >週</button>
        <button
          id="gantt__quarter_btn"
          :class="viewUnit === 'quarter' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
          class="px-3 py-1.5 border-l"
          @click="viewUnit = 'quarter'"
        >クォーター</button>
      </div>
      <div class="flex items-center gap-3 text-xs text-gray-500 ml-4">
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 bg-blue-500 rounded"></span>予定</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 bg-green-400 opacity-70 rounded"></span>実績</span>
      </div>
    </div>

    <!-- ガントチャート本体 -->
    <div id="gantt__chart_area" class="bg-white rounded-lg shadow overflow-x-auto overflow-y-auto max-h-[calc(100vh-220px)]">
      <div class="min-w-[900px]">
        <!-- ヘッダー（月ラベル） -->
        <div class="flex border-b border-gray-500 sticky top-0 z-20 bg-gray-50">
          <div class="w-56 flex-shrink-0 px-4 py-2 text-sm font-medium text-gray-600 bg-gray-50 border-r border-gray-500 sticky left-0 z-30">
            タスク名
          </div>
          <div class="flex flex-1">
            <div
              v-for="month in months"
              :key="month"
              class="flex-1 text-center text-xs text-gray-500 py-2 border-r border-gray-500 last:border-0 bg-gray-50"
            >
              {{ month }}
            </div>
          </div>
        </div>

        <!-- タスク行 -->
        <div
          v-for="task in tasks"
          :key="task.id"
          :id="`gantt__row_${task.id}`"
          data-testid="gantt-row"
          class="flex border-b border-gray-500 last:border-0 hover:bg-gray-50/50"
        >
          <!-- タスク名カラム -->
          <div class="w-56 flex-shrink-0 px-4 py-3 border-r border-b border-gray-500 sticky left-0 z-10 bg-white">
            <router-link :to="`/projects/${projectId}/tasks/${task.id}`" class="text-sm text-blue-600 hover:underline truncate block">
              {{ task.wbs_no }}. {{ task.title }}
            </router-link>
          </div>

          <!-- バー領域 -->
          <div class="flex-1 relative py-3 px-0 min-h-12 border-b border-gray-500">
            <!-- 月区切り線 -->
            <div class="absolute inset-0 flex pointer-events-none">
              <div v-for="(_, i) in months" :key="i" class="flex-1 border-r last:border-0 border-gray-500"></div>
            </div>

            <!-- 予定バー -->
            <div
              v-if="getBarStyle(task)"
              :style="getBarStyle(task)!"
              :class="barColor(task)"
              class="absolute top-2 h-5 rounded opacity-80 transition-all"
            >
              <span class="text-white text-xs px-1 truncate leading-5 block">{{ task.status }}</span>
            </div>

            <!-- 実績バー -->
            <div
              v-if="getActualBarStyle(task)"
              :style="getActualBarStyle(task)!"
              class="absolute bottom-2 h-2 bg-green-400 rounded opacity-60"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
