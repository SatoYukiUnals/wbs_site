<script setup lang="ts">
// 02-01-00 プロジェクト一覧
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { mockProjects } from '@/mocks/data'
import type { Project } from '@/types'

const authStore = useAuthStore()
const projects = ref<Project[]>([...mockProjects])

/** adminロール以上かどうか */
const isAdmin = authStore.currentUser?.role === 'admin' || authStore.currentUser?.role === 'master'
</script>

<template>
  <div>
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

    <div v-if="projects.length === 0" class="text-gray-500 text-sm py-8 text-center">
      プロジェクトがありません
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="project in projects"
        :key="project.id"
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

        <div class="text-xs text-gray-500 flex justify-between">
          <span>{{ project.start_date }}</span>
          <span>{{ project.end_date }}</span>
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
