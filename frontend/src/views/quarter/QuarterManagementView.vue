<script setup lang="ts">
// 03-01-00 クォーター管理画面
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import type { Quarter } from '@/types'

const route = useRoute()
const authStore = useAuthStore()
const projectId = route.params.projectId as string

const quarters = ref<Quarter[]>([])
const isAdmin = authStore.currentUser?.role !== 'member'
const showDeleteDialog = ref(false)
const deleteTargetId = ref('')

onMounted(async () => {
  quarters.value = await api.quarters.list(projectId)
})

/** 削除処理 */
const handleDelete = async () => {
  await api.quarters.delete(projectId, deleteTargetId.value)
  quarters.value = quarters.value.filter(q => q.id !== deleteTargetId.value)
  showDeleteDialog.value = false
}
</script>

<template>
  <div id="quarter_mgmt__container">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">クォーター管理</h1>
    </div>

    <div v-if="isAdmin" class="flex justify-end mb-4">
      <router-link
        :to="`/projects/${projectId}/quarters/new`"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
      >
        + クォーター追加
      </router-link>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table id="quarter_mgmt__table" class="w-full text-sm">
        <thead id="quarter_mgmt__thead" class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">クォーター名</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">開始日</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">終了日</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">進捗率</th>
            <th v-if="isAdmin" class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody id="quarter_mgmt__tbody">
          <tr
            v-for="q in quarters"
            :key="q.id"
            :id="`quarter_mgmt__row_${q.id}`"
            data-testid="quarter-row"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3 font-medium text-sky-900">{{ q.title }}</td>
            <td class="px-4 py-3 text-gray-600">{{ q.start_date }}</td>
            <td class="px-4 py-3 text-gray-600">{{ q.end_date }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-24 bg-gray-200 rounded-full h-1.5">
                  <div class="bg-blue-500 h-1.5 rounded-full" :style="{ width: `${q.progress}%` }" />
                </div>
                <span class="text-gray-600 text-xs">{{ q.progress }}%</span>
              </div>
            </td>
            <td v-if="isAdmin" class="px-4 py-3 text-right">
              <router-link
                :to="`/projects/${projectId}/quarters/${q.id}/edit`"
                class="text-blue-600 hover:underline text-xs mr-3"
              >
                編集
              </router-link>
              <button
                :id="`quarter_mgmt__delete_btn_${q.id}`"
                class="text-red-500 hover:text-red-700 text-xs"
                @click="deleteTargetId = q.id; showDeleteDialog = true"
              >
                削除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 削除確認ダイアログ -->
    <div
      v-if="showDeleteDialog"
      id="quarter_mgmt__delete_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">このクォーターを削除しますか？</p>
        <div class="flex justify-end gap-2">
          <button id="quarter_mgmt__cancel_delete_btn" class="px-4 py-2 text-sm border rounded hover:bg-gray-50" @click="showDeleteDialog = false">
            キャンセル
          </button>
          <button id="quarter_mgmt__confirm_delete_btn" class="px-4 py-2 text-sm text-white bg-red-500 rounded hover:bg-red-600" @click="handleDelete">
            削除する
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
