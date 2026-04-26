<script setup lang="ts">
// 09-01-04 報告書作成・編集画面
import { reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { mockProjects, mockTasks, mockQuarters } from '@/mocks/data'
import type { ReportSections } from '@/types'

const route = useRoute()
const projectId = route.params.projectId as string

const project = mockProjects.find(p => p.id === projectId)
const tasks = mockTasks.filter(t => t.project_id === projectId)
const quarters = mockQuarters.filter(q => q.project_id === projectId)

const isGenerating = ref(false)
const isSaving = ref(false)
const isGenerated = ref(false)

/** 報告書セクション内容 */
const sections = reactive<ReportSections>({
  overview: '',
  summary: '',
  quarters: '',
  tasks: '',
  delayed: '',
  reviews: '',
})

/** 自動生成（MOCK：テンプレートテキストをセット） */
const handleGenerate = async () => {
  isGenerating.value = true
  await new Promise(r => setTimeout(r, 800))

  const delayedTasks = tasks.filter(t => t.end_date && t.end_date < '2026-04-25' && t.status !== '完了')

  sections.overview = `プロジェクト「${project?.name}」の進捗報告書です。\n期間：${project?.start_date} 〜 ${project?.end_date}`
  sections.summary = `全体進捗率：${project?.progress}%\nタスク総数：${tasks.length}件`
  sections.quarters = quarters.map(q => `${q.title}：${q.progress}%`).join('\n')
  sections.tasks = tasks.map(t => `[${t.status}] ${t.wbs_no}. ${t.title}（${t.progress}%）`).join('\n')
  sections.delayed = delayedTasks.length > 0
    ? delayedTasks.map(t => `${t.title}（予定終了：${t.end_date}）`).join('\n')
    : '遅延タスクはありません'
  sections.reviews = 'レビュー待ちタスク：テスト・リリース準備'

  isGenerating.value = false
  isGenerated.value = true
}

/** 保存（MOCK） */
const handleSave = async () => {
  isSaving.value = true
  await new Promise(r => setTimeout(r, 500))
  isSaving.value = false
}

/** PDF出力（MOCK：アラートのみ） */
const handleExportPdf = () => {
  alert('PDF出力機能はバックエンド実装後に有効化されます（MOCK）')
}
</script>

<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">報告書</h1>
    </div>

    <!-- アクションバー -->
    <div class="flex gap-2 mb-6">
      <button
        :disabled="isGenerating"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        data-testid="generate-button"
        @click="handleGenerate"
      >
        {{ isGenerating ? '生成中...' : '自動生成' }}
      </button>
      <button
        :disabled="!isGenerated || isSaving"
        class="border border-gray-300 text-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-50 disabled:opacity-50"
        @click="handleSave"
      >
        {{ isSaving ? '保存中...' : '保存' }}
      </button>
      <button
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
        <label class="block text-sm font-semibold text-gray-700 mb-2">1. 概要</label>
        <textarea
          v-model="sections.overview"
          rows="3"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label class="block text-sm font-semibold text-gray-700 mb-2">2. 全体サマリー</label>
        <textarea
          v-model="sections.summary"
          rows="3"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label class="block text-sm font-semibold text-gray-700 mb-2">3. クォーター別進捗</label>
        <textarea
          v-model="sections.quarters"
          rows="4"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label class="block text-sm font-semibold text-gray-700 mb-2">4. タスク一覧</label>
        <textarea
          v-model="sections.tasks"
          rows="6"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label class="block text-sm font-semibold text-gray-700 mb-2">5. 遅延タスク</label>
        <textarea
          v-model="sections.delayed"
          rows="3"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="bg-white rounded-lg shadow p-5">
        <label class="block text-sm font-semibold text-gray-700 mb-2">6. レビュー状況</label>
        <textarea
          v-model="sections.reviews"
          rows="3"
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  </div>
</template>
