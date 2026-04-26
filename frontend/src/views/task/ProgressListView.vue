<script setup lang="ts">
// 04-XX 進捗一覧（3階層集計・時間/件数/日付/遅延）
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { mockTasks } from '@/mocks/data'
import type { Task } from '@/types'

const route = useRoute()
const projectId = route.params.projectId as string

/** 今日（時刻なし） */
const today = new Date()
today.setHours(0, 0, 0, 0)

// =============================================================
// 日付ベースのステータス判定（task.status フィールドは使わない）
// =============================================================
type DateStatus = 'Done' | 'InProgress' | 'Todo'

const dateStatus = (t: Task): DateStatus => {
  if (t.actual_end_date) return 'Done'
  if (t.actual_start_date) return 'InProgress'
  return 'Todo'
}

// =============================================================
// 実タスク取得（task_type === 'task' の末端ノード）
// =============================================================
const getActualTasks = (t: Task): Task[] => {
  if (t.task_type === 'task') return [t]
  return (t.children ?? []).flatMap(getActualTasks)
}

// =============================================================
// ノード集計
// =============================================================
type NodeStats = {
  wbs_no: string
  title: string
  depth: number
  total_h: number
  done_h: number
  inprogress_h: number
  todo_h: number
  progress_pct: number
  total_count: number
  done_count: number
  inprogress_count: number
  todo_count: number
  earliest_start: string | null
  latest_end: string | null
  earliest_actual_start: string | null
  latest_actual_end: string | null
  delay_h: number
  is_all_done: boolean
}

const calcStats = (node: Task): NodeStats => {
  const tasks = getActualTasks(node)

  const total_h      = tasks.reduce((s, t) => s + (t.estimated_hours ?? 0), 0)
  const done_h       = tasks.filter(t => dateStatus(t) === 'Done').reduce((s, t) => s + (t.estimated_hours ?? 0), 0)
  const inprogress_h = tasks.filter(t => dateStatus(t) === 'InProgress').reduce((s, t) => s + (t.estimated_hours ?? 0), 0)
  const todo_h       = tasks.filter(t => dateStatus(t) === 'Todo').reduce((s, t) => s + (t.estimated_hours ?? 0), 0)

  const total_count      = tasks.length
  const done_count       = tasks.filter(t => dateStatus(t) === 'Done').length
  const inprogress_count = tasks.filter(t => dateStatus(t) === 'InProgress').length
  const todo_count       = tasks.filter(t => dateStatus(t) === 'Todo').length

  // 日付集計（件数が一致しない場合は終了日を空欄）
  const starts     = tasks.map(t => t.start_date).filter(Boolean) as string[]
  const ends       = tasks.map(t => t.end_date).filter(Boolean) as string[]
  const actStarts  = tasks.map(t => t.actual_start_date).filter(Boolean) as string[]
  const actEnds    = tasks.map(t => t.actual_end_date).filter(Boolean) as string[]

  const earliest_start        = starts.length    ? starts.sort()[0]    : null
  const latest_end            = (starts.length === ends.length && ends.length) ? ends.sort().at(-1)! : null
  const earliest_actual_start = actStarts.length ? actStarts.sort()[0] : null
  const latest_actual_end     = (actStarts.length === actEnds.length && actEnds.length) ? actEnds.sort().at(-1)! : null

  const is_all_done = total_count > 0 && done_count === total_count

  // 遅延/巻き
  const aggEndDate = latest_end ? new Date(latest_end) : null
  let delay_h = 0
  if (aggEndDate) {
    if (aggEndDate <= today && !is_all_done) {
      // 期限切れ・未完了 → マイナス（残工数）
      delay_h = -(total_h - done_h)
    } else if (aggEndDate > today && is_all_done) {
      // 予定より前に完了 → プラス（完了工数）
      delay_h = done_h
    }
  }

  return {
    wbs_no: node.wbs_no,
    title: node.title,
    depth: node.depth,
    total_h, done_h, inprogress_h, todo_h,
    progress_pct: total_h > 0 ? done_h / total_h : 0,
    total_count, done_count, inprogress_count, todo_count,
    earliest_start, latest_end, earliest_actual_start, latest_actual_end,
    delay_h,
    is_all_done,
  }
}

// =============================================================
// スキップ条件チェック
// =============================================================
const hasActualTasks = (t: Task): boolean => getActualTasks(t).length > 0

const shouldSkip = (node: Task, parent: Task | null): boolean => {
  if (!parent) return false
  if (node.title === parent.title && !hasActualTasks(node)) return true
  return false
}

// =============================================================
// 行リスト構築（depth 0→1→2 順に展開）
// =============================================================
const rows = computed<NodeStats[]>(() => {
  const result: NodeStats[] = []
  const depth0 = mockTasks.filter(t => t.project_id === projectId && t.depth === 0)

  for (const d0 of depth0) {
    result.push(calcStats(d0))

    for (const d1 of (d0.children ?? [])) {
      if (shouldSkip(d1, d0)) continue
      result.push(calcStats(d1))

      for (const d2 of (d1.children ?? [])) {
        if (shouldSkip(d2, d1)) continue
        result.push(calcStats(d2))
      }
    }
  }

  return result
})

// =============================================================
// 表示ヘルパー
// =============================================================
const INDENT = ['', '　　', '　　　　']

const fmtH = (h: number)    => h.toFixed(1) + 'h'
const fmtPct = (v: number)  => (v * 100).toFixed(1) + '%'
const fmtDate = (d: string | null) => d ? d.replace(/-/g, '/') : '—'

const depthRowClass = (depth: number): string => {
  if (depth === 0) return 'bg-sky-50 font-semibold'
  if (depth === 1) return 'bg-gray-50'
  return 'bg-white'
}

const delayClass = (h: number): string => {
  if (h > 0) return 'text-blue-600 font-medium'
  if (h < 0) return 'text-red-600 font-medium'
  return 'text-sky-900'
}

const fmtDelay = (h: number): string => {
  if (h === 0) return '—'
  return (h > 0 ? '+' : '') + h.toFixed(1) + 'h'
}
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-sky-900 mb-4">進捗一覧</h1>

    <div class="bg-white rounded-lg shadow overflow-x-auto overflow-y-auto border border-gray-500 max-h-[calc(100vh-160px)]">
      <table class="text-xs border-separate border-spacing-0 w-max min-w-full">
        <thead>
          <tr class="bg-gray-100 sticky top-0 z-10">
            <!-- 固定列 -->
            <th class="border-b border-r border-gray-500 px-3 py-2 text-left text-sky-900 whitespace-nowrap sticky left-0 bg-gray-100 z-20">項番</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-left text-sky-900 whitespace-nowrap sticky z-20 bg-gray-100" style="left: 72px">タイトル</th>
            <!-- 時間系 -->
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">総時間</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">Done(h)</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">進行(h)</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">未着手(h)</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">進捗(%)</th>
            <!-- 件数系 -->
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">総件数</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">Done(件)</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">進行(件)</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">未着手(件)</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-center text-sky-900 whitespace-nowrap">進捗(件数)</th>
            <!-- 日付系 -->
            <th class="border-b border-r border-gray-500 px-3 py-2 text-center text-sky-900 whitespace-nowrap">予定開始日</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-center text-sky-900 whitespace-nowrap">予定終了日</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-center text-sky-900 whitespace-nowrap">実績開始日</th>
            <th class="border-b border-r border-gray-500 px-3 py-2 text-center text-sky-900 whitespace-nowrap">実績終了日</th>
            <!-- 遅延/巻き -->
            <th class="border-b border-gray-500 px-3 py-2 text-right text-sky-900 whitespace-nowrap">遅延/巻き</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in rows"
            :key="row.wbs_no"
            :class="depthRowClass(row.depth)"
            class="hover:brightness-95 transition-all"
          >
            <!-- 項番 -->
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-sky-900 whitespace-nowrap sticky left-0 z-10"
                :class="depthRowClass(row.depth)">
              {{ row.wbs_no }}
            </td>
            <!-- タイトル（インデント） -->
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-sky-900 sticky z-10 min-w-[200px]"
                :class="depthRowClass(row.depth)"
                style="left: 72px">
              {{ INDENT[row.depth] }}{{ row.title }}
            </td>
            <!-- 時間系 -->
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right text-sky-900 whitespace-nowrap">{{ fmtH(row.total_h) }}</td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right whitespace-nowrap">
              <span class="text-purple-700">{{ fmtH(row.done_h) }}</span>
            </td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right whitespace-nowrap">
              <span class="text-yellow-700">{{ fmtH(row.inprogress_h) }}</span>
            </td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right whitespace-nowrap">
              <span class="text-green-700">{{ fmtH(row.todo_h) }}</span>
            </td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right text-sky-900 whitespace-nowrap">{{ fmtPct(row.progress_pct) }}</td>
            <!-- 件数系 -->
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right text-sky-900 whitespace-nowrap">{{ row.total_count }}</td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right whitespace-nowrap">
              <span class="text-purple-700">{{ row.done_count }}</span>
            </td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right whitespace-nowrap">
              <span class="text-yellow-700">{{ row.inprogress_count }}</span>
            </td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-right whitespace-nowrap">
              <span class="text-green-700">{{ row.todo_count }}</span>
            </td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-center text-sky-900 whitespace-nowrap">
              {{ row.done_count }}/{{ row.total_count }}
            </td>
            <!-- 日付系 -->
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-center text-sky-900 whitespace-nowrap">{{ fmtDate(row.earliest_start) }}</td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-center text-sky-900 whitespace-nowrap">{{ fmtDate(row.latest_end) }}</td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-center text-sky-900 whitespace-nowrap">{{ fmtDate(row.earliest_actual_start) }}</td>
            <td class="border-b border-r border-gray-500 px-3 py-1.5 text-center text-sky-900 whitespace-nowrap">{{ fmtDate(row.latest_actual_end) }}</td>
            <!-- 遅延/巻き -->
            <td class="border-b border-gray-500 px-3 py-1.5 text-right whitespace-nowrap"
                :class="delayClass(row.delay_h)">
              {{ fmtDelay(row.delay_h) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
