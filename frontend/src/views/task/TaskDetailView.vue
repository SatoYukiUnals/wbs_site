<script setup lang="ts">
// 04-01-03 タスク詳細・編集画面
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import type {
  Task, Quarter, TaskStatus, TaskKind, TaskType, ProjectMember,
} from '@/types'

const route = useRoute()
const router = useRouter()
const taskId = route.params.taskId as string
const projectId = route.params.projectId as string

const task = ref<Task | null>(null)
const quarters = ref<Quarter[]>([])
const members = ref<ProjectMember[]>([])
const isLoading = ref(true)

const form = reactive({
  title: '',
  task_type: 'task' as TaskType,
  description: '',
  status: 'Todo' as TaskStatus,
  progress: 0,
  start_date: '',
  end_date: '',
  estimated_hours: '' as string | number,
  quarter_id: '',
  task_kind: null as TaskKind | null,
  tm_reviewer_id: '' as string,
})

// 初期値を保持しておき、保存時に「日付が手動編集されたか」を判定する
const initialDates = { start: '', end: '' }

onMounted(async () => {
  const [t, q, m] = await Promise.all([
    api.tasks.get(projectId, taskId),
    api.quarters.list(projectId),
    api.projects.listMembers(projectId),
  ])
  task.value = t
  quarters.value = q
  members.value = m
  form.title = t.title
  form.task_type = t.task_type
  form.description = t.description
  form.status = t.status
  form.progress = t.progress
  form.start_date = t.start_date ?? ''
  form.end_date = t.end_date ?? ''
  form.estimated_hours = t.estimated_hours ?? ''
  form.quarter_id = t.quarter_id ?? ''
  form.task_kind = t.task_kind
  form.tm_reviewer_id = t.tm_reviewer?.id ?? ''
  initialDates.start = form.start_date
  initialDates.end = form.end_date
  isLoading.value = false
})

const errors = reactive({ title: '' })

const validate = (): boolean => {
  errors.title = form.title.trim() ? '' : 'タスク名は必須です'
  return !errors.title
}

/** 保存処理 */
const handleSubmit = async () => {
  if (!validate()) return
  isLoading.value = true
  try {
    // 親項目（item）の場合はタイトル・説明・種別・TMレビュー者のみ保存し
    // その他のフィールドは null クリアする
    if (form.task_type === 'item') {
      const payload: Record<string, unknown> = {
        title: form.title,
        task_type: form.task_type,
        description: form.description,
        start_date: null,
        end_date: null,
        estimated_hours: null,
        quarter: null,
        task_kind: null,
        tm_reviewer: form.tm_reviewer_id || null,
        dates_manual: false,
      }
      await api.tasks.update(projectId, taskId, payload)
    } else {
      // タスクの場合: 日付が初期値から変わっていれば dates_manual=true
      const datesChanged =
        form.start_date !== initialDates.start ||
        form.end_date !== initialDates.end
      const payload: Record<string, unknown> = {
        title: form.title,
        task_type: form.task_type,
        description: form.description,
        status: form.status,
        progress: form.progress,
        start_date: form.start_date || null,
        end_date: form.end_date || null,
        estimated_hours: form.estimated_hours || null,
        quarter: form.quarter_id || null,
        task_kind: form.task_kind,
      }
      if (datesChanged) {
        // 日付欄を完全にクリアした場合は手動フラグも解除
        payload.dates_manual = !!(form.start_date || form.end_date)
      }
      await api.tasks.update(projectId, taskId, payload)
    }
    router.push(`/projects/${projectId}/wbs`)
  } finally {
    isLoading.value = false
  }
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
    {{ isLoading ? '読み込み中...' : 'タスクが見つかりません' }}
  </div>

  <div v-else id="task_detail__container" class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}/wbs`" class="text-blue-600 hover:underline text-sm">
        ← WBS
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">タスク詳細</h1>
      <span
        v-if="form.task_type === 'task'"
        :class="statusColor(form.status)"
        class="px-2 py-0.5 rounded-full text-xs ml-auto"
      >
        {{ form.status }}
      </span>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <form id="task_detail__form" @submit.prevent="handleSubmit" class="space-y-4">
        <!-- タスク名 -->
        <div>
          <label for="task_detail__title_input" class="block text-sm font-medium text-gray-700 mb-1">タスク名 <span class="text-red-500">*</span></label>
          <input
            id="task_detail__title_input"
            v-model="form.title"
            type="text"
            data-testid="task-title-input"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p v-if="errors.title" class="text-red-500 text-xs mt-1">{{ errors.title }}</p>
        </div>

        <!-- 説明（タスク／親項目どちらでも編集可能） -->
        <div>
          <label for="task_detail__description_textarea" class="block text-sm font-medium text-gray-700 mb-1">説明</label>
          <textarea
            id="task_detail__description_textarea"
            v-model="form.description"
            rows="3"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- TMレビュー者（item の場合のみ） -->
        <div v-if="form.task_type === 'item'">
          <label for="task_detail__tm_reviewer_select" class="block text-sm font-medium text-gray-700 mb-1">TMレビュー者</label>
          <select
            id="task_detail__tm_reviewer_select"
            v-model="form.tm_reviewer_id"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
          >
            <option value="">未設定</option>
            <option v-for="m in members" :key="m.user_id" :value="m.user_id">
              {{ m.user_name }}
            </option>
          </select>
          <p class="text-xs text-gray-500 mt-1">
            この項目配下の TMRV タスクは、このレビュー者の予定にスケジュールされます。
          </p>
        </div>

        <!-- item の場合は以下の入力欄をすべて非表示にする -->
        <template v-if="form.task_type === 'task'">
        <!-- ステータス -->
        <div>
          <label for="task_detail__status_select" class="block text-sm font-medium text-gray-700 mb-1">ステータス</label>
          <select
            id="task_detail__status_select"
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

        <!-- タスク分類 -->
        <div>
          <label for="task_detail__task_kind_select" class="block text-sm font-medium text-gray-700 mb-1">タスク分類</label>
          <select id="task_detail__task_kind_select" v-model="form.task_kind" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
            <option :value="null">未設定</option>
            <option value="実装">実装</option>
            <option value="TMRV">TMRV</option>
            <option value="PJRV">PJRV</option>
            <option value="レビュー修正">レビュー修正</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">
            TMRV/PJRV はそれぞれ親項目のTMレビュー者／プロジェクトのPJレビュー者にスケジュールされます。
          </p>
        </div>

        <!-- 開始日・終了日 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="task_detail__start_date_input" class="block text-sm font-medium text-gray-700 mb-1">開始日</label>
            <input id="task_detail__start_date_input" v-model="form.start_date" type="date" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label for="task_detail__end_date_input" class="block text-sm font-medium text-gray-700 mb-1">終了日</label>
            <input id="task_detail__end_date_input" v-model="form.end_date" type="date" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
          </div>
        </div>

        <!-- 見積時間・クォーター -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="task_detail__estimated_hours_input" class="block text-sm font-medium text-gray-700 mb-1">見積時間（h）</label>
            <input
              id="task_detail__estimated_hours_input"
              v-model.number="form.estimated_hours"
              type="number"
              min="0"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label for="task_detail__quarter_select" class="block text-sm font-medium text-gray-700 mb-1">クォーター</label>
            <select id="task_detail__quarter_select" v-model="form.quarter_id" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
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
        </template>

        <div class="flex gap-2 pt-2">
          <button
            id="task_detail__save_btn"
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
