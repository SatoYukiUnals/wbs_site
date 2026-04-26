<script setup lang="ts">
// 07-01-00 ダッシュボード画面
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import type { Project } from '@/types'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.currentUser?.role === 'admin' || authStore.currentUser?.role === 'master')

const projects = ref<Project[]>([])
const stats = ref<{ total: number; done: number; in_progress: number; todo: number } | null>(null)
const isLoading = ref(true)

onMounted(async () => {
  try {
    const [projectList, dashboard] = await Promise.all([
      api.projects.list(),
      api.dashboard.get(),
    ])
    projects.value = projectList
    stats.value = dashboard.task_summary
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div id="dashboard__container">
    <h1 class="text-xl font-bold text-sky-900 mb-6">ダッシュボード</h1>

    <div v-if="isLoading" class="text-gray-400 text-sm py-8 text-center">読み込み中...</div>

    <template v-else>
      <!-- タスクサマリー -->
      <div v-if="stats" id="dashboard__stats_section" class="grid grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-lg shadow p-4 text-center">
          <div class="text-2xl font-bold text-sky-900">{{ stats.total }}</div>
          <div class="text-xs text-gray-500 mt-1">タスク総数</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ stats.done }}</div>
          <div class="text-xs text-gray-500 mt-1">完了</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4 text-center">
          <div class="text-2xl font-bold text-yellow-600">{{ stats.in_progress }}</div>
          <div class="text-xs text-gray-500 mt-1">進行中</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4 text-center">
          <div class="text-2xl font-bold text-gray-500">{{ stats.todo }}</div>
          <div class="text-xs text-gray-500 mt-1">未着手</div>
        </div>
      </div>

      <!-- プロジェクト一覧 -->
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-semibold text-gray-600">プロジェクト</h2>
        <router-link
          v-if="isAdmin"
          to="/projects/new"
          class="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700"
        >
          + プロジェクト追加
        </router-link>
      </div>
      <div id="dashboard__projects_section" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <router-link
          v-for="p in projects"
          :key="p.id"
          :id="`dashboard__card_${p.id}`"
          :to="`/projects/${p.id}`"
          class="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow block"
        >
          <div class="flex items-center justify-between mb-3">
            <span class="font-medium text-sky-900">{{ p.name }}</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div class="bg-blue-500 h-2 rounded-full" :style="{ width: `${p.progress}%` }" />
          </div>
          <div class="flex items-center justify-between text-xs text-gray-500">
            <span>進捗率</span>
            <span class="font-medium text-gray-700">{{ p.progress }}%</span>
          </div>
        </router-link>
      </div>

      <div v-if="projects.length === 0" class="text-gray-400 text-sm py-8 text-center">
        プロジェクトがありません
      </div>
    </template>
  </div>
</template>
