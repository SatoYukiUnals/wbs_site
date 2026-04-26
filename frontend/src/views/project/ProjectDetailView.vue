<script setup lang="ts">
// 02-01-03 プロジェクト詳細画面
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import type { Project, Quarter, ProjectMember } from '@/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const projectId = route.params.projectId as string
const project = ref<Project | null>(null)
const members = ref<ProjectMember[]>([])
const quarters = ref<Quarter[]>([])
const isAdmin = authStore.currentUser?.role === 'admin' || authStore.currentUser?.role === 'master'
const showDeleteDialog = ref(false)

onMounted(async () => {
  const [p, m, q] = await Promise.all([
    api.projects.get(projectId),
    api.projects.listMembers(projectId),
    api.quarters.list(projectId),
  ])
  project.value = p
  members.value = m
  quarters.value = q
})

/** プロジェクト削除処理 */
const handleDelete = async () => {
  await api.projects.delete(projectId)
  showDeleteDialog.value = false
  router.push('/projects')
}
</script>

<template>
  <div v-if="!project" class="text-gray-500 py-8 text-center">読み込み中...</div>

  <div v-else id="project_detail__container">
    <!-- ヘッダー -->
    <div class="flex items-start justify-between mb-6">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <router-link to="/projects" class="text-blue-600 hover:underline text-sm">
            プロジェクト一覧
          </router-link>
          <span class="text-gray-400">/</span>
          <h1 class="text-xl font-bold text-sky-900">{{ project.name }}</h1>
        </div>
        <p class="text-sm text-gray-500">{{ project.description }}</p>
      </div>
      <div v-if="isAdmin" class="flex gap-2">
        <router-link
          id="project_detail__edit_btn"
          :to="`/projects/${projectId}/edit`"
          class="text-sm text-blue-600 border border-blue-600 px-3 py-1.5 rounded hover:bg-blue-50"
        >
          編集
        </router-link>
        <button
          id="project_detail__delete_btn"
          class="text-sm text-red-500 border border-red-500 px-3 py-1.5 rounded hover:bg-red-50"
          @click="showDeleteDialog = true"
        >
          削除
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <!-- プロジェクト概要カード -->
      <div class="bg-white rounded-lg shadow p-5">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">進捗状況</h2>
        <div class="text-3xl font-bold text-blue-600 mb-2">{{ project.progress }}%</div>
        <div class="w-full bg-gray-200 rounded-full h-2 mb-3">
          <div class="bg-blue-500 h-2 rounded-full" :style="{ width: `${project.progress}%` }" />
        </div>
      </div>

      <!-- クイックリンク -->
      <div class="bg-white rounded-lg shadow p-5 col-span-2">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">機能メニュー</h2>
        <div class="grid grid-cols-3 gap-2">
          <router-link :to="`/projects/${projectId}/wbs`" class="text-center p-3 border rounded hover:bg-blue-50 hover:border-blue-300 text-sm text-gray-700">WBS</router-link>
          <router-link :to="`/projects/${projectId}/recent`" class="text-center p-3 border rounded hover:bg-blue-50 hover:border-blue-300 text-sm text-gray-700">直近のタスク</router-link>
          <router-link :to="`/projects/${projectId}/progress`" class="text-center p-3 border rounded hover:bg-blue-50 hover:border-blue-300 text-sm text-gray-700">進捗一覧</router-link>
          <router-link :to="`/projects/${projectId}/reviews`" class="text-center p-3 border rounded hover:bg-blue-50 hover:border-blue-300 text-sm text-gray-700">レビュー</router-link>
          <router-link :to="`/projects/${projectId}/quarters`" class="text-center p-3 border rounded hover:bg-blue-50 hover:border-blue-300 text-sm text-gray-700">クォーター</router-link>
          <router-link :to="`/projects/${projectId}/members`" class="text-center p-3 border rounded hover:bg-blue-50 hover:border-blue-300 text-sm text-gray-700">メンバー管理</router-link>
        </div>
      </div>
    </div>

    <!-- クォーター一覧 -->
    <div id="project_detail__quarters_section" class="bg-white rounded-lg shadow p-5 mb-6">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-semibold text-gray-700">クォーター</h2>
        <router-link :to="`/projects/${projectId}/quarters`" class="text-xs text-blue-600 hover:underline">すべて見る</router-link>
      </div>
      <div class="space-y-2">
        <div v-for="q in quarters" :key="q.id" :id="`project_detail__quarter_row_${q.id}`" class="flex items-center justify-between text-sm">
          <span class="text-gray-700">{{ q.title }}</span>
          <div class="flex items-center gap-3">
            <div class="w-32 bg-gray-200 rounded-full h-1.5">
              <div class="bg-blue-500 h-1.5 rounded-full" :style="{ width: `${q.progress}%` }" />
            </div>
            <span class="text-gray-500 w-10 text-right">{{ q.progress }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- メンバー一覧 -->
    <div id="project_detail__members_section" class="bg-white rounded-lg shadow p-5">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-semibold text-gray-700">メンバー</h2>
        <router-link v-if="isAdmin" :to="`/projects/${projectId}/members`" class="text-xs text-blue-600 hover:underline">管理</router-link>
      </div>
      <div class="flex flex-wrap gap-2">
        <span v-for="m in members" :key="m.id" :id="`project_detail__member_row_${m.user_id}`" class="bg-gray-100 text-gray-700 text-xs px-3 py-1 rounded-full">
          {{ m.user_name }}（{{ m.role }}）
        </span>
      </div>
    </div>

    <!-- 削除確認ダイアログ -->
    <div v-if="showDeleteDialog" id="project_detail__delete_dialog" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">「{{ project.name }}」を削除しますか？この操作は取り消せません。</p>
        <div class="flex justify-end gap-2">
          <button id="project_detail__cancel_delete_btn" class="px-4 py-2 text-sm text-gray-600 border rounded hover:bg-gray-50" @click="showDeleteDialog = false">キャンセル</button>
          <button id="project_detail__confirm_delete_btn" class="px-4 py-2 text-sm text-white bg-red-500 rounded hover:bg-red-600" @click="handleDelete">削除する</button>
        </div>
      </div>
    </div>
  </div>
</template>
