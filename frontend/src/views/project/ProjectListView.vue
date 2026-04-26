<script setup lang="ts">
// 02-01-00 プロジェクト一覧
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import type { Project } from '@/types'

const authStore = useAuthStore()
const projects = ref<Project[]>([])
const isLoading = ref(true)

const isAdmin = authStore.currentUser?.role === 'admin' || authStore.currentUser?.role === 'master'

onMounted(async () => {
  try {
    projects.value = await api.projects.list()
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div id="project_list__container">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold text-sky-900">プロジェクト一覧</h1>
      <router-link
        v-if="isAdmin"
        to="/projects/new"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
      >
        + プロジェクト追加
      </router-link>
    </div>

    <div v-if="isLoading" class="text-gray-400 text-sm py-8 text-center">読み込み中...</div>

    <div v-else-if="projects.length === 0" class="text-gray-500 text-sm py-8 text-center">
      プロジェクトがありません
    </div>

    <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="project in projects"
        :key="project.id"
        :id="`project_list__card_${project.id}`"
        data-testid="project-card"
        class="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between mb-3">
          <router-link
            :to="`/projects/${project.id}`"
            data-testid="project-name"
            class="text-base font-semibold text-blue-700 hover:underline"
          >
            {{ project.name }}
          </router-link>
          <span
            data-testid="project-progress"
            class="text-sm font-medium text-gray-700 ml-2 shrink-0"
          >
            {{ project.progress }}%
          </span>
        </div>

        <p class="text-xs text-gray-500 mb-3 line-clamp-2">{{ project.description }}</p>

        <!-- 進捗バー -->
        <div class="w-full bg-gray-200 rounded-full h-2 mb-3">
          <div
            class="bg-blue-500 h-2 rounded-full transition-all"
            :style="{ width: `${project.progress}%` }"
          />
        </div>

        <div v-if="isAdmin" class="flex gap-2 mt-3 pt-3 border-t">
          <router-link
            :to="`/projects/${project.id}/edit`"
            class="text-xs text-blue-600 hover:underline"
          >
            編集
          </router-link>
          <router-link
            :to="`/projects/${project.id}/members`"
            class="text-xs text-blue-600 hover:underline"
          >
            メンバー管理
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
