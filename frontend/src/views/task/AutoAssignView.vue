<script setup lang="ts">
// 04-02-04 タスク自動割り振り画面
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import type { AutoAssignPreview } from '@/types'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId as string

const isPreviewing = ref(false)
const isConfirming = ref(false)
const previewResults = ref<AutoAssignPreview[]>([])
const showConfirmDialog = ref(false)

const handlePreview = async () => {
  isPreviewing.value = true
  previewResults.value = await api.autoAssign.preview(projectId)
  isPreviewing.value = false
}

const handleConfirm = async () => {
  isConfirming.value = true
  await api.autoAssign.confirm(projectId)
  isConfirming.value = false
  showConfirmDialog.value = false
  router.push(`/projects/${projectId}/wbs`)
}
</script>

<template>
  <div id="auto_assign__container" class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}/wbs`" class="text-blue-600 hover:underline text-sm">
        ← WBS
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">タスク自動割り振り</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-6 mb-4">
      <p class="text-sm text-gray-600 mb-4">
        担当者未割り当てのタスクを、メンバーの負荷状況に基づいて自動的に割り振ります。
        プレビューで結果を確認してから確定できます。
      </p>
      <button
        id="auto_assign__preview_btn"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        :disabled="isPreviewing"
        data-testid="preview-button"
        @click="handlePreview"
      >
        {{ isPreviewing ? '計算中...' : 'プレビューを取得' }}
      </button>
    </div>

    <!-- プレビュー結果 -->
    <div v-if="previewResults.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-5 py-4 border-b">
        <h2 class="text-sm font-semibold text-gray-700">割り振り結果プレビュー</h2>
      </div>
      <table id="auto_assign__table" class="w-full text-sm">
        <thead id="auto_assign__thead" class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">タスク名</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">割り当て担当者</th>
          </tr>
        </thead>
        <tbody id="auto_assign__tbody">
          <tr
            v-for="item in previewResults"
            :key="item.task_id"
            :id="`auto_assign__row_${item.task_id}`"
            data-testid="preview-row"
            class="border-b last:border-0"
          >
            <td class="px-4 py-3 text-sky-900">{{ item.task_title }}</td>
            <td class="px-4 py-3">
              <span class="bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full">
                {{ item.assignee_name }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="px-5 py-4 border-t bg-gray-50 flex justify-end gap-2">
        <router-link
          :to="`/projects/${projectId}/wbs`"
          class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
        >
          キャンセル
        </router-link>
        <button
          id="auto_assign__confirm_btn"
          class="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700"
          data-testid="confirm-button"
          @click="showConfirmDialog = true"
        >
          この内容で確定する
        </button>
      </div>
    </div>

    <!-- 確定確認ダイアログ -->
    <div
      v-if="showConfirmDialog"
      id="auto_assign__confirm_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">この割り振り内容を確定しますか？</p>
        <div class="flex justify-end gap-2">
          <button id="auto_assign__cancel_dialog_btn" class="px-4 py-2 text-sm border rounded hover:bg-gray-50" @click="showConfirmDialog = false">
            キャンセル
          </button>
          <button
            id="auto_assign__confirm_dialog_btn"
            class="px-4 py-2 text-sm text-white bg-green-600 rounded hover:bg-green-700 disabled:opacity-50"
            :disabled="isConfirming"
            @click="handleConfirm"
          >
            {{ isConfirming ? '処理中...' : '確定する' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
