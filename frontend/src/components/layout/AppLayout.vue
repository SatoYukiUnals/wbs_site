<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import type { Project } from '@/types'
import { isPageLoading } from '@/composables/usePageLoading'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const projectId = computed(() => route.params.projectId as string | undefined)
const currentProject = ref<Project | null>(null)
const isAdmin = computed(() => authStore.currentUser?.role === 'admin' || authStore.currentUser?.role === 'master')

/** プロジェクト内ページに入ったらプロジェクト情報を取得 */
onMounted(async () => {
  if (projectId.value) {
    try {
      currentProject.value = await api.projects.get(projectId.value)
    } catch {
      currentProject.value = null
    }
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div id="app_layout__container" class="min-h-screen bg-gray-100 flex">

    <!-- サイドバー -->
    <aside id="app_layout__sidebar" class="w-52 bg-gray-900 text-gray-200 flex-shrink-0 flex flex-col">

      <!-- ロゴ -->
      <div class="px-4 py-4 border-b border-gray-700">
        <router-link to="/dashboard" class="font-bold text-base text-white hover:opacity-80 block">
          WBS管理
        </router-link>
      </div>

      <!-- ナビゲーション -->
      <nav id="app_layout__nav" class="flex-1 px-3 py-4 overflow-y-auto text-sm space-y-0.5">

        <!-- グローバルメニュー -->
        <p class="text-xs text-gray-500 px-2 py-1 uppercase tracking-wide">メニュー</p>

        <router-link
          to="/dashboard"
          class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors"
          active-class="bg-gray-700 text-white"
        >
          <span>ダッシュボード</span>
        </router-link>

        <div class="flex items-center justify-between px-3 py-2 rounded hover:bg-gray-700 transition-colors group">
          <router-link
            to="/projects"
            class="flex-1"
            active-class="text-white"
          >
            <span>プロジェクト一覧</span>
          </router-link>
          <router-link
            v-if="isAdmin"
            to="/projects/new"
            class="text-gray-400 hover:text-white text-base leading-none ml-1"
            title="プロジェクト追加"
          >＋</router-link>
        </div>

        <div class="flex items-center justify-between px-3 py-2 rounded hover:bg-gray-700 transition-colors group">
          <router-link
            to="/templates"
            class="flex-1"
            active-class="text-white"
          >
            <span>テンプレート</span>
          </router-link>
          <router-link
            v-if="isAdmin"
            to="/templates/new"
            class="text-gray-400 hover:text-white text-base leading-none ml-1"
            title="テンプレート追加"
          >＋</router-link>
        </div>

        <!-- プロジェクト内メニュー -->
        <template v-if="projectId && currentProject">
          <p class="text-xs text-gray-500 px-2 py-1 uppercase tracking-wide mt-4">プロジェクト</p>

          <router-link
            :to="`/projects/${projectId}`"
            class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors font-medium"
            active-class="bg-gray-700 text-white"
          >
            <span class="truncate">{{ currentProject.name }}</span>
          </router-link>

          <router-link
            :to="`/projects/${projectId}/wbs`"
            class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors pl-5"
            active-class="bg-gray-700 text-white"
          >
            <span>WBS</span>
          </router-link>

          <router-link
            :to="`/projects/${projectId}/recent`"
            class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors pl-5"
            active-class="bg-gray-700 text-white"
          >
            <span>直近のタスク</span>
          </router-link>

          <router-link
            :to="`/projects/${projectId}/progress`"
            class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors pl-5"
            active-class="bg-gray-700 text-white"
          >
            <span>進捗一覧</span>
          </router-link>


          <router-link
            :to="`/projects/${projectId}/reviews`"
            class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors pl-5"
            active-class="bg-gray-700 text-white"
          >
            <span>レビュー</span>
          </router-link>

          <router-link
            :to="`/projects/${projectId}/quarters`"
            class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors pl-5"
            active-class="bg-gray-700 text-white"
          >
            <span>クォーター管理</span>
          </router-link>

          <router-link
            :to="`/projects/${projectId}/members`"
            class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors pl-5"
            active-class="bg-gray-700 text-white"
          >
            <span>メンバー管理</span>
          </router-link>
        </template>
      </nav>

      <!-- ユーザー情報・ログアウト -->
      <div class="border-t border-gray-700 px-3 py-3 text-sm space-y-0.5">
        <router-link
          to="/profile"
          class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors truncate"
          active-class="bg-gray-700 text-white"
        >
          <span class="truncate">{{ authStore.currentUser?.display_name }}</span>
        </router-link>
        <button
          id="app_layout__logout_btn"
          class="w-full text-left flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors text-gray-400 hover:text-white"
          @click="handleLogout"
        >
          ログアウト
        </button>
      </div>
    </aside>

    <!-- メインコンテンツ -->
    <main id="app_layout__main" class="flex-1 overflow-auto">
      <div class="px-4 py-4">
        <slot />
      </div>
    </main>

    <!-- 画面遷移中ローディングオーバーレイ -->
    <div v-if="isPageLoading" class="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-[500]">
      <div class="bg-white rounded-lg shadow-lg px-6 py-4 flex items-center gap-3">
        <svg class="animate-spin w-5 h-5 text-blue-600 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 22 6.477 22 12h-4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
        <span class="text-sm text-sky-900">読み込み中...</span>
      </div>
    </div>

  </div>
</template>
