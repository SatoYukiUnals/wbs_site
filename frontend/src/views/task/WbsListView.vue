<script setup lang="ts">
// 04-01-00 WBS一覧画面（WBSリスト + ガントチャート統合）
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { mockTasks, mockMembers, mockQuarters } from '@/mocks/data'
import type { Task, TaskStatus, TaskType } from '@/types'

const route = useRoute()
const authStore = useAuthStore()
const projectId = route.params.projectId as string
const isAdmin = authStore.currentUser?.role !== 'member'

/** フィルター */
const filterStatus = ref<TaskStatus | ''>('')
const filterAssignee = ref('')
const filterQuarter = ref('')
const members = mockMembers.filter(m => m.project_id === projectId)
const quarters = mockQuarters.filter(q => q.project_id === projectId)

const rootTasks = ref<Task[]>(
  mockTasks.filter(t => t.project_id === projectId && t.parent_task_id === null)
)

const filteredTasks = computed(() =>
  rootTasks.value
    .filter(t => {
      if (filterStatus.value && t.status !== filterStatus.value) return false
      if (filterAssignee.value && !t.assignees.find(a => a.id === filterAssignee.value)) return false
      if (filterQuarter.value && t.quarter_id !== filterQuarter.value) return false
      return true
    })
    .sort((a, b) => a.sort_order - b.sort_order)
)

/** 子タスクを sort_order 順に返す */
const sortedChildren = (task: Task): Task[] =>
  [...(task.children ?? [])].sort((a, b) => a.sort_order - b.sort_order)

/** 全子が完了済みかどうか（初期折り畳み判定用） */
const allChildrenDone = (t: Task): boolean =>
  (t.children?.length ?? 0) > 0 && t.children!.every(c => c.status === 'Done')

/** 展開状態（初期表示は全階層展開。ただし全子完了のタスクは折り畳む） */
const allTaskIds = (): string[] => {
  const ids: string[] = []
  for (const t of rootTasks.value) {
    if (!allChildrenDone(t)) {
      ids.push(t.id)
    }
    for (const c of t.children ?? []) {
      if (!allChildrenDone(c)) ids.push(c.id)
    }
  }
  return ids
}
const expandedIds = ref<Set<string>>(new Set(allTaskIds()))
const toggleExpand = (id: string) => {
  if (expandedIds.value.has(id)) expandedIds.value.delete(id)
  else expandedIds.value.add(id)
}


/** ステータス選択肢 */
const statusOptions: TaskStatus[] = ['Todo', 'InProgress', 'InReview', 'Done', 'OnHold']

/** ステータスバッジ色 */
const statusClass = (status: string): string => {
  const map: Record<string, string> = {
    'Todo':       'bg-green-100 text-green-700 border-green-300',
    'InProgress': 'bg-yellow-100 text-yellow-700 border-yellow-300',
    'InReview':   'bg-red-100 text-red-700 border-red-300',
    'Done':       'bg-purple-100 text-purple-700 border-purple-300',
    'OnHold':     'bg-gray-100 text-gray-600 border-gray-300',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600 border-gray-300'
}

/** メンバーカラーパレット（予定:700・実績:900） */
const BAR_COLORS_500 = ['bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-amber-500', 'bg-rose-500', 'bg-cyan-500', 'bg-indigo-500', 'bg-teal-500']
const BAR_COLORS_900 = ['bg-blue-900', 'bg-emerald-900', 'bg-violet-900', 'bg-amber-900', 'bg-rose-900', 'bg-cyan-900', 'bg-indigo-900', 'bg-teal-900']

const memberColorIdx = (userId: string): number => {
  const idx = members.findIndex(m => m.user_id === userId)
  return idx >= 0 ? idx % BAR_COLORS_500.length : BAR_COLORS_500.length - 1
}

/** 予定バー色（担当者ベース・700） */
const barColor = (task: Task): string => {
  const uid = task.assignees[0]?.id
  return uid ? BAR_COLORS_500[memberColorIdx(uid)] : 'bg-gray-500'
}

/** 実績バー色（担当者ベース・900） */
const actualBarColor = (task: Task): string => {
  const uid = task.assignees[0]?.id
  return uid ? BAR_COLORS_900[memberColorIdx(uid)] : 'bg-gray-700'
}

/** 担当者セル背景色（100 + group-hover 200） */
const BG_COLORS_100       = ['bg-blue-100',  'bg-emerald-100',  'bg-violet-100',  'bg-amber-100',  'bg-rose-100',  'bg-cyan-100',  'bg-indigo-100',  'bg-teal-100']
const BG_COLORS_100_HOVER = ['group-hover:bg-blue-200', 'group-hover:bg-emerald-200', 'group-hover:bg-violet-200', 'group-hover:bg-amber-200', 'group-hover:bg-rose-200', 'group-hover:bg-cyan-200', 'group-hover:bg-indigo-200', 'group-hover:bg-teal-200']

const memberCellBgClasses = (task: Task): string => {
  const uid = task.assignees[0]?.id
  if (!uid) return ''
  const idx = memberColorIdx(uid)
  return `${BG_COLORS_100[idx]} ${BG_COLORS_100_HOVER[idx]}`
}

// =====================================================================
// ガントチャート計算（2026-04-01 基準、9ヶ月分）
// =====================================================================

/** 2026年 4〜12月の祝日（固定祝日＋振替含む）*/
const HOLIDAYS = new Set([
  '2026-04-29',
  '2026-05-03', '2026-05-04', '2026-05-05', '2026-05-06',
  '2026-07-20',
  '2026-08-11',
  '2026-09-21', '2026-09-23',
  '2026-10-12',
  '2026-11-03', '2026-11-23',
])

const toYMD = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

const isHoliday = (d: Date) => HOLIDAYS.has(toYMD(d))

const DOW_LABEL = ['日', '月', '火', '水', '木', '金', '土']

const isDayOff = (d: Date) => {
  const dow = d.getDay()
  return dow === 0 || dow === 6 || isHoliday(d)
}

const dowTextClass = (dow: number, holiday: boolean) => {
  if (holiday || dow === 0) return 'text-red-500'
  if (dow === 6) return 'text-sky-500'
  return 'text-sky-900'
}

const viewUnit = ref<'day' | 'week' | 'month'>('day')
const COL_WIDTH = { day: 24, week: 56, month: 80 } as const
const colWidth = computed(() => COL_WIDTH[viewUnit.value])

// クォーター定義（1Q: 4月〜6月）
const QUARTER_START = new Date('2026-04-01')
const QUARTER_END   = new Date('2026-06-30')

/** 全タスクを再帰的に走査して日付一覧を収集 */
const collectDates = (tasks: Task[]): Date[] => {
  const dates: Date[] = []
  for (const t of tasks) {
    if (t.start_date)        dates.push(new Date(t.start_date))
    if (t.end_date)          dates.push(new Date(t.end_date))
    if (t.actual_start_date) dates.push(new Date(t.actual_start_date))
    if (t.actual_end_date)   dates.push(new Date(t.actual_end_date))
    if (t.children)          dates.push(...collectDates(t.children))
  }
  return dates
}

/**
 * ガント表示範囲：クォーターとタスク日付の合算
 * - 日/週表示：実日付をそのまま使用（空白期間を作らない）
 * - 月表示  ：月の境界に丸める（列とバーの位置を一致させる）
 */
const ganttRange = computed(() => {
  const dates = [QUARTER_START, QUARTER_END, ...collectDates(rootTasks.value)]
  const minMs = Math.min(...dates.map(d => d.getTime()))
  const maxMs = Math.max(...dates.map(d => d.getTime()))
  const minDate = new Date(minMs)
  const maxDate = new Date(maxMs)
  const start = viewUnit.value === 'month'
    ? new Date(minDate.getFullYear(), minDate.getMonth(), 1)
    : minDate
  const end = viewUnit.value === 'month'
    ? new Date(maxDate.getFullYear(), maxDate.getMonth() + 1, 0)
    : maxDate
  const totalDays = Math.round((end.getTime() - start.getTime()) / 86400000) + 1
  return { start, end, totalDays, baseMs: start.getTime() }
})

type GanttCol = { label: string; key: string; dow: string; isOff: boolean; holiday: boolean; isPast: boolean; isMonthStart: boolean }

const ganttCols = computed((): GanttCol[] => {
  const { start, totalDays, baseMs } = ganttRange.value
  if (viewUnit.value === 'month') {
    const cols: GanttCol[] = []
    let cur = new Date(start.getFullYear(), start.getMonth(), 1)
    let i = 0
    while (cur <= ganttRange.value.end) {
      const monthEnd = new Date(cur.getFullYear(), cur.getMonth() + 1, 0)
      cols.push({ label: `${cur.getMonth() + 1}月`, key: `m${i}`, dow: '', isOff: false, holiday: false, isPast: monthEnd < today0, isMonthStart: true })
      cur = new Date(cur.getFullYear(), cur.getMonth() + 1, 1)
      i++
    }
    return cols
  }
  if (viewUnit.value === 'week') {
    const cols: GanttCol[] = []
    let prevMonth = -1
    for (let i = 0; i < Math.ceil(totalDays / 7); i++) {
      const d = new Date(baseMs + i * 7 * 86400000)
      const weekEnd = new Date(d.getTime() + 6 * 86400000)
      const isMonthStart = d.getMonth() !== prevMonth
      prevMonth = d.getMonth()
      cols.push({ label: `${d.getMonth() + 1}/${d.getDate()}`, key: `w${i}`, dow: DOW_LABEL[d.getDay()], isOff: isDayOff(d), holiday: isHoliday(d), isPast: weekEnd < today0, isMonthStart })
    }
    return cols
  }
  // 日表示
  const cols: GanttCol[] = []
  let prevMonth = -1
  for (let i = 0; i < totalDays; i++) {
    const d = new Date(baseMs + i * 86400000)
    const isMonthStart = d.getMonth() !== prevMonth
    prevMonth = d.getMonth()
    cols.push({ label: String(d.getDate()), key: `d${i}`, dow: DOW_LABEL[d.getDay()], isOff: isDayOff(d), holiday: isHoliday(d), isPast: d < today0, isMonthStart })
  }
  return cols
})

const ganttGroups = computed(() => {
  if (viewUnit.value === 'month') return null
  const { baseMs } = ganttRange.value
  const groups: { label: string; span: number }[] = []
  let currentMonth = -1
  ganttCols.value.forEach((_, i) => {
    const d = viewUnit.value === 'day'
      ? new Date(baseMs + i * 86400000)
      : new Date(baseMs + i * 7 * 86400000)
    const month = d.getMonth()
    if (month !== currentMonth) { groups.push({ label: `${month + 1}月`, span: 1 }); currentMonth = month }
    else { groups[groups.length - 1].span++ }
  })
  return groups
})

const ganttTotalWidth = computed(() => ganttCols.value.length * colWidth.value)

/** 各ガント列の時刻範囲を事前計算 */
const ganttColRanges = computed((): { startMs: number; endMs: number }[] => {
  const { start, baseMs } = ganttRange.value
  return ganttCols.value.map((_, i) => {
    if (viewUnit.value === 'day') {
      const s = baseMs + i * 86400000
      return { startMs: s, endMs: s + 86400000 - 1 }
    }
    if (viewUnit.value === 'week') {
      const s = baseMs + i * 7 * 86400000
      return { startMs: s, endMs: s + 7 * 86400000 - 1 }
    }
    // 月表示：その月の初日〜末日
    const ms = new Date(start.getFullYear(), start.getMonth() + i, 1)
    const me = new Date(start.getFullYear(), start.getMonth() + i + 1, 0)
    return { startMs: ms.getTime(), endMs: me.getTime() + 86400000 - 1 }
  })
})

/** 今日が属する列インデックス（-1 なら範囲外） */
const todayColIdx = computed(() =>
  ganttColRanges.value.findIndex(r => r.startMs <= today0.getTime() && today0.getTime() <= r.endMs)
)

/** 日付範囲 → [firstCol, lastCol] を返す */
const calcBarRange = (startDate: string | null, endDate: string | null) => {
  if (!startDate || !endDate) return null
  const s = new Date(startDate).getTime()
  const e = new Date(endDate).getTime() + 86400000 - 1
  const ranges = ganttColRanges.value
  let first = -1, last = -1
  for (let i = 0; i < ranges.length; i++) {
    if (ranges[i].endMs >= s && ranges[i].startMs <= e) {
      if (first === -1) first = i
      last = i
    }
  }
  return first === -1 ? null : { first, last }
}

/** 予定バー列範囲を全タスクで事前計算 */
const taskBars = computed(() => {
  const map = new Map<string, { first: number; last: number } | null>()
  const process = (tasks: Task[]) => {
    for (const t of tasks) {
      map.set(t.id, calcBarRange(t.start_date, t.end_date))
      if (t.children) process(t.children)
    }
  }
  process(rootTasks.value)
  return map
})

/** 実績バー列範囲を全タスクで事前計算 */
const taskActualBars = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  const map = new Map<string, { first: number; last: number } | null>()
  const process = (tasks: Task[]) => {
    for (const t of tasks) {
      map.set(t.id, calcBarRange(t.actual_start_date, t.actual_start_date ? (t.actual_end_date ?? today) : null))
      if (t.children) process(t.children)
    }
  }
  process(rootTasks.value)
  return map
})

/** ガントセルの背景クラス */
const ganttCellBg = (col: { isPast: boolean; isOff: boolean }, ci: number): string =>
  ci === todayColIdx.value
    ? 'bg-amber-100 group-hover:bg-amber-200'
    : (col.isPast || col.isOff)
    ? 'bg-gray-200 group-hover:bg-gray-300/70'
    : 'group-hover:bg-gray-100/50'

// =====================================================================
// 列幅管理
// =====================================================================
const COL_NO     = 40
const COL_STATUS = 112
const COL_DATE   = 120
const COL_HOURS  = 72
const COL_OP     = 96

const TITLE_DEFAULT    = 264
const ASSIGNEE_DEFAULT = 96
const titleColWidth    = ref(TITLE_DEFAULT)
const assigneeColWidth = ref(ASSIGNEE_DEFAULT)
const dblClickTitle    = () => { titleColWidth.value    = titleColWidth.value    === TITLE_DEFAULT    ? TITLE_DEFAULT * 2    : TITLE_DEFAULT }
const dblClickAssignee = () => { assigneeColWidth.value = assigneeColWidth.value === ASSIGNEE_DEFAULT ? ASSIGNEE_DEFAULT * 2 : ASSIGNEE_DEFAULT }

// =====================================================================
// 列表示/非表示
// =====================================================================
type ColKey = 'status' | 'assignee' | 'start' | 'end' | 'hours' | 'op'

const COL_DEFS: { key: ColKey; label: string }[] = [
  { key: 'status',   label: 'ステータス' },
  { key: 'assignee', label: '担当者' },
  { key: 'start',    label: '開始日' },
  { key: 'end',      label: '終了日' },
  { key: 'hours',    label: '工数' },
  { key: 'op',       label: '操作' },
]

const visibleCols = ref<Set<ColKey>>(new Set(COL_DEFS.map(d => d.key)))
const showColMenu  = ref(false)
const toggleCol    = (key: ColKey) => {
  if (visibleCols.value.has(key)) visibleCols.value.delete(key)
  else visibleCols.value.add(key)
  visibleCols.value = new Set(visibleCols.value)
}
const show = (key: ColKey) => visibleCols.value.has(key)

/** スクロールコンテナ参照 */
const tableWrapper = ref<HTMLElement | null>(null)

/** 全列の left 位置を一元管理（sticky 配置用） */
const colLeft = computed(() => {
  let l = 0
  const no = l;       l += COL_NO
  const title = l;    l += titleColWidth.value
  const status = l;   if (show('status'))   l += COL_STATUS
  const assignee = l; if (show('assignee')) l += assigneeColWidth.value
  const start = l;    if (show('start'))    l += COL_DATE
  const end = l;      if (show('end'))      l += COL_DATE
  const hours = l;    if (show('hours'))    l += COL_HOURS
  const op = l
  return { no, title, status, assignee, start, end, hours, op }
})

const tableWidth = computed(() => {
  const colWidths: [ColKey, number][] = [
    ['status',   COL_STATUS],
    ['assignee', assigneeColWidth.value],
    ['start',    COL_DATE],
    ['end',      COL_DATE],
    ['hours',    COL_HOURS],
    ['op',       COL_OP],
  ]
  const conditional = colWidths.reduce((sum, [key, w]) => sum + (show(key) ? w : 0), 0)
  return COL_NO + titleColWidth.value + conditional + ganttTotalWidth.value
})

// =====================================================================
// 行ハイライト：進行中 かつ 予定開始日 ≤ 今日 ≤ 予定終了日
// =====================================================================
const today0 = new Date(); today0.setHours(0, 0, 0, 0)
const isActiveToday = (task: Task): boolean => {
  if (task.status !== 'InProgress' || !task.start_date || !task.end_date) return false
  const s = new Date(task.start_date); s.setHours(0, 0, 0, 0)
  const e = new Date(task.end_date);   e.setHours(0, 0, 0, 0)
  return s <= today0 && today0 <= e
}

/** 日付を YYYY/MM/DD 形式に変換 */
const formatDate = (d: string | null) => d ? d.replace(/-/g, '/') : '—'
const formatHours = (h: number | null) => h != null ? h.toFixed(1) : '—'

/** 直接の子タスクの完了数・総数（非リーフ行のステータス表示用） */
const childStats = (task: Task) => {
  const children = task.children ?? []
  const total = children.length
  const completed = children.filter(c => c.status === 'Done').length
  return { completed, total, allDone: total > 0 && completed === total }
}

// =====================================================================
// 項目（item）の日付・工数計算（配下タスクから集計）
// =====================================================================

/** 配下タスクの start_date の最小値 */
const itemStartDate = (task: Task): string | null => {
  if (task.task_type === 'task') return task.start_date
  const dates: string[] = []
  const collect = (t: Task) => {
    if (t.task_type === 'task' && t.start_date) dates.push(t.start_date)
    for (const c of t.children ?? []) collect(c)
  }
  for (const c of task.children ?? []) collect(c)
  return dates.length ? dates.reduce((a, b) => a < b ? a : b) : null
}

/** 配下タスクの end_date の最大値 */
const itemEndDate = (task: Task): string | null => {
  if (task.task_type === 'task') return task.end_date
  const dates: string[] = []
  const collect = (t: Task) => {
    if (t.task_type === 'task' && t.end_date) dates.push(t.end_date)
    for (const c of t.children ?? []) collect(c)
  }
  for (const c of task.children ?? []) collect(c)
  return dates.length ? dates.reduce((a, b) => a > b ? a : b) : null
}

/** 配下タスクの estimated_hours の合計 */
const itemHours = (task: Task): number | null => {
  if (task.task_type === 'task') return task.estimated_hours
  let total = 0, hasAny = false
  const collect = (t: Task) => {
    if (t.task_type === 'task' && t.estimated_hours != null) { total += t.estimated_hours; hasAny = true }
    for (const c of t.children ?? []) collect(c)
  }
  for (const c of task.children ?? []) collect(c)
  return hasAny ? Math.round(total * 100) / 100 : null
}

// =====================================================================
// タスク操作
// =====================================================================

/** 再帰的にIDでタスクを検索 */
const findTaskById = (tasks: Task[], id: string): Task | undefined => {
  for (const t of tasks) {
    if (t.id === id) return t
    if (t.children) {
      const found = findTaskById(t.children, id)
      if (found) return found
    }
  }
}

/** 削除ダイアログ */
const showDeleteDialog = ref(false)
const deleteTargetId = ref('')
const handleDelete = () => {
  rootTasks.value = rootTasks.value.filter(t => t.id !== deleteTargetId.value)
  showDeleteDialog.value = false
}

// =====================================================================
// タスク追加ダイアログ（詳細入力）
// =====================================================================
const showAddDialog = ref(false)
const addParentId = ref<string | null>(null)

const newTask = ref({
  title: '',
  description: '',
  status: 'Todo' as TaskStatus,
  start_date: '',
  end_date: '',
  estimated_hours: '' as number | '',
})
const addError = ref('')

const openAddDialog = (parentId: string | null) => {
  addParentId.value = parentId
  newTask.value = { title: '', description: '', status: 'Todo', start_date: '', end_date: '', estimated_hours: '' }
  addError.value = ''
  showAddDialog.value = true
}

const handleAddTask = () => {
  if (!newTask.value.title.trim()) { addError.value = 'タスク名は必須です'; return }
  const parentTask = addParentId.value ? findTaskById(rootTasks.value, addParentId.value) : null
  const depth = parentTask ? parentTask.depth + 1 : 0
  const task_type: TaskType = depth >= 2 ? 'task' : 'item'
  const task: Task = {
    id: `t${Date.now()}`,
    title: newTask.value.title.trim(),
    description: newTask.value.description,
    task_type,
    status: newTask.value.status,
    sort_order: parentTask ? (parentTask.children?.length ?? 0) + 1 : rootTasks.value.length + 1,
    progress: 0,
    start_date: newTask.value.start_date || null,
    end_date: newTask.value.end_date || null,
    actual_start_date: null,
    actual_end_date: null,
    estimated_hours: newTask.value.estimated_hours !== '' ? Number(newTask.value.estimated_hours) : null,
    quarter_id: null,
    parent_task_id: addParentId.value,
    project_id: projectId,
    wbs_no: '',
    depth,
    assignees: [],
    tm_reviewer: null,
    pj_reviewer: null,
  }
  if (parentTask) {
    if (!parentTask.children) parentTask.children = []
    parentTask.children.push(task)
    expandedIds.value.add(parentTask.id)
  } else {
    rootTasks.value.push(task)
  }
  showAddDialog.value = false
}

// =====================================================================
// 一括追加ダイアログ
// =====================================================================
const showBulkDialog = ref(false)
const bulkText = ref('')

const bulkPreview = computed(() =>
  bulkText.value.split('\n').map(l => l.trim()).filter(l => l.length > 0)
)

const handleBulkAdd = () => {
  bulkPreview.value.forEach((title, i) => {
    rootTasks.value.push({
      id: `t${Date.now()}_${i}`, title, description: '', task_type: 'item', status: 'Todo',
      sort_order: rootTasks.value.length + i + 1,
      progress: 0, start_date: null, end_date: null, actual_start_date: null, actual_end_date: null,
      estimated_hours: null, quarter_id: null, parent_task_id: null, project_id: projectId, wbs_no: '',
      depth: 0, assignees: [], tm_reviewer: null, pj_reviewer: null,
    })
  })
  bulkText.value = ''
  showBulkDialog.value = false
}

/** 初期表示時：ガントの今日列が左端付近に来るようスクロール */
onMounted(() => {
  if (!tableWrapper.value || todayColIdx.value < 0) return
  tableWrapper.value.scrollLeft = Math.max(0, (todayColIdx.value - 3) * colWidth.value)
})
</script>

<template>
  <div>
    <div class="flex items-center gap-3 mb-4">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">WBS</h1>
    </div>

    <!-- フィルター & アクションバー -->
    <div class="flex flex-wrap items-center gap-2 mb-3">
      <select v-model="filterStatus" class="border border-gray-300 rounded px-2 py-1.5 text-sm transition-colors hover:border-gray-400">
        <option value="">ステータス：全て</option>
        <option v-for="s in statusOptions" :key="s" :value="s" class="bg-white text-sky-900">{{ s }}</option>
      </select>
      <select v-model="filterAssignee" class="border border-gray-300 rounded px-2 py-1.5 text-sm transition-colors hover:border-gray-400">
        <option value="">担当者：全て</option>
        <option v-for="m in members" :key="m.user_id" :value="m.user_id">{{ m.user_name }}</option>
      </select>
      <select v-model="filterQuarter" class="border border-gray-300 rounded px-2 py-1.5 text-sm transition-colors hover:border-gray-400">
        <option value="">クォーター：全体</option>
        <option v-for="q in quarters" :key="q.id" :value="q.id">{{ q.title }}</option>
      </select>
      <!-- ガント単位切替 -->
      <div class="flex border border-gray-300 rounded overflow-hidden text-sm">
        <button v-for="unit in (['day', 'week', 'month'] as const)" :key="unit"
          :class="viewUnit === unit ? 'bg-gray-700 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'"
          class="px-3 py-1.5 transition-colors"
          @click="viewUnit = unit"
        >{{ unit === 'day' ? '日' : unit === 'week' ? '週' : '月' }}</button>
      </div>

      <!-- 列表示切替 -->
      <div class="relative">
        <button
          class="border border-gray-300 text-sky-900 px-3 py-1.5 rounded text-sm transition-colors hover:bg-gray-100"
          @click="showColMenu = !showColMenu"
        >列 ▾</button>
        <div v-if="showColMenu"
          class="absolute left-0 top-full mt-1 bg-white border border-gray-500 rounded shadow-lg z-40 py-1 min-w-[120px]">
          <label v-for="def in COL_DEFS" :key="def.key"
            class="flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-gray-50 cursor-pointer">
            <input type="checkbox" :checked="show(def.key)" class="rounded" @change="toggleCol(def.key)" />
            {{ def.label }}
          </label>
        </div>
      </div>

      <div class="ml-auto flex gap-2">
        <router-link :to="`/projects/${projectId}/auto-assign`"
          class="border border-gray-300 text-sky-900 px-3 py-1.5 rounded text-sm transition-colors hover:bg-gray-100 hover:border-gray-400">
          自動割り振り
        </router-link>
        <router-link :to="`/projects/${projectId}/reports`"
          class="border border-gray-300 text-sky-900 px-3 py-1.5 rounded text-sm transition-colors hover:bg-gray-100 hover:border-gray-400">
          報告書
        </router-link>
        <router-link :to="`/projects/${projectId}/export/excel`"
          class="border border-gray-300 text-sky-900 px-3 py-1.5 rounded text-sm transition-colors hover:bg-gray-100 hover:border-gray-400">
          Excel出力
        </router-link>
        <button v-if="isAdmin"
          class="border border-blue-600 text-blue-600 px-3 py-1.5 rounded text-sm transition-colors hover:bg-blue-100"
          @click="showBulkDialog = true">
          一括追加
        </button>
        <button v-if="isAdmin"
          class="bg-blue-600 text-white px-3 py-1.5 rounded text-sm transition-colors hover:bg-blue-700"
          @click="openAddDialog(null)">
          + タスク追加
        </button>
      </div>
    </div>

    <!-- ガント凡例 -->
    <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-sky-900 mb-2">
      <span v-for="(m, i) in members" :key="m.user_id" class="flex items-center gap-1">
        <span class="inline-flex gap-0.5">
          <span :class="BAR_COLORS_500[i % BAR_COLORS_500.length]" class="inline-block w-3 h-2.5 rounded-l opacity-80"></span>
          <span :class="BAR_COLORS_900[i % BAR_COLORS_900.length]" class="inline-block w-3 h-2.5 rounded-r opacity-70"></span>
        </span>
        {{ m.user_name }}
      </span>
      <span class="text-sky-900">（左:予定 右:実績）</span>
      <span class="flex items-center gap-1"><span class="inline-block w-px h-3 bg-red-400 opacity-60"></span>今日</span>
      <span class="flex items-center gap-1"><span class="inline-block w-4 h-3 bg-amber-100 border border-amber-300 rounded"></span>本日進行中</span>
    </div>

    <!-- WBS + ガント統合テーブル（横・縦スクロール） -->
    <div ref="tableWrapper" class="bg-white rounded-lg shadow border border-gray-500 overflow-x-auto overflow-y-auto max-h-[calc(100vh-220px)]" @click.self="showColMenu = false">
      <table class="border-separate border-spacing-0 text-sm table-fixed" :style="{ width: tableWidth + 'px' }">
        <colgroup>
          <col :style="{ width: colLeft.title + 'px' }" />
          <col :style="{ width: titleColWidth + 'px' }" />
          <col v-if="show('status')"   :style="{ width: COL_STATUS + 'px' }" />
          <col v-if="show('assignee')" :style="{ width: assigneeColWidth + 'px' }" />
          <col v-if="show('start')"    :style="{ width: COL_DATE + 'px' }" />
          <col v-if="show('end')"      :style="{ width: COL_DATE + 'px' }" />
          <col v-if="show('hours')"    :style="{ width: COL_HOURS + 'px' }" />
          <col v-if="show('op')" :style="{ width: COL_OP + 'px' }" />
          <col v-for="col in ganttCols" :key="'cg-' + col.key" :style="{ width: colWidth + 'px' }" />
        </colgroup>

        <!-- ========== ヘッダー ========== -->
        <thead class="bg-gray-50 border-b border-gray-500 sticky top-0 z-20">
          <tr>
            <th class="sticky left-0 z-30 bg-gray-50 border-r border-b border-gray-500 px-3 py-2 text-left text-gray-600 font-medium overflow-hidden relative">No<div class="absolute inset-y-0 right-0 w-px bg-gray-200"></div></th>
            <th class="sticky z-30 bg-gray-50 border-r border-b border-gray-500 px-3 py-2 text-left text-gray-600 font-medium overflow-hidden cursor-pointer select-none hover:bg-gray-100 transition-colors" :style="{ left: colLeft.title + 'px' }"
              title="ダブルクリックで列幅を拡張" @dblclick="dblClickTitle">タスク名</th>
            <th v-if="show('status')"   class="sticky z-30 bg-gray-50 border-r border-b border-gray-500 px-3 py-2 text-left text-gray-600 font-medium overflow-hidden" :style="{ left: colLeft.status + 'px' }">ステータス</th>
            <th v-if="show('assignee')" class="sticky z-30 bg-gray-50 border-r border-b border-gray-500 px-3 py-2 text-left text-gray-600 font-medium overflow-hidden cursor-pointer select-none hover:bg-gray-100 transition-colors" :style="{ left: colLeft.assignee + 'px' }"
              title="ダブルクリックで列幅を拡張" @dblclick="dblClickAssignee">担当者</th>
            <th v-if="show('start')" class="sticky z-30 bg-gray-50 border-r border-b border-gray-500 px-2 py-1 text-left text-gray-600 font-medium overflow-hidden" :style="{ left: colLeft.start + 'px' }">
              <div>開始日</div><div class="text-[10px] font-normal text-sky-900 leading-none">予 / 実</div>
            </th>
            <th v-if="show('end')" class="sticky z-30 bg-gray-50 border-r border-b border-gray-500 px-2 py-1 text-left text-gray-600 font-medium overflow-hidden" :style="{ left: colLeft.end + 'px' }">
              <div>終了日</div><div class="text-[10px] font-normal text-sky-900 leading-none">予 / 実</div>
            </th>
            <th v-if="show('hours')" class="sticky z-30 bg-gray-50 border-r border-b border-gray-500 px-3 py-2 text-left text-gray-600 font-medium overflow-hidden" :style="{ left: colLeft.hours + 'px' }">工数(h)</th>
            <th v-if="show('op')" class="sticky z-30 bg-gray-50 border-r border-b border-gray-500 px-3 py-2 overflow-hidden" :style="{ left: colLeft.op + 'px' }"></th>
            <!-- ガントカラムヘッダー（2行） -->
            <th :colspan="ganttCols.length" class="px-0 py-0 border-b border-gray-500">
              <div v-if="ganttGroups" class="flex border-b border-gray-500">
                <div v-for="group in ganttGroups" :key="group.label"
                  :style="{ minWidth: (group.span * colWidth) + 'px' }"
                  class="text-center text-xs font-medium text-sky-900 py-1 border-r border-gray-500 last:border-0">{{ group.label }}</div>
              </div>
              <div class="flex">
                <div v-for="(col, ci) in ganttCols" :key="col.key"
                  :style="{ minWidth: colWidth + 'px', width: colWidth + 'px' }"
                  :class="ci === todayColIdx ? 'bg-amber-100' : (col.isPast || col.isOff) ? 'bg-gray-200' : ''"
                  class="text-center text-xs py-0.5 border-r border-gray-500 last:border-0 overflow-hidden">
                  <div :class="(col.isPast || col.isOff) ? 'text-gray-400' : 'text-sky-900'">{{ col.label }}</div>
                  <div v-if="viewUnit !== 'month'" :class="dowTextClass(DOW_LABEL.indexOf(col.dow), col.holiday)" class="text-[10px] leading-none pb-0.5">{{ col.dow }}</div>
                </div>
              </div>
            </th>
          </tr>
        </thead>

        <!-- ========== ボディ ========== -->
        <tbody>
          <template v-for="task in filteredTasks" :key="task.id">

            <!-- ルートタスク行 -->
            <tr data-testid="task-row"
              :class="['border-b border-gray-500 group', isActiveToday(task) ? 'bg-amber-50 hover:bg-amber-100' : 'hover:bg-gray-50/60']">
              <td :class="['sticky left-0 z-10 border-r border-b border-gray-500 px-3 py-2 text-sky-900 text-xs overflow-hidden relative', isActiveToday(task) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-white group-hover:bg-gray-50/60']">
                {{ task.wbs_no }}<div class="absolute inset-y-0 right-0 w-px bg-gray-100"></div>
              </td>
              <td :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 font-medium overflow-hidden', isActiveToday(task) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-white group-hover:bg-gray-50/60']" :style="{ left: colLeft.title + 'px' }">
                <div class="flex items-center gap-1">
                  <button v-if="task.children?.length"
                    class="rounded hover:bg-gray-200 transition-colors w-5 h-5 flex items-center justify-center flex-shrink-0 text-sky-900"
                    @click="toggleExpand(task.id)">{{ expandedIds.has(task.id) ? '▾' : '▸' }}</button>
                  <span v-else class="w-5 flex-shrink-0"></span>
                  <span class="truncate text-sky-900">{{ task.title }}</span>
                </div>
              </td>
              <td v-if="show('status')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-2 overflow-hidden', isActiveToday(task) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-white group-hover:bg-gray-50/60']" :style="{ left: colLeft.status + 'px' }">
                <select v-if="task.task_type === 'task'" v-model="task.status" :class="statusClass(task.status)"
                  class="border rounded-full px-2 py-0.5 text-xs cursor-pointer w-full" data-testid="status-select">
                  <option v-for="s in statusOptions" :key="s" :value="s" class="bg-white text-sky-900">{{ s }}</option>
                </select>
                <span v-else class="text-sky-900 text-xs whitespace-nowrap block text-center">
                  {{ childStats(task).completed }} / {{ childStats(task).total }}
                </span>
              </td>
              <td v-if="show('assignee')" :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 text-xs overflow-hidden', isActiveToday(task) ? 'bg-amber-50 group-hover:bg-amber-100' : memberCellBgClasses(task) || 'bg-white group-hover:bg-gray-50/60']" :style="{ left: colLeft.assignee + 'px' }">
                <div class="truncate">{{ task.assignees.map(a => a.name).join(', ') || '—' }}</div>
                <div v-if="task.task_type === 'item' && (task.tm_reviewer || task.pj_reviewer)" class="text-[10px] text-sky-900 leading-snug">
                  <span v-if="task.tm_reviewer">TM:{{ task.tm_reviewer.name }}</span>
                  <span v-if="task.pj_reviewer" class="ml-1">PJ:{{ task.pj_reviewer.name }}</span>
                </div>
              </td>
              <td v-if="show('start')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-1 overflow-hidden', isActiveToday(task) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-white group-hover:bg-gray-50/60']" :style="{ left: colLeft.start + 'px' }">
                <div class="text-xs">{{ formatDate(itemStartDate(task)) }}</div>
                <div v-if="task.task_type === 'task'" class="text-[10px] text-sky-900 leading-snug">{{ formatDate(task.actual_start_date) }}</div>
              </td>
              <td v-if="show('end')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-1 overflow-hidden', isActiveToday(task) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-white group-hover:bg-gray-50/60']" :style="{ left: colLeft.end + 'px' }">
                <div class="text-xs">{{ formatDate(itemEndDate(task)) }}</div>
                <div v-if="task.task_type === 'task'" class="text-[10px] text-sky-900 leading-snug">{{ formatDate(task.actual_end_date) }}</div>
              </td>
              <td v-if="show('hours')" :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 text-xs text-right overflow-hidden', isActiveToday(task) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-white group-hover:bg-gray-50/60']" :style="{ left: colLeft.hours + 'px' }">
                {{ formatHours(itemHours(task)) }}
              </td>
              <td v-if="show('op')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-2 whitespace-nowrap overflow-hidden', isActiveToday(task) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-white group-hover:bg-gray-50/60']" :style="{ left: colLeft.op + 'px' }">
                <button class="rounded hover:bg-gray-200 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 text-sm"
                  title="子タスクを追加" @click="openAddDialog(task.id)">+</button>
                <router-link v-if="task.task_kind === 'レビュー依頼'"
                  :to="`/projects/${projectId}/tasks/${task.id}/reviews`"
                  class="rounded hover:bg-yellow-100 hover:text-yellow-600 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                  title="レビュー">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                </router-link>
                <router-link :to="`/projects/${projectId}/tasks/${task.id}`"
                  class="rounded hover:bg-blue-100 hover:text-blue-500 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                  title="編集">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/>
                  </svg>
                </router-link>
                <button class="rounded hover:bg-red-100 hover:text-red-500 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                  title="削除" @click="deleteTargetId = task.id; showDeleteDialog = true">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zm0 2h2l.5 1H8.5L9 4zM6 6h8v10H6V6zm2 2a1 1 0 00-1 1v4a1 1 0 102 0V9a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 102 0V9a1 1 0 00-1-1z" clip-rule="evenodd"/>
                  </svg>
                </button>
              </td>
              <!-- ガントセル（列ごと・上半分=予定 / 下半分=実績） -->
              <td v-for="(col, ci) in ganttCols" :key="col.key"
                  :class="['px-0 relative z-0 overflow-hidden h-10 border-r border-b border-gray-500',
                                                      ganttCellBg(col, ci)]">
                <div class="absolute inset-x-0 top-1/2 border-t border-gray-500 pointer-events-none"></div>
                <!-- 予定バー（上半分） -->
                <div v-if="taskBars.get(task.id) && ci >= taskBars.get(task.id)!.first && ci <= taskBars.get(task.id)!.last"
                     :class="['absolute top-1.5 h-3 opacity-80 pointer-events-none z-10', barColor(task),
                              ci === taskBars.get(task.id)!.first ? 'left-px rounded-l-sm' : 'left-0',
                              ci === taskBars.get(task.id)!.last  ? 'right-px rounded-r-sm' : 'right-0']">
                </div>
                <!-- 実績バー（下半分） -->
                <div v-if="taskActualBars.get(task.id) && ci >= taskActualBars.get(task.id)!.first && ci <= taskActualBars.get(task.id)!.last"
                     :class="['absolute bottom-1.5 h-2.5 opacity-70 pointer-events-none', actualBarColor(task),
                              ci === taskActualBars.get(task.id)!.first ? 'left-px rounded-l-sm' : 'left-0',
                              ci === taskActualBars.get(task.id)!.last  ? 'right-px rounded-r-sm' : 'right-0']">
                </div>
              </td>
            </tr>

            <!-- 子タスク行 -->
            <template v-if="expandedIds.has(task.id) && task.children">
              <template v-for="child in sortedChildren(task)" :key="child.id">
                <tr data-testid="task-row-child"
                  :class="['border-b border-gray-500 group', isActiveToday(child) ? 'bg-amber-50 hover:bg-amber-100' : 'bg-gray-50/30 hover:bg-gray-50/80']">
                  <td :class="['sticky left-0 z-10 border-r border-b border-gray-500 px-3 py-2 text-sky-900 text-xs overflow-hidden relative', isActiveToday(child) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-gray-50 group-hover:bg-gray-100']">
                    {{ child.wbs_no }}<div class="absolute inset-y-0 right-0 w-px bg-gray-100"></div>
                  </td>
                  <td :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 overflow-hidden', isActiveToday(child) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-gray-50 group-hover:bg-gray-100']" :style="{ left: colLeft.title + 'px' }">
                    <div class="flex items-center gap-1 pl-5">
                      <button v-if="child.children?.length"
                        class="rounded hover:bg-gray-200 transition-colors w-5 h-5 flex items-center justify-center flex-shrink-0 text-sky-900"
                        @click="toggleExpand(child.id)">{{ expandedIds.has(child.id) ? '▾' : '▸' }}</button>
                      <span v-else class="w-5 flex-shrink-0"></span>
                      <span class="truncate text-sky-900">{{ child.title }}</span>
                    </div>
                  </td>
                  <td v-if="show('status')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-2 overflow-hidden', isActiveToday(child) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-gray-50 group-hover:bg-gray-100']" :style="{ left: colLeft.status + 'px' }">
                    <select v-if="child.task_type === 'task'" v-model="child.status" :class="statusClass(child.status)"
                      class="border rounded-full px-2 py-0.5 text-xs cursor-pointer w-full">
                      <option v-for="s in statusOptions" :key="s" :value="s" class="bg-white text-sky-900">{{ s }}</option>
                    </select>
                    <span v-else class="text-sky-900 text-xs whitespace-nowrap block text-center">
                      {{ childStats(child).completed }} / {{ childStats(child).total }}
                    </span>
                  </td>
                  <td v-if="show('assignee')" :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 text-xs overflow-hidden', isActiveToday(child) ? 'bg-amber-50 group-hover:bg-amber-100' : memberCellBgClasses(child) || 'bg-gray-50 group-hover:bg-gray-100']" :style="{ left: colLeft.assignee + 'px' }">
                    <div class="truncate">{{ child.assignees.map(a => a.name).join(', ') || '—' }}</div>
                    <div v-if="child.task_type === 'item' && (child.tm_reviewer || child.pj_reviewer)" class="text-[10px] text-sky-900 leading-snug">
                      <span v-if="child.tm_reviewer">TM:{{ child.tm_reviewer.name }}</span>
                      <span v-if="child.pj_reviewer" class="ml-1">PJ:{{ child.pj_reviewer.name }}</span>
                    </div>
                  </td>
                  <td v-if="show('start')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-1 overflow-hidden', isActiveToday(child) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-gray-50 group-hover:bg-gray-100']" :style="{ left: colLeft.start + 'px' }">
                    <div class="text-xs">{{ formatDate(itemStartDate(child)) }}</div>
                    <div v-if="child.task_type === 'task'" class="text-[10px] text-sky-900 leading-snug">{{ formatDate(child.actual_start_date) }}</div>
                  </td>
                  <td v-if="show('end')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-1 overflow-hidden', isActiveToday(child) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-gray-50 group-hover:bg-gray-100']" :style="{ left: colLeft.end + 'px' }">
                    <div class="text-xs">{{ formatDate(itemEndDate(child)) }}</div>
                    <div v-if="child.task_type === 'task'" class="text-[10px] text-sky-900 leading-snug">{{ formatDate(child.actual_end_date) }}</div>
                  </td>
                  <td v-if="show('hours')" :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 text-xs text-right overflow-hidden', isActiveToday(child) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-gray-50 group-hover:bg-gray-100']" :style="{ left: colLeft.hours + 'px' }">
                    {{ formatHours(itemHours(child)) }}
                  </td>
                  <td v-if="show('op')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-2 whitespace-nowrap overflow-hidden', isActiveToday(child) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-gray-50 group-hover:bg-gray-100']" :style="{ left: colLeft.op + 'px' }">
                    <button class="rounded hover:bg-gray-200 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 text-sm"
                      title="子タスクを追加" @click="openAddDialog(child.id)">+</button>
                    <router-link :to="`/projects/${projectId}/tasks/${child.id}`"
                      class="rounded hover:bg-blue-100 hover:text-blue-500 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                      title="編集">
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/>
                      </svg>
                    </router-link>
                    <button class="rounded hover:bg-red-100 hover:text-red-500 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                      title="削除" @click="deleteTargetId = child.id; showDeleteDialog = true">
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zm0 2h2l.5 1H8.5L9 4zM6 6h8v10H6V6zm2 2a1 1 0 00-1 1v4a1 1 0 102 0V9a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 102 0V9a1 1 0 00-1-1z" clip-rule="evenodd"/>
                      </svg>
                    </button>
                    <router-link v-if="child.task_kind === 'レビュー依頼'"
                      :to="`/projects/${projectId}/tasks/${child.id}/reviews`"
                      class="rounded hover:bg-yellow-100 hover:text-yellow-600 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                      title="レビュー">
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                      </svg>
                    </router-link>
                  </td>
                  <!-- ガントセル（子・列ごと・上半分=予定 / 下半分=実績） -->
                  <td v-for="(col, ci) in ganttCols" :key="col.key"
                      :class="['px-0 relative z-0 overflow-hidden h-9 border-r border-b border-gray-500',
                                                              ganttCellBg(col, ci)]">
                    <div class="absolute inset-x-0 top-1/2 border-t border-gray-500 pointer-events-none"></div>
                    <!-- 予定バー（上半分） -->
                    <div v-if="taskBars.get(child.id) && ci >= taskBars.get(child.id)!.first && ci <= taskBars.get(child.id)!.last"
                         :class="['absolute top-1.5 h-2.5 opacity-75 pointer-events-none z-10', barColor(child),
                                  ci === taskBars.get(child.id)!.first ? 'left-px rounded-l-sm' : 'left-0',
                                  ci === taskBars.get(child.id)!.last  ? 'right-px rounded-r-sm' : 'right-0']">
                    </div>
                    <!-- 実績バー（下半分） -->
                    <div v-if="taskActualBars.get(child.id) && ci >= taskActualBars.get(child.id)!.first && ci <= taskActualBars.get(child.id)!.last"
                         :class="['absolute bottom-1.5 h-2 opacity-65 pointer-events-none', actualBarColor(child),
                                  ci === taskActualBars.get(child.id)!.first ? 'left-px rounded-l-sm' : 'left-0',
                                  ci === taskActualBars.get(child.id)!.last  ? 'right-px rounded-r-sm' : 'right-0']">
                    </div>
                  </td>
                </tr>

                <!-- 孫タスク行 -->
                <template v-if="expandedIds.has(child.id) && child.children">
                  <tr v-for="grand in sortedChildren(child)" :key="grand.id" data-testid="task-row-grand"
                    :class="['border-b border-gray-500 group', isActiveToday(grand) ? 'bg-amber-50 hover:bg-amber-100' : 'bg-blue-50/10 hover:bg-blue-50/30']">
                    <td :class="['sticky left-0 z-10 border-r border-b border-gray-500 px-3 py-2 text-sky-900 text-xs overflow-hidden relative', isActiveToday(grand) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-blue-50 group-hover:bg-blue-100']">
                      {{ grand.wbs_no }}<div class="absolute inset-y-0 right-0 w-px bg-gray-100"></div>
                    </td>
                    <td :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 text-xs overflow-hidden', isActiveToday(grand) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-blue-50 group-hover:bg-blue-100']" :style="{ left: colLeft.title + 'px' }">
                      <div class="flex items-center gap-1 pl-10">
                        <span class="w-5 flex-shrink-0"></span>
                        <span class="truncate text-sky-900">{{ grand.title }}</span>
                      </div>
                    </td>
                    <td v-if="show('status')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-2 overflow-hidden', isActiveToday(grand) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-blue-50 group-hover:bg-blue-100']" :style="{ left: colLeft.status + 'px' }">
                      <select v-model="grand.status" :class="statusClass(grand.status)"
                        class="border rounded-full px-2 py-0.5 text-xs cursor-pointer w-full">
                        <option v-for="s in statusOptions" :key="s" :value="s" class="bg-white text-sky-900">{{ s }}</option>
                      </select>
                    </td>
                    <td v-if="show('assignee')" :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 text-xs truncate overflow-hidden', isActiveToday(grand) ? 'bg-amber-50 group-hover:bg-amber-100' : memberCellBgClasses(grand) || 'bg-blue-50 group-hover:bg-blue-100']" :style="{ left: colLeft.assignee + 'px' }">
                      {{ grand.assignees.map(a => a.name).join(', ') || '—' }}
                    </td>
                    <td v-if="show('start')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-1 overflow-hidden', isActiveToday(grand) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-blue-50 group-hover:bg-blue-100']" :style="{ left: colLeft.start + 'px' }">
                      <div class="text-xs">{{ formatDate(grand.start_date) }}</div>
                      <div class="text-[10px] text-sky-900 leading-snug">{{ formatDate(grand.actual_start_date) }}</div>
                    </td>
                    <td v-if="show('end')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-1 overflow-hidden', isActiveToday(grand) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-blue-50 group-hover:bg-blue-100']" :style="{ left: colLeft.end + 'px' }">
                      <div class="text-xs">{{ formatDate(grand.end_date) }}</div>
                      <div class="text-[10px] text-sky-900 leading-snug">{{ formatDate(grand.actual_end_date) }}</div>
                    </td>
                    <td v-if="show('hours')" :class="['sticky z-10 border-r border-b border-gray-500 px-3 py-2 text-xs text-right overflow-hidden', isActiveToday(grand) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-blue-50 group-hover:bg-blue-100']" :style="{ left: colLeft.hours + 'px' }">
                      {{ formatHours(grand.estimated_hours) }}
                    </td>
                    <td v-if="show('op')" :class="['sticky z-10 border-r border-b border-gray-500 px-2 py-2 whitespace-nowrap overflow-hidden', isActiveToday(grand) ? 'bg-amber-50 group-hover:bg-amber-100' : 'bg-blue-50 group-hover:bg-blue-100']" :style="{ left: colLeft.op + 'px' }">
                      <span class="w-5 h-5 inline-flex flex-shrink-0"></span>
                      <router-link :to="`/projects/${projectId}/tasks/${grand.id}`"
                        class="rounded hover:bg-blue-100 hover:text-blue-500 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                        title="編集">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/>
                        </svg>
                      </router-link>
                      <button class="rounded hover:bg-red-100 hover:text-red-500 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                        title="削除" @click="deleteTargetId = grand.id; showDeleteDialog = true">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zm0 2h2l.5 1H8.5L9 4zM6 6h8v10H6V6zm2 2a1 1 0 00-1 1v4a1 1 0 102 0V9a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 102 0V9a1 1 0 00-1-1z" clip-rule="evenodd"/>
                        </svg>
                      </button>
                      <router-link v-if="grand.task_kind === 'レビュー依頼'"
                        :to="`/projects/${projectId}/tasks/${grand.id}/reviews`"
                        class="rounded hover:bg-yellow-100 hover:text-yellow-600 transition-colors w-5 h-5 inline-flex items-center justify-center text-sky-900 ml-1"
                        title="レビュー">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                      </router-link>
                    </td>
                    <!-- ガントセル（孫・列ごと） -->
                    <td v-for="(col, ci) in ganttCols" :key="col.key"
                        :class="['px-0 relative z-0 overflow-hidden h-8 border-r border-b border-gray-500',
                                                                  ganttCellBg(col, ci)]">
                      <div class="absolute inset-x-0 top-1/2 border-t border-gray-500 pointer-events-none"></div>
                      <!-- 予定バー（上半分） -->
                      <div v-if="taskBars.get(grand.id) && ci >= taskBars.get(grand.id)!.first && ci <= taskBars.get(grand.id)!.last"
                           :class="['absolute top-1 h-2.5 opacity-65 pointer-events-none z-10', barColor(grand),
                                    ci === taskBars.get(grand.id)!.first ? 'left-px rounded-l-sm' : 'left-0',
                                    ci === taskBars.get(grand.id)!.last  ? 'right-px rounded-r-sm' : 'right-0']">
                      </div>
                      <!-- 実績バー（下半分） -->
                      <div v-if="taskActualBars.get(grand.id) && ci >= taskActualBars.get(grand.id)!.first && ci <= taskActualBars.get(grand.id)!.last"
                           :class="['absolute bottom-1 h-2 opacity-60 pointer-events-none', actualBarColor(grand),
                                    ci === taskActualBars.get(grand.id)!.first ? 'left-px rounded-l-sm' : 'left-0',
                                    ci === taskActualBars.get(grand.id)!.last  ? 'right-px rounded-r-sm' : 'right-0']">
                      </div>
                    </td>
                  </tr>
                </template>
              </template>
            </template>
          </template>

          <tr v-if="filteredTasks.length === 0">
            <td colspan="99" class="px-4 py-8 text-center text-sky-900">タスクがありません</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ========== タスク追加ダイアログ ========== -->
    <div v-if="showAddDialog" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 w-[480px] max-h-[90vh] overflow-y-auto">
        <h2 class="text-base font-semibold mb-4">{{ addParentId ? '子タスクを追加' : 'タスクを追加' }}</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-sky-900 mb-1">タスク名 <span class="text-red-500">*</span></label>
            <input v-model="newTask.title" type="text" data-testid="new-task-title-input"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <p v-if="addError" class="text-red-500 text-xs mt-1">{{ addError }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-sky-900 mb-1">説明</label>
            <textarea v-model="newTask.description" rows="2"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-sky-900 mb-1">ステータス</label>
            <select v-model="newTask.status" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              <option v-for="s in statusOptions" :key="s" :value="s" class="bg-white text-sky-900">{{ s }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-sky-900 mb-1">開始日</label>
              <input v-model="newTask.start_date" type="date" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-sky-900 mb-1">終了日</label>
              <input v-model="newTask.end_date" type="date" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-sky-900 mb-1">見積時間（h）</label>
              <input v-model.number="newTask.estimated_hours" type="number" min="0" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button class="px-4 py-2 text-sm text-gray-600 border rounded transition-colors hover:bg-gray-100" @click="showAddDialog = false">キャンセル</button>
          <button class="px-4 py-2 text-sm text-white bg-blue-600 rounded transition-colors hover:bg-blue-700" @click="handleAddTask">追加</button>
        </div>
      </div>
    </div>

    <!-- ========== 一括追加ダイアログ ========== -->
    <div v-if="showBulkDialog" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 w-[480px]">
        <h2 class="text-base font-semibold mb-2">タスクを一括追加</h2>
        <p class="text-xs text-sky-900 mb-3">1行に1つのタスク名を入力してください。空行は無視されます。</p>
        <textarea v-model="bulkText" rows="8"
          placeholder="例）&#10;要件定義&#10;基本設計&#10;詳細設計"
          data-testid="bulk-add-textarea"
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono" />
        <div class="mt-2 text-xs text-sky-900">{{ bulkPreview.length }} 件追加されます</div>
        <div class="flex justify-end gap-2 mt-4">
          <button class="px-4 py-2 text-sm text-gray-600 border rounded transition-colors hover:bg-gray-100"
            @click="showBulkDialog = false; bulkText = ''">キャンセル</button>
          <button :disabled="bulkPreview.length === 0"
            class="px-4 py-2 text-sm text-white bg-blue-600 rounded transition-colors hover:bg-blue-700 disabled:opacity-50"
            @click="handleBulkAdd">{{ bulkPreview.length }} 件追加</button>
        </div>
      </div>
    </div>

    <!-- 削除確認ダイアログ -->
    <div v-if="showDeleteDialog" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">このタスクを削除しますか？</p>
        <div class="flex justify-end gap-2">
          <button class="px-4 py-2 text-sm border rounded transition-colors hover:bg-gray-100" @click="showDeleteDialog = false">キャンセル</button>
          <button class="px-4 py-2 text-sm text-white bg-red-500 rounded transition-colors hover:bg-red-600" @click="handleDelete">削除する</button>
        </div>
      </div>
    </div>
  </div>
</template>
