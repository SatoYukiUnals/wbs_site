<script setup lang="ts">
// 11-01-00 テンプレート一覧画面
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import type { Template, TemplateType } from '@/types'

const authStore = useAuthStore()
const isAdmin = authStore.currentUser?.role !== 'member'

const templates = ref<Template[]>([])
const filterType = ref<TemplateType | ''>('')
const showDeleteDialog = ref(false)
const deleteTargetId = ref('')

onMounted(async () => {
  templates.value = await api.templates.list()
})

/** フィルター後の一覧 */
const filteredTemplates = () =>
  filterType.value
    ? templates.value.filter(t => t.type === filterType.value)
    : templates.value

const handleDelete = async () => {
  await api.templates.delete(deleteTargetId.value)
  templates.value = templates.value.filter(t => t.id !== deleteTargetId.value)
  showDeleteDialog.value = false
}

/** 種別ラベル */
const typeLabel = (type: TemplateType): string =>
  type === 'wbs' ? 'WBS' : 'タスク'
</script>

<template>
  <div id="template_list__container">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-sky-900">テンプレート一覧</h1>
      <router-link
        v-if="isAdmin"
        to="/templates/new"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
      >
        + テンプレート追加
      </router-link>
    </div>

    <!-- フィルター -->
    <div id="template_list__filter_area" class="flex items-center gap-3 mb-4">
      <select
        id="template_list__type_select"
        v-model="filterType"
        class="border border-gray-300 rounded px-3 py-1.5 text-sm"
      >
        <option value="">種別：全て</option>
        <option value="wbs">WBS</option>
        <option value="task">タスク</option>
      </select>
    </div>

    <!-- テンプレート一覧テーブル -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table id="template_list__table" class="w-full text-sm">
        <thead id="template_list__thead" class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">テンプレート名</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">種別</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">共有</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">作成者</th>
            <th v-if="isAdmin" class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody id="template_list__tbody">
          <tr
            v-for="t in filteredTemplates()"
            :key="t.id"
            :id="`template_list__row_${t.id}`"
            data-testid="template-row"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3 font-medium text-sky-900">{{ t.title }}</td>
            <td class="px-4 py-3">
              <span class="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded">{{ typeLabel(t.type) }}</span>
            </td>
            <td class="px-4 py-3 text-gray-600 text-xs">{{ t.is_shared ? '共有' : '非共有' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ t.created_by_name }}</td>
            <td v-if="isAdmin" class="px-4 py-3 text-right">
              <router-link
                :to="`/templates/${t.id}/edit`"
                class="text-blue-600 hover:underline text-xs mr-3"
              >
                編集
              </router-link>
              <button
                :id="`template_list__delete_btn_${t.id}`"
                class="text-red-500 hover:text-red-700 text-xs"
                @click="deleteTargetId = t.id; showDeleteDialog = true"
              >
                削除
              </button>
            </td>
          </tr>
          <tr v-if="filteredTemplates().length === 0">
            <td :colspan="isAdmin ? 5 : 4" class="px-4 py-8 text-center text-gray-400">
              テンプレートがありません
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 削除確認ダイアログ -->
    <div
      v-if="showDeleteDialog"
      id="template_list__delete_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">このテンプレートを削除しますか？</p>
        <div class="flex justify-end gap-2">
          <button id="template_list__cancel_delete_btn" class="px-4 py-2 text-sm border rounded hover:bg-gray-50" @click="showDeleteDialog = false">
            キャンセル
          </button>
          <button id="template_list__confirm_delete_btn" class="px-4 py-2 text-sm text-white bg-red-500 rounded hover:bg-red-600" @click="handleDelete">
            削除する
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
