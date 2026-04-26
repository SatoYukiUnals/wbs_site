<script setup lang="ts">
// 02-02-00 メンバー管理画面
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import type { ProjectMember, User, UserRole } from '@/types'

const route = useRoute()
const projectId = route.params.projectId as string

const members = ref<ProjectMember[]>([])
const allUsers = ref<User[]>([])

/** 追加可能なユーザー（既にメンバーでないユーザー） */
const availableUsers = computed(() =>
  allUsers.value.filter(u => !members.value.find(m => m.user_id === u.id))
)

const showAddDialog = ref(false)
const addUserId = ref('')
const addRole = ref<UserRole>('member')
const showDeleteDialog = ref(false)
const deleteTargetId = ref('')

onMounted(async () => {
  const [m, u] = await Promise.all([
    api.projects.listMembers(projectId),
    api.auth.listUsers(),
  ])
  members.value = m
  allUsers.value = u
})

/** メンバー追加処理 */
const handleAddMember = async () => {
  if (!addUserId.value) return
  const m = await api.projects.addMember(projectId, addUserId.value, addRole.value)
  members.value.push(m)
  showAddDialog.value = false
  addUserId.value = ''
}

/** メンバー削除処理 */
const handleDelete = async () => {
  const m = members.value.find(m => m.id === deleteTargetId.value)
  if (!m) return
  await api.projects.removeMember(projectId, m.user_id)
  members.value = members.value.filter(m => m.id !== deleteTargetId.value)
  showDeleteDialog.value = false
}
</script>

<template>
  <div id="member_mgmt__container">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">メンバー管理</h1>
    </div>

    <div class="flex justify-end mb-4">
      <button
        id="member_mgmt__open_add_dialog_btn"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
        @click="showAddDialog = true"
      >
        メンバー追加
      </button>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table id="member_mgmt__table" class="w-full text-sm">
        <thead id="member_mgmt__thead" class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">名前</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">メール</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">ロール</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody id="member_mgmt__tbody">
          <tr
            v-for="m in members"
            :key="m.id"
            :id="`member_mgmt__row_${m.user_id}`"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3">{{ m.user_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ m.email }}</td>
            <td class="px-4 py-3">{{ m.role }}</td>
            <td class="px-4 py-3 text-right">
              <button
                :id="`member_mgmt__delete_btn_${m.user_id}`"
                class="text-red-500 hover:text-red-700 text-xs"
                @click="deleteTargetId = m.id; showDeleteDialog = true"
              >
                削除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- メンバー追加ダイアログ -->
    <div
      v-if="showAddDialog"
      id="member_mgmt__add_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <h2 class="text-base font-semibold mb-4">メンバーを追加</h2>
        <div class="space-y-3">
          <div>
            <label for="member_mgmt__add_user_select" class="block text-sm text-gray-700 mb-1">ユーザー</label>
            <select
              id="member_mgmt__add_user_select"
              v-model="addUserId"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="">選択してください</option>
              <option v-for="u in availableUsers" :key="u.id" :value="u.id">
                {{ u.display_name }}（{{ u.email }}）
              </option>
            </select>
          </div>
          <div>
            <label for="member_mgmt__add_role_select" class="block text-sm text-gray-700 mb-1">ロール</label>
            <select
              id="member_mgmt__add_role_select"
              v-model="addRole"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="admin">管理者</option>
              <option value="member">メンバー</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-4">
          <button
            id="member_mgmt__cancel_add_btn"
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
            @click="showAddDialog = false"
          >
            キャンセル
          </button>
          <button
            id="member_mgmt__confirm_add_btn"
            class="px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700"
            :disabled="!addUserId"
            @click="handleAddMember"
          >
            追加
          </button>
        </div>
      </div>
    </div>

    <!-- 削除確認ダイアログ -->
    <div
      v-if="showDeleteDialog"
      id="member_mgmt__delete_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">このメンバーをプロジェクトから削除しますか？</p>
        <div class="flex justify-end gap-2">
          <button
            id="member_mgmt__cancel_delete_btn"
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
            @click="showDeleteDialog = false"
          >
            キャンセル
          </button>
          <button
            id="member_mgmt__confirm_delete_btn"
            class="px-4 py-2 text-sm text-white bg-red-500 rounded hover:bg-red-600"
            @click="handleDelete"
          >
            削除する
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
