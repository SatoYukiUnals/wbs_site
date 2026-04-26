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

onMounted(async () => {
  quarters.value = await api.quarters.list(projectId)
})

/** 出力設定 */
const settings = reactive({
  quarter_id: '',
  include_gantt: true,
  include_completed: true,
})

/** Excel出力（MOCK：アラートのみ） */
const handleExport = async () => {
  isExporting.value = true
  await new Promise(r => setTimeout(r, 800))
  isExporting.value = false
  alert('Excel出力機能はバックエンド実装後に有効化されます（MOCK）')
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
        <!-- クォーター選択 -->
        <div>
          <label for="excel_export__quarter_select" class="block text-sm font-medium text-gray-700 mb-1">クォーター（任意）</label>
          <select
            id="excel_export__quarter_select"
            v-model="settings.quarter_id"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
          >
            <option value="">全クォーター</option>
            <option v-for="q in quarters" :key="q.id" :value="q.id">{{ q.title }}</option>
          </select>
          <p class="text-xs text-gray-400 mt-1">指定した場合、そのクォーターのタスクのみ出力します</p>
        </div>

        <!-- 出力オプション -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">出力オプション</label>
          <div class="space-y-2">
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input
                id="excel_export__include_gantt_input"
                v-model="settings.include_gantt"
                type="checkbox"
                data-testid="include-gantt-checkbox"
                class="rounded"
              />
              ガントチャートシートを含める
            </label>
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input
                id="excel_export__include_completed_input"
                v-model="settings.include_completed"
                type="checkbox"
                class="rounded"
              />
              完了済みタスクを含める
            </label>
          </div>
        </div>

        <!-- 出力形式の説明 -->
        <div class="bg-gray-50 rounded p-4 text-xs text-gray-600 space-y-1">
          <p class="font-medium text-gray-700 mb-2">出力内容</p>
          <p>シート1：タスク一覧（WBS番号、タスク名、ステータス、担当者、開始日、終了日、進捗率）</p>
          <p v-if="settings.include_gantt">シート2：ガントチャート（タスクバー、実績バー）</p>
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
