<script setup lang="ts">
// 09-01-04 報告書作成・編集画面
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import type { Project, Task, Quarter, ReportSections } from '@/types'

const route = useRoute()
const projectId = route.params.projectId as string

const project = ref<Project | null>(null)
const tasks = ref<Task[]>([])
const quarters = ref<Quarter[]>([])

onMounted(async () => {
  const [p, t, q] = await Promise.all([
    api.projects.get(projectId),
    api.tasks.list(projectId),
    api.quarters.list(projectId),
  ])
  project.value = p
  tasks.value = t
  quarters.value = q
})

const isGenerating = ref(false)
const isSaving = ref(false)
const isGenerated = ref(false)

const sections = reactive<ReportSections>({
  overview: '',
  summary: '',
  quarters: '',
  tasks: '',
  delayed: '',
  reviews: '',
})

/** 全タスクをフラット展開（再帰） */
const flatTasks = (list: Task[]): Task[] =>
  list.flatMap(t => [t, ...flatTasks(t.children ?? [])])

const handleGenerate = async () => {
  isGenerating.value = true
  const flat = flatTasks(tasks.value)
  const today = new Date().toISOString().slice(0, 10)
  const delayedTasks = flat.filter(t => t.end_date && t.end_date < today && t.status !== 'Done')

  sections.overview = `プロジェクト「${project.value?.name}」の進捗報告書です。\n期間：${project.value?.start_date} 〜 ${project.value?.end_date}`
  sections.summary = `タスク総数：${flat.length}件`
  sections.quarters = quarters.value.map(q => `${q.title}：${q.progress}%`).join('\n')
  sections.tasks = flat.map(t => `[${t.status}] ${t.wbs_no}. ${t.title}`).join('\n')
  sections.delayed = delayedTasks.length > 0
    ? delayedTasks.map(t => `${t.title}（予定終了：${t.end_date}）`).join('\n')
    : '遅延タスクはありません'
  sections.reviews = ''

  isGenerating.value = false
  isGenerated.value = true
}

const handleSave = async () => {
  isSaving.value = true
  await new Promise(r => setTimeout(r, 500))
  isSaving.value = false
}

const handleExportPdf = () => {
  alert('PDF出力機能はバックエンド実装後に有効化されます')
}
</script>

<template>
  <div id="report__container">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">報告書</h1>
    </div>

    <!-- アクションバー -->
    <div id="report__action_bar" class="flex gap-2 mb-6">
      <button
        id="report__generate_btn"
        :disabled="isGenerating"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        data-testid="generate-button"
        @click="handleGenerate"
      >
        {{ isGenerating ? '生成中...' : '自動生成' }}
      </button>
      <button
        id="report__save_btn"
        :disabled="!isGenerated || isSaving"
        class="border border-gray-300 text-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-50 disabled:opacity-50"
        @click="handleSave"
      >
        {{ isSaving ? '保存中...' : '保存' }}
      </button>
      <button
        id="report__export_pdf_btn"
        :disabled="!isGenerated"
        class="border border-gray-300 text-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-50 disabled:opacity-50"
        data-testid="export-pdf-button"
        @click="handleExportPdf"
      >
        PDF出力
      </button>
    </div>

    <div v-if="!isGenerated" class="bg-white rounded-lg shadow p-8 text-center text-gray-400">
      「自動生成」ボタンをクリックすると、プロジェクトの状況を元に報告書が生成されます。
    </div>

    <!-- 報告書フォーム -->
    <div v-else class="space-y-4">
      <div class="bg-white rounded-lg shadow p-5">
        <label for="report__overview_textarea" class="block text-sm font-semibold text-gray-700 mb-2">1. 概要</label>
        <textarea
          id="report__overview_textarea"
          v-model="sections.overview"
          rows="3"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label for="report__summary_textarea" class="block text-sm font-semibold text-gray-700 mb-2">2. 全体サマリー</label>
        <textarea
          id="report__summary_textarea"
          v-model="sections.summary"
          rows="3"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label for="report__quarters_textarea" class="block text-sm font-semibold text-gray-700 mb-2">3. クォーター別進捗</label>
        <textarea
          id="report__quarters_textarea"
          v-model="sections.quarters"
          rows="4"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label for="report__tasks_textarea" class="block text-sm font-semibold text-gray-700 mb-2">4. タスク一覧</label>
        <textarea
          id="report__tasks_textarea"
          v-model="sections.tasks"
          rows="6"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label for="report__delayed_textarea" class="block text-sm font-semibold text-gray-700 mb-2">5. 遅延タスク</label>
        <textarea
          id="report__delayed_textarea"
          v-model="sections.delayed"
          rows="3"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label for="report__reviews_textarea" class="block text-sm font-semibold text-gray-700 mb-2">6. レビュー状況</label>
        <textarea
          id="report__reviews_textarea"
          v-model="sections.reviews"
          rows="3"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  </div>
</template>
