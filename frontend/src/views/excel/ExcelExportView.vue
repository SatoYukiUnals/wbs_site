<script setup lang="ts">
// 10-01-04 Excel出力設定画面
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import type { Quarter } from '@/types'

const route = useRoute()
const projectId = route.params.projectId as string

const quarters = ref<Quarter[]>([])
const isExporting = ref(false)
const filterMode = ref<'quarter' | 'date'>('quarter')

onMounted(async () => {
  quarters.value = await api.quarters.list(projectId)
})

const settings = reactive({
  quarter_id: '',
  start_date: '',
  end_date: '',
})

const handleExport = async () => {
  isExporting.value = true
  try {
    const params: { quarter_id?: string; start_date?: string; end_date?: string } = {}
    if (filterMode.value === 'quarter' && settings.quarter_id) {
      params.quarter_id = settings.quarter_id
    } else if (filterMode.value === 'date') {
      if (settings.start_date) params.start_date = settings.start_date
      if (settings.end_date) params.end_date = settings.end_date
    }
    const blob = await api.excel.export(projectId, params)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'WBS.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    isExporting.value = false
  }
}
</script>

<template>
  <div id="excel_export__container" class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">WBS Excel出力</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <div class="space-y-5">
        <!-- フィルターモード切替 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">出力範囲</label>
          <div class="flex gap-4">
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input
                id="excel_export__mode_quarter_input"
                v-model="filterMode"
                type="radio"
                value="quarter"
              />
              クォーター指定
            </label>
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input
                id="excel_export__mode_date_input"
                v-model="filterMode"
                type="radio"
                value="date"
              />
              期間指定
            </label>
          </div>
        </div>

        <!-- クォーター選択 -->
        <div v-if="filterMode === 'quarter'">
          <label for="excel_export__quarter_select" class="block text-sm font-medium text-gray-700 mb-1">クォーター</label>
          <select
            id="excel_export__quarter_select"
            v-model="settings.quarter_id"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
          >
            <option value="">全クォーター（全期間）</option>
            <option v-for="q in quarters" :key="q.id" :value="q.id">{{ q.title }}</option>
          </select>
          <p class="text-xs text-gray-400 mt-1">指定した場合、そのクォーターのタスクのみ出力します</p>
        </div>

        <!-- 期間指定 -->
        <div v-else class="space-y-3">
          <div>
            <label for="excel_export__start_date_input" class="block text-sm font-medium text-gray-700 mb-1">開始日</label>
            <input
              id="excel_export__start_date_input"
              v-model="settings.start_date"
              type="date"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label for="excel_export__end_date_input" class="block text-sm font-medium text-gray-700 mb-1">終了日</label>
            <input
              id="excel_export__end_date_input"
              v-model="settings.end_date"
              type="date"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <p class="text-xs text-gray-400">指定期間内に開始日・終了日が重なるタスクを出力します</p>
        </div>

        <!-- 出力内容の説明 -->
        <div class="bg-gray-50 rounded p-4 text-xs text-gray-600 space-y-1">
          <p class="font-medium text-gray-700 mb-2">出力内容（3シート）</p>
          <p>シート1：WBS一覧（WBS番号・タスク名・ステータス・担当者・日付・見積時間・進捗%）</p>
          <p>シート2：直近のタスク（期限切れ・今週開始予定・着手中）</p>
          <p>シート3：進捗一覧（時間/件数/日付集計・遅延/巻き）</p>
        </div>

        <div class="pt-2">
          <button
            id="excel_export__export_btn"
            :disabled="isExporting"
            class="bg-green-600 text-white px-6 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50 w-full"
            data-testid="export-button"
            @click="handleExport"
          >
            {{ isExporting ? '出力中...' : 'Excelファイルをダウンロード' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
