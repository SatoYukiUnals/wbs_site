<script setup lang="ts">
// 04-02-04 タスク自動割り振り（日付スケジューラ）画面
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import type {
  AutoAssignPreview, ProjectMember, Project, Task, UserPto,
} from '@/types'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId as string

const isLoading = ref(true)
const isPreviewing = ref(false)
const isConfirming = ref(false)

const project = ref<Project | null>(null)
const members = ref<ProjectMember[]>([])
const items = ref<Task[]>([])  // 全 task_type='item' のフラットリスト

const dailyHours = ref<number>(8)
const ptos = ref<UserPto[]>([])
const previewResult = ref<AutoAssignPreview | null>(null)

// PTO 入力用
const ptoForm = reactive({ user_id: '', date: '' })

// プロジェクトのフラット項目を再帰的に集める
const flattenItems = (tasks: Task[]): Task[] => {
  const out: Task[] = []
  const walk = (list: Task[]) => {
    for (const t of list) {
      if (t.task_type === 'item') out.push(t)
      if (t.children?.length) walk(t.children)
    }
  }
  walk(tasks)
  return out
}

const fetchAll = async () => {
  isLoading.value = true
  const [p, m, ts, wh, ptoList] = await Promise.all([
    api.projects.get(projectId),
    api.projects.listMembers(projectId),
    api.tasks.list(projectId),
    api.workingHour.get(projectId),
    api.pto.list(projectId),
  ])
  project.value = p
  members.value = m
  items.value = flattenItems(ts).sort((a, b) =>
    a.wbs_no.localeCompare(b.wbs_no, undefined, { numeric: true }),
  )
  dailyHours.value = wh.daily_hours
  ptos.value = ptoList
  isLoading.value = false
}

onMounted(fetchAll)

// 稼働時間を保存
const saveDailyHours = async () => {
  await api.workingHour.update(projectId, dailyHours.value)
}

// PJ レビュー者を保存
const savePjReviewer = async (userId: string) => {
  if (!project.value) return
  const updated = await api.projects.update(projectId, {
    pj_reviewer: userId || null,
  })
  project.value = updated
}

// 項目ごとの TM レビュー者を保存
const saveTmReviewer = async (item: Task, userId: string) => {
  await api.tasks.update(projectId, item.id, {
    tm_reviewer: userId || null,
  })
  // 反映
  item.tm_reviewer = userId
    ? { id: userId, name: members.value.find(m => m.user_id === userId)?.user_name ?? '' }
    : null
}

// PTO 追加
const addPto = async () => {
  if (!ptoForm.user_id || !ptoForm.date) return
  const created = await api.pto.add(projectId, ptoForm.user_id, ptoForm.date)
  ptos.value.push(created)
  ptoForm.date = ''
}

// PTO 削除
const removePto = async (p: UserPto) => {
  await api.pto.remove(projectId, p.user_id, p.date)
  ptos.value = ptos.value.filter(x => x.id !== p.id)
}

// プレビュー
const handlePreview = async () => {
  isPreviewing.value = true
  try {
    previewResult.value = await api.autoAssign.preview(projectId)
  } finally {
    isPreviewing.value = false
  }
}

// 確定
const handleConfirm = async () => {
  isConfirming.value = true
  try {
    const res = await api.autoAssign.confirm(projectId)
    if (res.errors && res.errors.length > 0) {
      alert(res.detail ?? '担当者またはレビュー者が未設定のタスクがあります。')
      return
    }
    router.push(`/projects/${projectId}/wbs`)
  } finally {
    isConfirming.value = false
  }
}

// 表示用: 担当者ごとに PTO をグループ化
const ptosByUser = computed(() => {
  const map = new Map<string, UserPto[]>()
  for (const p of ptos.value) {
    const arr = map.get(p.user_id) ?? []
    arr.push(p)
    map.set(p.user_id, arr)
  }
  for (const arr of map.values()) {
    arr.sort((a, b) => a.date.localeCompare(b.date))
  }
  return map
})

const memberNameById = (id: string): string =>
  members.value.find(m => m.user_id === id)?.user_name ?? id
</script>

<template>
  <div id="auto_assign__container" class="max-w-4xl">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}/wbs`" class="text-blue-600 hover:underline text-sm">
        ← WBS
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">タスク自動割り振り（日付）</h1>
    </div>

    <div v-if="isLoading" class="text-gray-500 py-8 text-center">読み込み中...</div>

    <template v-else>
      <!-- ① 1日あたりの稼働時間 -->
      <section class="bg-white rounded-lg shadow p-5 mb-4">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">① 1日あたりの稼働時間</h2>
        <div class="flex items-center gap-2">
          <input
            v-model.number="dailyHours"
            type="number" min="0.5" step="0.5"
            class="w-24 border border-gray-300 rounded px-3 py-2 text-sm"
          />
          <span class="text-sm text-gray-700">時間／日</span>
          <button
            class="ml-auto bg-gray-700 text-white px-3 py-1.5 rounded text-sm hover:bg-gray-800"
            @click="saveDailyHours"
          >
            保存
          </button>
        </div>
      </section>

      <!-- ② PJレビュー者（プロジェクト単位） -->
      <section class="bg-white rounded-lg shadow p-5 mb-4">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">② PJレビュー者（プロジェクト単位）</h2>
        <select
          :value="project?.pj_reviewer_id ?? ''"
          class="border border-gray-300 rounded px-3 py-2 text-sm w-64"
          @change="savePjReviewer(($event.target as HTMLSelectElement).value)"
        >
          <option value="">未設定</option>
          <option v-for="m in members" :key="m.user_id" :value="m.user_id">
            {{ m.user_name }}
          </option>
        </select>
        <p class="text-xs text-gray-500 mt-1">
          タスク分類が「PJRV」のタスクは、このユーザーの予定にスケジュールされます。
        </p>
      </section>

      <!-- ③ 項目ごとの TMレビュー者 -->
      <section class="bg-white rounded-lg shadow p-5 mb-4 max-h-80">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">③ 項目ごとの TMレビュー者</h2>
        <p v-if="items.length === 0" class="text-sm text-gray-500">
          項目（task_type='item'）がまだありません。
        </p>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="text-left px-3 py-2 text-gray-600 font-medium w-24">WBS</th>
              <th class="text-left px-3 py-2 text-gray-600 font-medium">項目</th>
              <th class="text-left px-3 py-2 text-gray-600 font-medium w-56">TMレビュー者</th>
            </tr>
          </thead>
          <tbody class="max-40 overflow-y-auto">
            <tr v-for="item in items" :key="item.id" class="border-b last:border-0">
              <td class="px-3 py-2 text-sky-900">{{ item.wbs_no }}</td>
              <td class="px-3 py-2 text-sky-900" :style="{ paddingLeft: `${12 + item.depth * 16}px` }">
                {{ item.title }}
              </td>
              <td class="px-3 py-2">
                <select
                  :value="item.tm_reviewer?.id ?? ''"
                  class="border border-gray-300 rounded px-2 py-1 text-sm w-full"
                  @change="saveTmReviewer(item, ($event.target as HTMLSelectElement).value)"
                >
                  <option value="">未設定</option>
                  <option v-for="m in members" :key="m.user_id" :value="m.user_id">
                    {{ m.user_name }}
                  </option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- ④ ユーザーごとの有休 -->
      <section class="bg-white rounded-lg shadow p-5 mb-4">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">④ ユーザーごとの有休</h2>
        <div class="flex items-center gap-2 mb-3">
          <select v-model="ptoForm.user_id" class="border border-gray-300 rounded px-3 py-2 text-sm">
            <option value="">ユーザー選択</option>
            <option v-for="m in members" :key="m.user_id" :value="m.user_id">
              {{ m.user_name }}
            </option>
          </select>
          <input v-model="ptoForm.date" type="date" class="border border-gray-300 rounded px-3 py-2 text-sm" />
          <button
            :disabled="!ptoForm.user_id || !ptoForm.date"
            class="bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            @click="addPto"
          >
            追加
          </button>
        </div>
        <div v-if="ptos.length === 0" class="text-xs text-gray-500">
          有休はまだ登録されていません。
        </div>
        <div v-else class="space-y-2">
          <div v-for="[uid, list] in ptosByUser" :key="uid" class="border-t pt-2 first:border-t-0 first:pt-0">
            <div class="text-xs font-semibold text-sky-900 mb-1">{{ memberNameById(uid) }}</div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="p in list" :key="p.id"
                class="bg-amber-50 text-amber-800 text-xs px-2 py-0.5 rounded-full inline-flex items-center gap-1"
              >
                {{ p.date }}
                <button class="hover:text-red-600" @click="removePto(p)">×</button>
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- ⑤ プレビュー -->
      <section class="bg-white rounded-lg shadow p-5 mb-4">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-700">⑤ プレビュー</h2>
          <button
            id="auto_assign__preview_btn"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            :disabled="isPreviewing"
            @click="handlePreview"
          >
            {{ isPreviewing ? '計算中...' : 'プレビューを取得' }}
          </button>
        </div>

        <div v-if="previewResult">
          <!-- エラー一覧 -->
          <div v-if="previewResult.errors.length > 0" class="bg-red-50 border border-red-200 rounded p-3 mb-3">
            <p class="text-sm font-semibold text-red-700 mb-2">
              ⚠ 担当者またはレビュー者が未設定のタスクがあります（{{ previewResult.errors.length }}件）。
            </p>
            <ul class="text-xs text-red-700 space-y-1 list-disc pl-5">
              <li v-for="e in previewResult.errors" :key="e.task_id">
                {{ e.wbs_no }} {{ e.task_title }}（{{ e.task_kind || '分類未設定' }}）— {{ e.detail }}
              </li>
            </ul>
          </div>

          <!-- スケジュール表 -->
          <table v-if="previewResult.schedule.length > 0" class="w-full text-sm">
            <thead class="bg-gray-50 border-b">
              <tr>
                <th class="text-left px-3 py-2 text-gray-600 font-medium w-20">WBS</th>
                <th class="text-left px-3 py-2 text-gray-600 font-medium">タスク</th>
                <th class="text-left px-3 py-2 text-gray-600 font-medium w-24">分類</th>
                <th class="text-left px-3 py-2 text-gray-600 font-medium w-32">担当</th>
                <th class="text-left px-3 py-2 text-gray-600 font-medium w-28">開始日</th>
                <th class="text-left px-3 py-2 text-gray-600 font-medium w-28">終了日</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="r in previewResult.schedule"
                :key="r.task_id"
                :class="r.is_skipped ? 'bg-gray-50 text-gray-500' : ''"
                class="border-b last:border-0"
              >
                <td class="px-3 py-2">{{ r.wbs_no }}</td>
                <td class="px-3 py-2">
                  {{ r.task_title }}
                  <span v-if="r.is_skipped" class="text-xs text-amber-600 ml-2">（{{ r.reason }}）</span>
                </td>
                <td class="px-3 py-2 text-xs">{{ r.task_kind || '—' }}</td>
                <td class="px-3 py-2 text-xs">{{ r.user_name || '—' }}</td>
                <td class="px-3 py-2 text-xs">{{ r.start_date ?? '—' }}</td>
                <td class="px-3 py-2 text-xs">{{ r.end_date ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 確定ボタン -->
      <div v-if="previewResult" class="flex justify-end gap-2">
        <router-link
          :to="`/projects/${projectId}/wbs`"
          class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
        >
          キャンセル
        </router-link>
        <button
          id="auto_assign__confirm_btn"
          :disabled="isConfirming || previewResult.errors.length > 0"
          class="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50"
          @click="handleConfirm"
        >
          {{ isConfirming ? '処理中...' : 'この内容で確定する' }}
        </button>
      </div>
    </template>
  </div>
</template>
