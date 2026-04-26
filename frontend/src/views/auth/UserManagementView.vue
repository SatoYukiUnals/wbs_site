<script setup lang="ts">
// 01-02-00 ユーザー管理画面
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { mockUsers } from '@/mocks/data'
import type { User, UserRole } from '@/types'

const authStore = useAuthStore()

/** ユーザー一覧（MOCKデータ） */
const users = ref<User[]>([...mockUsers])

/** 削除確認ダイアログ表示フラグ */
const showDeleteDialog = ref(false)
const deleteTargetId = ref('')

/**
 * ロール変更処理（MOCK：表示上のみ更新）
 * @param userId 対象ユーザーID
 * @param newRole 新しいロール
 */
const handleRoleChange = (userId: string, newRole: UserRole) => {
  const user = users.value.find(u => u.id === userId)
  if (user) user.role = newRole
}

/**
 * 削除確認ダイアログを表示する
 */
const confirmDelete = (userId: string) => {
  deleteTargetId.value = userId
  showDeleteDialog.value = true
}

/**
 * ユーザー削除処理（MOCK：一覧から除外）
 */
const handleDelete = () => {
  users.value = users.value.filter(u => u.id !== deleteTargetId.value)
  showDeleteDialog.value = false
}

const roleLabel = (role: UserRole) => ({ master: 'マスター', admin: '管理者', member: 'メンバー' }[role])
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold text-sky-900">ユーザー管理</h1>
      <router-link
        to="/users/invite"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
      >
        ユーザー招待
      </router-link>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">表示名</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">メールアドレス</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">ロール</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in users"
            :key="user.id"
            data-testid="user-row"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3" data-testid="user-name">{{ user.display_name }}</td>
            <td class="px-4 py-3 text-gray-600" data-testid="user-email">{{ user.email }}</td>
            <td class="px-4 py-3" data-testid="user-role">
              <!-- masterユーザー自身のロールは変更不可 -->
              <select
                v-if="authStore.currentUser?.role === 'master' && user.id !== authStore.currentUser?.id"
                :value="user.role"
                class="border border-gray-300 rounded px-2 py-1 text-sm"
                @change="handleRoleChange(user.id, ($event.target as HTMLSelectElement).value as UserRole)"
              >
                <option value="master">マスター</option>
                <option value="admin">管理者</option>
                <option value="member">メンバー</option>
              </select>
              <span v-else class="text-gray-700">{{ roleLabel(user.role) }}</span>
            </td>
            <td class="px-4 py-3 text-right">
              <button
                v-if="authStore.currentUser?.role === 'master' && user.id !== authStore.currentUser?.id"
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

    <!-- 削除確認ダイアログ -->
    <div
      v-if="showDeleteDialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">このユーザーを削除しますか？</p>
        <div class="flex justify-end gap-2">
          <button
            class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50"
            @click="showDeleteDialog = false"
          >
            キャンセル
          </button>
          <button
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
