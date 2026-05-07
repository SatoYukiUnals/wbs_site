<script setup lang="ts">
// 04-01-04 WBS編集画面（フラット一覧・選択行への一括適用）
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import type {
  Task, ProjectMember, Quarter, TaskKind, TaskStatus,
} from '@/types'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId as string

const isLoading = ref(true)
const isSaving = ref(false)

const allTasks = ref<Task[]>([])
const members = ref<ProjectMember[]>([])
const quarters = ref<Quarter[]>([])

// 行ごとの編集ドラフト（空のうちは未編集とみなす）
type Draft = {
  start_date: string | null
  end_date: string | null
  estimated_hours: number | null
  assigneeIds: string[]
  task_kind: TaskKind | null
  quarter_id: string | null
}
const drafts = reactive(new Map<string, Draft>())

const initDraft = (t: Task): Draft => ({
  start_date: t.start_date,
  end_date: t.end_date,
  estimated_hours: t.estimated_hours,
  assigneeIds: t.assignees.map(a => a.id),
  task_kind: t.task_kind,
  quarter_id: t.quarter_id,
})

const draftFor = (t: Task): Draft => {
  // Vue の reactive Map では .get() の戻り値が reactive proxy にラップされる。
  // 新規作成時に initDraft の生オブジェクトをそのまま返すと proxy 経由でないため
  // ミューテーション（特に一括適用での代入）がリアクティブに反映されない。
  // よって作成後も必ず drafts.get() で取り直す。
  if (!drafts.has(t.id)) {
    drafts.set(t.id, initDraft(t))
  }
  return drafts.get(t.id)!
}

// =====================================================================
// 絞り込み（クライアント側でフィルタ・ドラフト状態は保持）
// =====================================================================
// 各カテゴリは複数選択可。空集合 = 絞り込みなし。
// 未設定／未割り当てはセンチネル '__none__' として表現する。
const NONE = '__none__' as const
const filterStatuses = ref<Set<TaskStatus>>(new Set())
const filterKinds = ref<Set<TaskKind | typeof NONE>>(new Set())
const filterAssignees = ref<Set<string>>(new Set())  // user_id or '__none__'
const filterQuarters = ref<Set<string>>(new Set())   // quarter_id or '__none__'
// 工数未入力のみに絞り込むフラグ（true のとき estimated_hours が null の leaf のみ表示）
const filterHoursUnset = ref(false)
const filterText = ref<string>('')
// 親項目（item）の id。指定するとその配下のタスクのみ表示
const filterParentId = ref<string>('')

// 絞り込みダイアログの開閉
const showFilterDialog = ref(false)

// テンプレート内では ref が自動アンラップされるため、ref オブジェクトを
// 共通ヘルパーに渡す方式は使えない。各カテゴリ専用のトグル関数を用意する。
const toggleStatusFilter = (s: TaskStatus) => {
  const x = new Set(filterStatuses.value)
  if (x.has(s)) x.delete(s); else x.add(s)
  filterStatuses.value = x
}
const toggleKindFilter = (k: TaskKind | typeof NONE) => {
  const x = new Set(filterKinds.value)
  if (x.has(k)) x.delete(k); else x.add(k)
  filterKinds.value = x
}
const toggleAssigneeFilter = (id: string) => {
  const x = new Set(filterAssignees.value)
  if (x.has(id)) x.delete(id); else x.add(id)
  filterAssignees.value = x
}
const toggleQuarterFilter = (id: string) => {
  const x = new Set(filterQuarters.value)
  if (x.has(id)) x.delete(id); else x.add(id)
  filterQuarters.value = x
}

// 親項目（item）一覧。絞り込みダイアログのプルダウン用。
// 1階層目（depth 0）と 2階層目（depth 1）の item のみに限定する。
const itemTasks = computed<Task[]>(() =>
  allTasks.value.filter(t => t.task_type === 'item' && t.depth <= 1),
)

/** 指定した親項目の wbs_no を起点とする配下タスクのみを通すヘルパー */
const isUnderParent = (t: Task, parentWbs: string): boolean => {
  if (!parentWbs) return true
  return t.wbs_no === parentWbs ||
    t.wbs_no.startsWith(parentWbs + '.')
}

/** leaf タスク（task_type='task'）が絞り込み条件にマッチするか */
const leafFilterMatches = (t: Task): boolean => {
  if (filterStatuses.value.size > 0 &&
      !filterStatuses.value.has(t.status)) return false

  if (filterKinds.value.size > 0) {
    const ok = (t.task_kind && filterKinds.value.has(t.task_kind))
      || (!t.task_kind && filterKinds.value.has(NONE))
    if (!ok) return false
  }

  if (filterAssignees.value.size > 0) {
    const isUnassigned = t.assignees.length === 0
    const someMatch = t.assignees.some(a => filterAssignees.value.has(a.id))
    if (!(someMatch || (isUnassigned && filterAssignees.value.has(NONE)))) {
      return false
    }
  }

  if (filterQuarters.value.size > 0) {
    const ok = (t.quarter_id && filterQuarters.value.has(t.quarter_id))
      || (!t.quarter_id && filterQuarters.value.has(NONE))
    if (!ok) return false
  }

  if (filterText.value) {
    const q = filterText.value.toLowerCase()
    if (!t.title.toLowerCase().includes(q)) return false
  }

  // 工数未入力フィルター: ドラフトがあればそちらを優先して null 判定する
  if (filterHoursUnset.value) {
    const d = drafts.get(t.id)
    const hours = d ? d.estimated_hours : t.estimated_hours
    if (hours != null) return false
  }
  return true
}

const visibleTasks = computed<Task[]>(() => {
  // 親項目スコープの起点 wbs_no
  const parentWbs = filterParentId.value
    ? (allTasks.value.find(x => x.id === filterParentId.value)?.wbs_no ?? '')
    : ''

  // id → Task の検索マップ（祖先を辿るため）
  const byId = new Map<string, Task>()
  for (const t of allTasks.value) byId.set(t.id, t)

  // ステップ1: 表示対象の leaf タスクを抽出
  // 絞り込み条件は task_type='task' のみに適用する。
  // task_type='item' は条件評価対象から外し、配下の leaf があれば後で含める。
  const visibleSet = new Set<string>()
  for (const t of allTasks.value) {
    if (parentWbs && !isUnderParent(t, parentWbs)) continue
    if (t.task_type !== 'task') continue
    if (!leafFilterMatches(t)) continue
    visibleSet.add(t.id)

    // ステップ2: その祖先（item）を辿って表示対象に追加
    let cur: Task | undefined = t
    while (cur && cur.parent_task_id) {
      const parent = byId.get(cur.parent_task_id)
      if (!parent) break
      // スコープ外の祖先は含めない
      if (parentWbs && !isUnderParent(parent, parentWbs)) break
      visibleSet.add(parent.id)
      cur = parent
    }
  }

  return allTasks.value.filter(t => visibleSet.has(t.id))
})

const clearFilters = () => {
  filterStatuses.value = new Set()
  filterKinds.value = new Set()
  filterAssignees.value = new Set()
  filterQuarters.value = new Set()
  filterHoursUnset.value = false
  filterText.value = ''
  filterParentId.value = ''
}

// =====================================================================
// 列表示/非表示
// =====================================================================
type ColKey = 'task_kind' | 'assignees' | 'start_date'
  | 'end_date' | 'estimated_hours' | 'quarter_id'
const COL_DEFS: { key: ColKey; label: string }[] = [
  { key: 'task_kind',       label: '分類' },
  { key: 'assignees',       label: '担当者' },
  { key: 'start_date',      label: '開始日' },
  { key: 'end_date',        label: '終了日' },
  { key: 'estimated_hours', label: '見積(h)' },
  { key: 'quarter_id',      label: 'クォーター' },
]
const visibleCols = ref<Set<ColKey>>(new Set(COL_DEFS.map(d => d.key)))
const showColMenu = ref(false)
const showCol = (key: ColKey) => visibleCols.value.has(key)
const toggleCol = (key: ColKey) => {
  const s = new Set(visibleCols.value)
  if (s.has(key)) s.delete(key)
  else s.add(key)
  visibleCols.value = s
}

/** アクティブな絞り込み条件の数（トリガーボタンに表示） */
const activeFilterCount = computed(() => {
  let n = 0
  if (filterText.value) n++
  if (filterParentId.value) n++
  if (filterHoursUnset.value) n++
  n += filterStatuses.value.size
  n += filterKinds.value.size
  n += filterAssignees.value.size
  n += filterQuarters.value.size
  return n
})

// 選択状態
const selectedIds = ref(new Set<string>())

// その行の「チェック表示状態」: 親行ならサブツリー全選択時のみ checked
const isRowChecked = (t: Task): boolean => {
  const sub = subtreeOf(t)
  return sub.length > 0 && sub.every(x => selectedIds.value.has(x.id))
}

// 行クリック: 親なら配下を含めてサブツリー全体をトグルする
const toggleSelect = (t: Task) => {
  const subtree = subtreeOf(t)
  const s = new Set(selectedIds.value)
  if (subtree.every(x => s.has(x.id))) {
    for (const x of subtree) s.delete(x.id)
  } else {
    for (const x of subtree) s.add(x.id)
  }
  selectedIds.value = s
}

// 表示行に対しての全選択（フィルター状態を尊重する）
const allVisibleSelected = computed(() =>
  visibleTasks.value.length > 0 &&
  visibleTasks.value.every(t => selectedIds.value.has(t.id)),
)

const toggleSelectAll = () => {
  const s = new Set(selectedIds.value)
  if (allVisibleSelected.value) {
    for (const t of visibleTasks.value) s.delete(t.id)
  } else {
    for (const t of visibleTasks.value) s.add(t.id)
  }
  selectedIds.value = s
}

// 親子（サブツリー）単位の選択
// wbs_no のプレフィックス一致で descendants を判定する
const subtreeOf = (t: Task): Task[] => {
  const prefix = t.wbs_no + '.'
  return visibleTasks.value.filter(
    x => x.id === t.id || x.wbs_no.startsWith(prefix),
  )
}


// =====================================================================
// 一括適用
// =====================================================================
type BulkField =
  | 'start_date'
  | 'end_date'
  | 'estimated_hours'
  | 'assignees'
  | 'task_kind'
  | 'quarter_id'

const bulkField = ref<BulkField>('task_kind')
const bulkText = ref('')
const bulkAssignees = ref<string[]>([])
const bulkTaskKind = ref<TaskKind | null>(null)

// 適用対象は「選択中 ∩ 表示中 ∩ task（リーフ）」。
// 項目（item）は値を持たないので件数からも除外する。
const bulkTargets = computed<Task[]>(() =>
  visibleTasks.value.filter(t =>
    t.task_type === 'task' && selectedIds.value.has(t.id),
  ),
)

const applyBulk = () => {
  if (bulkTargets.value.length === 0) return
  for (const t of bulkTargets.value) {
    // 項目（item）には日付・工数・担当者・分類・クォーターを持たせない
    if (t.task_type === 'item') continue
    const d = draftFor(t)
    switch (bulkField.value) {
      case 'start_date':
        d.start_date = bulkText.value || null
        break
      case 'end_date':
        d.end_date = bulkText.value || null
        break
      case 'estimated_hours': {
        // 0 を有効値として扱うため、空文字判定で null と数値を分岐する。
        // v-model 経由の値が数値の 0 になった場合でも、真偽値としての偽判定で
        // null に潰されないよう、文字列化したうえで前後の空白を除去して判定する。
        const raw = String(bulkText.value ?? '').trim()
        d.estimated_hours = raw === '' ? null : parseFloat(raw)
        break
      }
      case 'assignees':
        d.assigneeIds = [...bulkAssignees.value]
        break
      case 'task_kind':
        d.task_kind = bulkTaskKind.value
        break
      case 'quarter_id':
        d.quarter_id = bulkText.value || null
        break
    }
  }
}

// =====================================================================
// 取得
// =====================================================================
const flatten = (tasks: Task[], out: Task[] = []): Task[] => {
  for (const t of tasks) {
    out.push(t)
    if (t.children?.length) flatten(t.children, out)
  }
  return out
}

const wbsCompare = (a: string, b: string): number => {
  const ap = a.split('.').map(Number)
  const bp = b.split('.').map(Number)
  for (let i = 0; i < Math.max(ap.length, bp.length); i++) {
    const diff = (ap[i] ?? 0) - (bp[i] ?? 0)
    if (diff !== 0) return diff
  }
  return 0
}

onMounted(async () => {
  const [tasks, m, q] = await Promise.all([
    api.tasks.list(projectId),
    api.projects.listMembers(projectId),
    api.quarters.list(projectId),
  ])
  members.value = m
  quarters.value = q
  allTasks.value = flatten(tasks).sort((a, b) =>
    wbsCompare(a.wbs_no, b.wbs_no),
  )
  isLoading.value = false
})

// =====================================================================
// 保存
// =====================================================================
const persistDrafts = async () => {
  const promises: Promise<unknown>[] = []
  for (const t of allTasks.value) {
    const d = drafts.get(t.id)
    if (!d) continue
    // 項目（item）は日付・工数・担当者などを保持しない
    if (t.task_type === 'item') continue

    const payload: Record<string, unknown> = {}
    const datesChanged =
      d.start_date !== t.start_date || d.end_date !== t.end_date
    if (d.start_date !== t.start_date) payload.start_date = d.start_date
    if (d.end_date !== t.end_date) payload.end_date = d.end_date
    if (d.estimated_hours !== t.estimated_hours) {
      payload.estimated_hours = d.estimated_hours
    }
    if (d.task_kind !== t.task_kind) payload.task_kind = d.task_kind
    if (d.quarter_id !== t.quarter_id) payload.quarter = d.quarter_id
    if (datesChanged) {
      payload.dates_manual = !!(d.start_date || d.end_date)
    }
    if (Object.keys(payload).length > 0) {
      promises.push(api.tasks.update(projectId, t.id, payload))
    }

    const oldIds = t.assignees.map(a => a.id)
    const added = d.assigneeIds.filter(id => !oldIds.includes(id))
    const removed = oldIds.filter(id => !d.assigneeIds.includes(id))
    for (const uid of added) {
      promises.push(api.tasks.addAssignee(projectId, t.id, uid))
    }
    for (const uid of removed) {
      promises.push(api.tasks.removeAssignee(projectId, t.id, uid))
    }
  }
  await Promise.all(promises)
}

/** 保存後 WBS 画面に戻る */
const handleSave = async () => {
  isSaving.value = true
  try {
    await persistDrafts()
    router.push(`/projects/${projectId}/wbs`)
  } finally {
    isSaving.value = false
  }
}

/** 保存して画面に留まる（最新データを再読込してドラフト・選択をクリア） */
const handleSaveAndContinue = async () => {
  isSaving.value = true
  try {
    await persistDrafts()
    // 最新データを取り直してドラフトをリセットする
    const tasks = await api.tasks.list(projectId)
    allTasks.value = flatten(tasks).sort((a, b) =>
      wbsCompare(a.wbs_no, b.wbs_no),
    )
    drafts.clear()
    selectedIds.value = new Set()
  } finally {
    isSaving.value = false
  }
}

const handleCancel = () => {
  router.push(`/projects/${projectId}/wbs`)
}

// =====================================================================
// 行内編集ヘルパー
// =====================================================================
const toggleAssignee = (t: Task, userId: string) => {
  const d = draftFor(t)
  const i = d.assigneeIds.indexOf(userId)
  if (i === -1) d.assigneeIds.push(userId)
  else d.assigneeIds.splice(i, 1)
}

const memberNameById = (id: string): string =>
  members.value.find(m => m.user_id === id)?.user_name ?? id

// 担当者ポップオーバー（同時に1つだけ開く）
const openAssigneeForTaskId = ref<string | null>(null)

const editedCount = computed(() => drafts.size)

// =====================================================================
// 項目（item）の集計値を計算するヘルパー
// 項目は内部に値を持たず、配下リーフタスクから表示時に算出する。
// 担当者: 子の実装(task_kind='実装')タスクの担当者の和集合
// 開始日: 配下リーフの最早 start_date（ドラフトがあればそちらを使用）
// 終了日: 配下リーフの最遅 end_date
// 工数 : 配下リーフの estimated_hours の合計
// =====================================================================
const collectDescendants = (t: Task, out: Task[] = []): Task[] => {
  if (t.children) {
    for (const c of t.children) {
      out.push(c)
      collectDescendants(c, out)
    }
  }
  return out
}

const leafTasksOf = (t: Task): Task[] =>
  collectDescendants(t).filter(d => d.task_type === 'task')

const implementationTasksOf = (t: Task): Task[] =>
  leafTasksOf(t).filter(d => d.task_kind === '実装')

const effectiveAssigneeIds = (t: Task): string[] => {
  const d = drafts.get(t.id)
  return d ? d.assigneeIds : t.assignees.map(a => a.id)
}
const effectiveDate = (t: Task, key: 'start_date' | 'end_date'): string | null => {
  const d = drafts.get(t.id)
  return d ? d[key] : (t[key] ?? null)
}
const effectiveHours = (t: Task): number | null => {
  const d = drafts.get(t.id)
  return d ? d.estimated_hours : (t.estimated_hours ?? null)
}

const itemAssigneeNames = (t: Task): string => {
  const seen = new Set<string>()
  for (const task of implementationTasksOf(t)) {
    for (const id of effectiveAssigneeIds(task)) seen.add(id)
  }
  if (seen.size === 0) return '—'
  return Array.from(seen).map(memberNameById).join(', ')
}

const itemStartDate = (t: Task): string | null => {
  const dates = leafTasksOf(t)
    .map(x => effectiveDate(x, 'start_date'))
    .filter((d): d is string => !!d)
  if (dates.length === 0) return null
  return dates.reduce((a, b) => a < b ? a : b)
}

const itemEndDate = (t: Task): string | null => {
  const dates = leafTasksOf(t)
    .map(x => effectiveDate(x, 'end_date'))
    .filter((d): d is string => !!d)
  if (dates.length === 0) return null
  return dates.reduce((a, b) => a > b ? a : b)
}

const itemHours = (t: Task): number | null => {
  const hours = leafTasksOf(t)
    .map(x => effectiveHours(x))
    .filter((h): h is number => h != null)
  if (hours.length === 0) return null
  return hours.reduce((a, b) => a + b, 0)
}
</script>

<template>
  <div id="wbs_edit__container" class="h-full flex flex-col min-h-0">
    <div class="flex items-center gap-3 mb-4">
      <router-link :to="`/projects/${projectId}/wbs`" class="text-blue-600 hover:underline text-sm">
        ← WBS
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">WBS編集</h1>
      <div class="ml-auto flex gap-2">
        <button
          :disabled="isSaving"
          class="border border-gray-300 text-sky-900 px-3 py-1.5 rounded text-sm hover:bg-gray-100 disabled:opacity-50"
          @click="handleCancel"
        >
          キャンセル
        </button>
        <button
          :disabled="isSaving || editedCount === 0"
          class="bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
          @click="handleSave"
          title="保存して WBS 画面に戻ります"
        >
          {{ isSaving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="text-gray-500 py-8 text-center">読み込み中...</div>

    <div v-else class="flex-1 flex flex-col min-h-0">
      <!-- 絞り込みトリガー＋列表示 -->
      <div class="flex items-center gap-2 mb-3">
        <button
          class="border border-gray-300 text-sky-900 px-3 py-1.5 rounded text-sm hover:bg-gray-100 inline-flex items-center gap-1.5"
          @click="showFilterDialog = true"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 010 2H4a1 1 0 01-1-1zm2 5a1 1 0 011-1h8a1 1 0 010 2H6a1 1 0 01-1-1zm3 4a1 1 0 011-1h2a1 1 0 010 2H9a1 1 0 01-1-1z" clip-rule="evenodd"/>
          </svg>
          絞り込み
          <span v-if="activeFilterCount > 0" class="bg-blue-600 text-white text-xs rounded-full px-1.5 py-0.5 leading-none">
            {{ activeFilterCount }}
          </span>
        </button>
        <button
          v-if="activeFilterCount > 0"
          class="text-xs text-gray-500 hover:text-sky-900 underline"
          @click="clearFilters"
        >
          条件クリア
        </button>
        <!-- 列表示切替 -->
        <div class="relative">
          <button
            class="border border-gray-300 text-sky-900 px-3 py-1.5 rounded text-sm hover:bg-gray-100"
            @click="showColMenu = !showColMenu"
          >列 ▾</button>
          <div
            v-if="showColMenu"
            class="absolute left-0 top-full mt-1 bg-white border border-gray-300 rounded shadow-lg z-40 py-1 min-w-[140px]"
          >
            <label
              v-for="def in COL_DEFS" :key="def.key"
              class="flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-gray-50 cursor-pointer"
            >
              <input type="checkbox" :checked="showCol(def.key)" @change="toggleCol(def.key)" />
              {{ def.label }}
            </label>
          </div>
        </div>
        <span class="ml-auto text-xs text-gray-600">
          表示 {{ visibleTasks.length }} / 全 {{ allTasks.length }} 件
        </span>
      </div>

      <!-- 一括適用ツールバー -->
      <div class="bg-white rounded-lg shadow p-3 mb-3 border border-gray-300">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-sm font-semibold text-sky-900">一括適用：</span>

          <select
            v-model="bulkField"
            class="border border-gray-300 rounded px-2 py-1.5 text-sm"
          >
            <!-- 表の列順に揃える -->
            <option value="task_kind">分類</option>
            <option value="assignees">担当者</option>
            <option value="start_date">開始日</option>
            <option value="end_date">終了日</option>
            <option value="estimated_hours">見積時間（h）</option>
            <option value="quarter_id">クォーター</option>
          </select>

          <input
            v-if="bulkField === 'start_date' || bulkField === 'end_date'"
            v-model="bulkText"
            type="date"
            class="border border-gray-300 rounded px-2 py-1.5 text-sm"
          />
          <input
            v-else-if="bulkField === 'estimated_hours'"
            v-model="bulkText"
            type="number" min="0" step="0.5"
            class="border border-gray-300 rounded px-2 py-1.5 text-sm w-28"
          />
          <select
            v-else-if="bulkField === 'task_kind'"
            v-model="bulkTaskKind"
            class="border border-gray-300 rounded px-2 py-1.5 text-sm"
          >
            <option :value="null">未設定</option>
            <option value="実装">実装</option>
            <option value="TMRV">TMRV</option>
            <option value="PJRV">PJRV</option>
            <option value="レビュー修正">レビュー修正</option>
          </select>
          <select
            v-else-if="bulkField === 'quarter_id'"
            v-model="bulkText"
            class="border border-gray-300 rounded px-2 py-1.5 text-sm"
          >
            <option value="">未設定</option>
            <option v-for="q in quarters" :key="q.id" :value="q.id">{{ q.title }}</option>
          </select>
          <div
            v-else-if="bulkField === 'assignees'"
            class="flex flex-wrap gap-1.5 border border-gray-300 rounded px-2 py-1 text-sm"
          >
            <label
              v-for="m in members" :key="m.user_id"
              class="flex items-center gap-1 cursor-pointer"
            >
              <input type="checkbox" :value="m.user_id" v-model="bulkAssignees" />
              {{ m.user_name }}
            </label>
            <span v-if="members.length === 0" class="text-gray-400 text-xs">メンバーなし</span>
          </div>

          <button
            :disabled="bulkTargets.length === 0"
            class="bg-sky-700 text-white px-3 py-1.5 rounded text-sm hover:bg-sky-800 disabled:opacity-50"
            @click="applyBulk"
          >
            選択 {{ bulkTargets.length }} 件に適用
          </button>
          <button
            :disabled="isSaving || editedCount === 0"
            class="border border-blue-600 text-blue-600 px-3 py-1.5 rounded text-sm hover:bg-blue-50 disabled:opacity-50"
            @click="handleSaveAndContinue"
            title="保存して編集画面に留まります"
          >
            {{ isSaving ? '保存中...' : '保存して継続' }}
          </button>

          <span class="ml-auto text-xs text-gray-500">
            適用 → 保存して継続 で繰り返し編集できます
          </span>
        </div>
      </div>

      <!-- 編集テーブル: 表内のみスクロール -->
      <div class="bg-white rounded-lg shadow border border-gray-300 overflow-auto flex-1 min-h-0">
        <table class="w-full text-sm table-fixed">
          <thead class="bg-gray-50 border-b border-gray-300 sticky top-0 z-10">
            <tr>
              <th class="px-2 py-2 w-10">
                <input type="checkbox" tabindex="-1" :checked="allVisibleSelected" @change="toggleSelectAll" />
              </th>
              <th class="text-left px-2 py-2 text-gray-600 font-medium w-20">WBS</th>
              <th class="text-left px-2 py-2 text-gray-600 font-medium w-[320px]">タスク</th>
              <th v-if="showCol('task_kind')" class="text-left px-2 py-2 text-gray-600 font-medium w-24">分類</th>
              <th v-if="showCol('assignees')" class="text-left px-2 py-2 text-gray-600 font-medium w-44">担当者</th>
              <th v-if="showCol('start_date')" class="text-left px-2 py-2 text-gray-600 font-medium w-32">開始日</th>
              <th v-if="showCol('end_date')" class="text-left px-2 py-2 text-gray-600 font-medium w-32">終了日</th>
              <th v-if="showCol('estimated_hours')" class="text-left px-2 py-2 text-gray-600 font-medium w-20">見積(h)</th>
              <th v-if="showCol('quarter_id')" class="text-left px-2 py-2 text-gray-600 font-medium w-32">クォーター</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="t in visibleTasks"
              :key="t.id"
              :class="[
                selectedIds.has(t.id) ? 'bg-blue-50' : '',
                drafts.has(t.id) ? 'border-l-4 border-l-amber-400' : '',
              ]"
              class="border-b border-gray-200 hover:bg-gray-50"
            >
              <td class="px-2 py-1 text-center">
                <input type="checkbox" tabindex="-1" :checked="isRowChecked(t)" @change="toggleSelect(t)" />
              </td>
              <td class="px-2 py-1 text-sky-900 text-xs">{{ t.wbs_no }}</td>
              <td class="px-2 py-1 text-sky-900 overflow-hidden whitespace-nowrap" :style="{ paddingLeft: `${8 + t.depth * 16}px` }" :title="t.title">
                {{ t.title }}
              </td>
              <td v-if="showCol('task_kind')" class="px-2 py-1">
                <select
                  v-if="t.task_type === 'task'"
                  tabindex="-1"
                  :value="draftFor(t).task_kind ?? ''"
                  class="border border-gray-300 rounded px-1.5 py-0.5 text-xs w-full"
                  @change="draftFor(t).task_kind = (($event.target as HTMLSelectElement).value || null) as TaskKind | null"
                >
                  <option value="">未設定</option>
                  <option value="実装">実装</option>
                  <option value="TMRV">TMRV</option>
                  <option value="PJRV">PJRV</option>
                  <option value="レビュー修正">レビュー修正</option>
                </select>
                <span v-else class="text-xs text-gray-400">—</span>
              </td>
              <td v-if="showCol('assignees')" class="px-2 py-1">
                <div v-if="t.task_type === 'task'" class="relative">
                  <button
                    type="button"
                    tabindex="-1"
                    class="border border-gray-300 rounded px-2 py-0.5 text-xs w-full text-left bg-white hover:bg-gray-50"
                    @click="openAssigneeForTaskId = openAssigneeForTaskId === t.id ? null : t.id"
                  >
                    <template v-if="draftFor(t).assigneeIds.length === 0">
                      <span class="text-gray-400">未割り当て</span>
                    </template>
                    <template v-else>
                      {{ draftFor(t).assigneeIds.map(memberNameById).join(', ') }}
                    </template>
                  </button>
                  <div
                    v-if="openAssigneeForTaskId === t.id"
                    class="absolute left-0 top-full mt-1 bg-white border border-gray-300 rounded shadow-lg z-30 py-1 min-w-[180px]"
                  >
                    <label
                      v-for="m in members" :key="m.user_id"
                      class="flex items-center gap-2 px-3 py-1 text-xs hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        :checked="draftFor(t).assigneeIds.includes(m.user_id)"
                        @change="toggleAssignee(t, m.user_id)"
                      />
                      {{ m.user_name }}
                    </label>
                  </div>
                </div>
                <span v-else class="text-xs text-gray-500" :title="itemAssigneeNames(t)">
                  {{ itemAssigneeNames(t) }}
                </span>
              </td>
              <td v-if="showCol('start_date')" class="px-2 py-1">
                <input
                  v-if="t.task_type === 'task'"
                  type="date"
                  tabindex="-1"
                  :value="draftFor(t).start_date ?? ''"
                  class="border border-gray-300 rounded px-1.5 py-0.5 text-xs w-full"
                  @input="draftFor(t).start_date = ($event.target as HTMLInputElement).value || null"
                />
                <span v-else class="text-xs text-gray-500">{{ itemStartDate(t) ?? '—' }}</span>
              </td>
              <td v-if="showCol('end_date')" class="px-2 py-1">
                <input
                  v-if="t.task_type === 'task'"
                  type="date"
                  tabindex="-1"
                  :value="draftFor(t).end_date ?? ''"
                  class="border border-gray-300 rounded px-1.5 py-0.5 text-xs w-full"
                  @input="draftFor(t).end_date = ($event.target as HTMLInputElement).value || null"
                />
                <span v-else class="text-xs text-gray-500">{{ itemEndDate(t) ?? '—' }}</span>
              </td>
              <td v-if="showCol('estimated_hours')" class="px-2 py-1">
                <input
                  v-if="t.task_type === 'task'"
                  type="number" min="0" step="0.5"
                  :value="draftFor(t).estimated_hours ?? ''"
                  class="border border-gray-300 rounded px-1.5 py-0.5 text-xs w-full"
                  @input="(e) => {
                    // 0 を有効値として扱うため、空文字のみ null とする
                    const v = (e.target as HTMLInputElement).value
                    draftFor(t).estimated_hours = v === '' ? null : parseFloat(v)
                  }"
                />
                <span v-else class="text-xs text-gray-500">{{ itemHours(t) ?? '—' }}</span>
              </td>
              <td v-if="showCol('quarter_id')" class="px-2 py-1">
                <select
                  v-if="t.task_type === 'task'"
                  tabindex="-1"
                  :value="draftFor(t).quarter_id ?? ''"
                  class="border border-gray-300 rounded px-1.5 py-0.5 text-xs w-full"
                  @change="draftFor(t).quarter_id = ($event.target as HTMLSelectElement).value || null"
                >
                  <option value="">未設定</option>
                  <option v-for="q in quarters" :key="q.id" :value="q.id">{{ q.title }}</option>
                </select>
                <span v-else class="text-xs text-gray-400">—</span>
              </td>
            </tr>
            <tr v-if="visibleTasks.length === 0">
              <td colspan="10" class="px-4 py-8 text-center text-gray-500">
                {{ allTasks.length === 0 ? 'タスクがありません' : '絞り込み条件に一致するタスクがありません' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========== 絞り込みダイアログ ========== -->
    <div
      v-if="showFilterDialog"
      id="wbs_edit__filter_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
      @click.self="showFilterDialog = false"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-[560px] max-h-[90vh] overflow-y-auto">
        <div class="flex items-center mb-4">
          <h2 class="text-base font-semibold text-sky-900">絞り込み条件</h2>
          <button
            class="ml-auto text-gray-400 hover:text-gray-600 text-xl leading-none"
            @click="showFilterDialog = false"
          >×</button>
        </div>

        <div class="space-y-3">
          <!-- タイトル検索 -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">タイトル検索</label>
            <input
              v-model="filterText"
              type="text" placeholder="部分一致"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>

          <!-- 親項目 -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">親項目（配下のタスクのみ表示）</label>
            <select
              v-model="filterParentId"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="">指定しない（全タスク）</option>
              <option v-for="item in itemTasks" :key="item.id" :value="item.id">
                [{{ item.wbs_no }}] {{ item.title }}
              </option>
            </select>
          </div>

          <!-- ステータス（複数選択） -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">ステータス（複数選択可）</label>
            <div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-sky-900 border border-gray-200 rounded px-3 py-2 bg-gray-50">
              <label v-for="s in (['Todo','InProgress','InReview','Done','OnHold'] as const)" :key="s"
                class="inline-flex items-center gap-1 cursor-pointer">
                <input type="checkbox" :checked="filterStatuses.has(s)" @change="toggleStatusFilter(s)" />
                {{ s }}
              </label>
            </div>
          </div>

          <!-- 分類（複数選択・未分類含む） -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">分類（複数選択可）</label>
            <div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-sky-900 border border-gray-200 rounded px-3 py-2 bg-gray-50">
              <label v-for="k in (['実装','TMRV','PJRV','レビュー修正'] as const)" :key="k"
                class="inline-flex items-center gap-1 cursor-pointer">
                <input type="checkbox" :checked="filterKinds.has(k)" @change="toggleKindFilter(k)" />
                {{ k }}
              </label>
              <label class="inline-flex items-center gap-1 cursor-pointer text-gray-600">
                <input type="checkbox" :checked="filterKinds.has(NONE)" @change="toggleKindFilter(NONE)" />
                未分類
              </label>
            </div>
          </div>

          <!-- 担当者（複数選択・未割り当て含む） -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">担当者（複数選択可）</label>
            <div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-sky-900 border border-gray-200 rounded px-3 py-2 bg-gray-50 max-h-32 overflow-y-auto">
              <label v-for="m in members" :key="m.user_id"
                class="inline-flex items-center gap-1 cursor-pointer">
                <input type="checkbox" :checked="filterAssignees.has(m.user_id)" @change="toggleAssigneeFilter(m.user_id)" />
                {{ m.user_name }}
              </label>
              <label class="inline-flex items-center gap-1 cursor-pointer text-gray-600">
                <input type="checkbox" :checked="filterAssignees.has(NONE)" @change="toggleAssigneeFilter(NONE)" />
                未割り当て
              </label>
            </div>
          </div>

          <!-- クォーター（複数選択・未設定含む） -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">クォーター（複数選択可）</label>
            <div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-sky-900 border border-gray-200 rounded px-3 py-2 bg-gray-50">
              <label v-for="q in quarters" :key="q.id"
                class="inline-flex items-center gap-1 cursor-pointer">
                <input type="checkbox" :checked="filterQuarters.has(q.id)" @change="toggleQuarterFilter(q.id)" />
                {{ q.title }}
              </label>
              <label class="inline-flex items-center gap-1 cursor-pointer text-gray-600">
                <input type="checkbox" :checked="filterQuarters.has(NONE)" @change="toggleQuarterFilter(NONE)" />
                未設定
              </label>
            </div>
          </div>

          <!-- 工数未入力 -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">工数</label>
            <div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-sky-900 border border-gray-200 rounded px-3 py-2 bg-gray-50">
              <label class="inline-flex items-center gap-1 cursor-pointer">
                <input type="checkbox" v-model="filterHoursUnset" />
                未入力のみ
              </label>
            </div>
          </div>
        </div>

        <div class="flex justify-between items-center gap-2 mt-5">
          <button
            class="text-sm text-gray-600 hover:underline"
            @click="clearFilters"
          >
            条件をクリア
          </button>
          <div class="flex gap-2">
            <span class="text-xs text-gray-500 self-center">
              {{ visibleTasks.length }} / {{ allTasks.length }} 件
            </span>
            <button
              class="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700"
              @click="showFilterDialog = false"
            >
              閉じる
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
