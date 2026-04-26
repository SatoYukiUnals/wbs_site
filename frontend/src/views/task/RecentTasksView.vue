<script setup lang="ts">
// 04-XX 直近タスク一覧（期限切れ・今週開始予定・着手中の未完了タスク）
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import type { Task, TaskStatus, ProjectMember } from '@/types'

const route = useRoute()
const projectId = route.params.projectId as string

/** バックエンドの recent エンドポイントから取得したタスク（フラット） */
const allTasks = ref<Task[]>([])

onMounted(async () => {
  const result = await api.recent.get(projectId)
  const members_resp = await api.projects.listMembers(projectId)
  members.value = members_resp
  allTasks.value = [
    ...result.overdue,
    ...result.starting_soon,
    ...result.in_progress,
  ]
})

/** 今日・1週間後 */
const today = new Date()
today.setHours(0, 0, 0, 0)
const oneWeekLater = new Date(today)
oneWeekLater.setDate(today.getDate() + 7)

/** 抽出理由 */
type Reason = 'overdue' | 'starting_soon' | 'in_progress'

type RecentTask = {
  task: Task
  reason: Reason
}

/** 前提条件チェック（start_date・end_date両方あり、実績終了なし、未完了） */
const isEligible = (t: Task): boolean => {
  if (!t.start_date || !t.end_date) return false
  if (t.actual_end_date !== null) return false
  if (t.status === 'Done') return false
  return true
}

/** 抽出理由を返す（いずれにも該当しなければ null） */
const getReason = (t: Task): Reason | null => {
  if (!isEligible(t)) return null
  const endDate = new Date(t.end_date!)
  const startDate = new Date(t.start_date!)
  if (endDate <= today) return 'overdue'
  if (startDate >= today && startDate <= oneWeekLater) return 'starting_soon'
  if (t.actual_start_date !== null) return 'in_progress'
  return null
}

/** フィルタ */
const filterStatus = ref<TaskStatus | ''>('')
const filterAssigneeId = ref('')

/** グループごとの折り畳み状態 */
const collapsed = ref<Record<Reason, boolean>>({
  overdue: false,
  starting_soon: false,
  in_progress: false,
})

const toggleCollapse = (reason: Reason) => {
  collapsed.value[reason] = !collapsed.value[reason]
}

/** 抽出・フィルタ・ソート済みタスク */
const recentTasks = computed<RecentTask[]>(() => {
  return allTasks.value
    .filter(t => {
      const reason = getReason(t)
      if (!reason) return false
      if (filterStatus.value && t.status !== filterStatus.value) return false
      if (filterAssigneeId.value && !t.assignees.some(a => a.id === filterAssigneeId.value)) return false
      return true
    })
    .map(t => ({ task: t, reason: getReason(t)! }))
    .sort((a, b) => {
      const endCmp = (a.task.end_date ?? '').localeCompare(b.task.end_date ?? '')
      if (endCmp !== 0) return endCmp
      return (a.task.actual_start_date ?? '').localeCompare(b.task.actual_start_date ?? '')
    })
})

/** グループ別に分類 */
const grouped = computed<Record<Reason, RecentTask[]>>(() => ({
  overdue:       recentTasks.value.filter(r => r.reason === 'overdue'),
  starting_soon: recentTasks.value.filter(r => r.reason === 'starting_soon'),
  in_progress:   recentTasks.value.filter(r => r.reason === 'in_progress'),
}))

/** グループ定義 */
const groups: { reason: Reason; label: string; badgeClass: string }[] = [
  { reason: 'overdue',       label: '期限切れ',     badgeClass: 'bg-red-100 text-red-700' },
  { reason: 'starting_soon', label: '今週開始予定',  badgeClass: 'bg-amber-100 text-amber-700' },
  { reason: 'in_progress',   label: '着手中',        badgeClass: 'bg-blue-100 text-blue-700' },
]

const members = ref<ProjectMember[]>([])

const statusOptions: { value: TaskStatus | ''; label: string }[] = [
  { value: '', label: 'すべて' },
  { value: 'Todo',       label: 'Todo' },
  { value: 'InProgress', label: 'InProgress' },
  { value: 'InReview',   label: 'InReview' },
  { value: 'OnHold',     label: 'OnHold' },
]

const statusClass = (status: string): string => {
  const map: Record<string, string> = {
    'Todo':       'bg-green-100 text-green-700',
    'InProgress': 'bg-yellow-100 text-yellow-700',
    'InReview':   'bg-red-100 text-red-700',
    'Done':       'bg-purple-100 text-purple-700',
    'OnHold':     'bg-gray-100 text-gray-600',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}

const formatDate = (d: string | null) => d ? d.replace(/-/g, '/') : '—'
</script>

<template>
  <div id="recent_tasks__container">
    <h1 class="text-xl font-bold text-sky-900 mb-4">直近のタスク</h1>

    <!-- フィルタ -->
    <div id="recent_tasks__filter_area" class="bg-white rounded-lg shadow px-4 py-3 mb-4 flex flex-wrap gap-4 items-end">
      <div>
        <label class="block text-xs text-sky-900 mb-1">ステータス</label>
        <select
          id="recent_tasks__status_select"
          v-model="filterStatus"
          class="border border-gray-300 rounded px-2 py-1 text-sm text-sky-900"
        >
          <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
      </div>
      <div>
        <label class="block text-xs text-sky-900 mb-1">担当者</label>
        <select
          id="recent_tasks__assignee_select"
          v-model="filterAssigneeId"
          class="border border-gray-300 rounded px-2 py-1 text-sm text-sky-900"
        >
          <option value="">すべて</option>
          <option v-for="m in members" :key="m.user_id" :value="m.user_id">{{ m.user_name }}</option>
        </select>
      </div>
      <div class="ml-auto text-sm text-sky-900">
        {{ recentTasks.length }} 件
      </div>
    </div>

    <!-- グループ別テーブル -->
    <div v-for="g in groups" :key="g.reason" class="mb-4">

      <!-- グループヘッダー -->
      <button
        :id="`recent_tasks__group_btn_${g.reason}`"
        class="w-full flex items-center gap-2 px-4 py-2 bg-white rounded-t-lg border border-gray-500 hover:bg-gray-50 transition-colors"
        @click="toggleCollapse(g.reason)"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-4 h-4 text-sky-900 flex-shrink-0 transition-transform"
          :class="collapsed[g.reason] ? '-rotate-90' : ''"
          viewBox="0 0 20 20" fill="currentColor"
        >
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
        </svg>
        <span :class="g.badgeClass" class="px-2 py-0.5 rounded text-xs font-medium">{{ g.label }}</span>
        <span class="text-sm text-sky-900">{{ grouped[g.reason].length }} 件</span>
      </button>

      <!-- テーブル -->
      <div v-if="!collapsed[g.reason]" class="bg-white rounded-b-lg overflow-x-auto border-x border-b border-gray-500">
        <div v-if="grouped[g.reason].length === 0" class="px-4 py-6 text-center text-sm text-gray-400">
          該当タスクなし
        </div>
        <table v-else class="w-full text-sm border-separate border-spacing-0">
          <thead>
            <tr class="bg-gray-50">
              <th class="border-b border-r border-gray-500 px-3 py-2 text-left text-xs font-medium text-sky-900 whitespace-nowrap">WBS No</th>
              <th class="border-b border-r border-gray-500 px-3 py-2 text-left text-xs font-medium text-sky-900">タイトル</th>
              <th class="border-b border-r border-gray-500 px-3 py-2 text-left text-xs font-medium text-sky-900 whitespace-nowrap">ステータス</th>
              <th class="border-b border-r border-gray-500 px-3 py-2 text-left text-xs font-medium text-sky-900 whitespace-nowrap">担当者</th>
              <th class="border-b border-r border-gray-500 px-3 py-2 text-left text-xs font-medium text-sky-900 whitespace-nowrap">予定開始日</th>
              <th class="border-b border-r border-gray-500 px-3 py-2 text-left text-xs font-medium text-sky-900 whitespace-nowrap">予定終了日</th>
              <th class="border-b border-gray-500 px-3 py-2 text-left text-xs font-medium text-sky-900 whitespace-nowrap">実績開始日</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="{ task } in grouped[g.reason]"
              :key="task.id"
              :id="`recent_tasks__row_${task.id}`"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="border-b border-r border-gray-500 px-3 py-2 text-xs text-sky-900 whitespace-nowrap">{{ task.wbs_no }}</td>
              <td class="border-b border-r border-gray-500 px-3 py-2 text-sky-900">
                <router-link
                  :to="`/projects/${projectId}/tasks/${task.id}`"
                  class="hover:underline hover:text-blue-600"
                >
                  {{ task.title }}
                </router-link>
              </td>
              <td class="border-b border-r border-gray-500 px-3 py-2 whitespace-nowrap">
                <span :class="statusClass(task.status)" class="px-2 py-0.5 rounded-full text-xs">{{ task.status }}</span>
              </td>
              <td class="border-b border-r border-gray-500 px-3 py-2 text-xs text-sky-900 whitespace-nowrap">
                {{ task.assignees.map(a => a.name).join(', ') || '—' }}
              </td>
              <td class="border-b border-r border-gray-500 px-3 py-2 text-xs text-sky-900 whitespace-nowrap">{{ formatDate(task.start_date) }}</td>
              <td
                class="border-b border-r border-gray-500 px-3 py-2 text-xs whitespace-nowrap"
                :class="g.reason === 'overdue' ? 'text-red-600 font-medium' : 'text-sky-900'"
              >
                {{ formatDate(task.end_date) }}
              </td>
              <td class="border-b border-gray-500 px-3 py-2 text-xs text-sky-900 whitespace-nowrap">{{ formatDate(task.actual_start_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>
