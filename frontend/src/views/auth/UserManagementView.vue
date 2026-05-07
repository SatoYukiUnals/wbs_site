<script setup lang="ts">
// 01-02-00 ユーザー管理画面（直接登録・編集・削除）
import { reactive, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import type { User, UserRole } from '@/types'

const authStore = useAuthStore()

const users = ref<User[]>([])
const isMaster = () => authStore.currentUser?.role === 'master'

// 削除モーダル
const showDeleteDialog = ref(false)
const deleteTargetId = ref('')

// 追加モーダル
const showCreateDialog = ref(false)
const createForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'member' as UserRole,
})
const createErr = ref('')
const isCreating = ref(false)

// 編集モーダル
const showEditDialog = ref(false)
const editTarget = ref<User | null>(null)
const editForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'member' as UserRole,
})
const editErr = ref('')
const isSavingEdit = ref(false)

onMounted(async () => {
  users.value = await api.auth.listUsers()
})

const roleLabel = (role: UserRole) =>
  ({ master: 'マスター', admin: '管理者', member: 'メンバー' }[role])

// ---- 追加 ----
const openCreate = () => {
  createForm.username = ''
  createForm.email = ''
  createForm.password = ''
  createForm.role = 'member'
  createErr.value = ''
  showCreateDialog.value = true
}

const handleCreate = async () => {
  if (!createForm.username.trim() ||
      !createForm.email.trim() ||
      createForm.password.length < 8) return
  isCreating.value = true
  createErr.value = ''
  try {
    const created = await api.auth.createUser({
      username: createForm.username.trim(),
      email: createForm.email.trim(),
      password: createForm.password,
      role: createForm.role,
    })
    users.value.push(created)
    showCreateDialog.value = false
  } catch (err) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const e = err as any
    const data = e.response?.data ?? {}
    createErr.value =
      data.detail ??
      data.email?.[0] ??
      data.password?.[0] ??
      data.username?.[0] ??
      '登録に失敗しました。'
  } finally {
    isCreating.value = false
  }
}

// ---- 編集 ----
const openEdit = (user: User) => {
  editTarget.value = user
  editForm.username = user.display_name
  editForm.email = user.email
  editForm.password = ''
  editForm.role = user.role
  editErr.value = ''
  showEditDialog.value = true
}

const handleSaveEdit = async () => {
  if (!editTarget.value) return
  if (!editForm.username.trim() || !editForm.email.trim()) return
  if (editForm.password && editForm.password.length < 8) {
    editErr.value = 'パスワードは8文字以上にしてください。'
    return
  }
  isSavingEdit.value = true
  editErr.value = ''
  try {
    const payload: {
      username: string
      email: string
      role: UserRole
      password?: string
    } = {
      username: editForm.username.trim(),
      email: editForm.email.trim(),
      role: editForm.role,
    }
    if (editForm.password) payload.password = editForm.password
    const updated = await api.auth.updateUser(editTarget.value.id, payload)
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) users.value[idx] = updated
    showEditDialog.value = false
    editTarget.value = null
  } catch (err) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const e = err as any
    const data = e.response?.data ?? {}
    editErr.value =
      data.detail ??
      data.email?.[0] ??
      data.password?.[0] ??
      data.username?.[0] ??
      '更新に失敗しました。'
  } finally {
    isSavingEdit.value = false
  }
}

// ---- 削除 ----
const confirmDelete = (userId: string) => {
  deleteTargetId.value = userId
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  await api.auth.deleteUser(deleteTargetId.value)
  users.value = users.value.filter(u => u.id !== deleteTargetId.value)
  showDeleteDialog.value = false
}
</script>

<template>
  <div id="user_mgmt__container">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold text-sky-900">ユーザー管理</h1>
      <button
        v-if="isMaster()"
        id="user_mgmt__create_btn"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
        @click="openCreate"
      >
        ユーザー追加
      </button>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table id="user_mgmt__table" class="w-full text-sm">
        <thead id="user_mgmt__thead" class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">表示名</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">メールアドレス</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">ロール</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody id="user_mgmt__tbody">
          <tr
            v-for="user in users"
            :key="user.id"
            :id="`user_mgmt__row_${user.id}`"
            data-testid="user-row"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3" data-testid="user-name">{{ user.display_name }}</td>
            <td class="px-4 py-3 text-gray-600" data-testid="user-email">{{ user.email }}</td>
            <td class="px-4 py-3" data-testid="user-role">
              {{ roleLabel(user.role) }}
            </td>
            <td class="px-4 py-3 text-right space-x-3">
              <button
                v-if="isMaster()"
                :id="`user_mgmt__edit_btn_${user.id}`"
                class="text-blue-600 hover:text-blue-800 text-xs"
                @click="openEdit(user)"
              >
                編集
              </button>
              <button
                v-if="isMaster() && user.id !== authStore.currentUser?.id"
                :id="`user_mgmt__delete_btn_${user.id}`"
                class="text-red-500 hover:text-red-700 text-xs"
                @click="confirmDelete(user.id)"
              >
                削除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 追加ダイアログ -->
    <div
      v-if="showCreateDialog"
      id="user_mgmt__create_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-96">
        <h2 class="text-base font-semibold text-sky-900 mb-3">ユーザー追加</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">ユーザー名 <span class="text-red-500">*</span></label>
            <input
              v-model="createForm.username"
              type="text"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">メールアドレス <span class="text-red-500">*</span></label>
            <input
              v-model="createForm.email"
              type="email"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">パスワード <span class="text-red-500">*</span></label>
            <input
              v-model="createForm.password"
              type="password"
              autocomplete="new-password"
              minlength="8"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">8文字以上</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">ロール</label>
            <select
              v-model="createForm.role"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="master">マスター</option>
              <option value="admin">管理者</option>
              <option value="member">メンバー</option>
            </select>
          </div>
          <p v-if="createErr" class="text-sm text-red-600">{{ createErr }}</p>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
            @click="showCreateDialog = false"
          >
            キャンセル
          </button>
          <button
            :disabled="isCreating || !createForm.username.trim() || !createForm.email.trim() || createForm.password.length < 8"
            class="px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
            @click="handleCreate"
          >
            {{ isCreating ? '登録中...' : '登録' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 編集ダイアログ -->
    <div
      v-if="showEditDialog"
      id="user_mgmt__edit_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-96">
        <h2 class="text-base font-semibold text-sky-900 mb-3">ユーザー編集</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">ユーザー名</label>
            <input
              v-model="editForm.username"
              type="text"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">メールアドレス</label>
            <input
              v-model="editForm.email"
              type="email"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">パスワード</label>
            <input
              v-model="editForm.password"
              type="password"
              autocomplete="new-password"
              placeholder="変更しない場合は空のまま"
              minlength="8"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">変更する場合のみ入力（8文字以上）</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">ロール</label>
            <select
              v-model="editForm.role"
              :disabled="editTarget?.id === authStore.currentUser?.id"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm disabled:bg-gray-50 disabled:text-gray-500"
            >
              <option value="master">マスター</option>
              <option value="admin">管理者</option>
              <option value="member">メンバー</option>
            </select>
            <p v-if="editTarget?.id === authStore.currentUser?.id" class="text-xs text-gray-500 mt-1">
              自分自身のロールは変更できません。
            </p>
          </div>
          <p v-if="editErr" class="text-sm text-red-600">{{ editErr }}</p>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
            @click="showEditDialog = false"
          >
            キャンセル
          </button>
          <button
            :disabled="isSavingEdit || !editForm.username.trim() || !editForm.email.trim()"
            class="px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
            @click="handleSaveEdit"
          >
            {{ isSavingEdit ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 削除確認ダイアログ -->
    <div
      v-if="showDeleteDialog"
      id="user_mgmt__delete_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">このユーザーを削除しますか？</p>
        <div class="flex justify-end gap-2">
          <button
            id="user_mgmt__cancel_delete_btn"
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
            @click="showDeleteDialog = false"
          >
            キャンセル
          </button>
          <button
            id="user_mgmt__confirm_delete_btn"
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
