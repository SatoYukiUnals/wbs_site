<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { mockProjects } from '@/mocks/data'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const projectId = computed(() => route.params.projectId as string | undefined)
const currentProject = computed(() =>
  projectId.value ? mockProjects.find(p => p.id === projectId.value) : null
)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex">

    <!-- サイドバー -->
    <aside class="w-52 bg-gray-900 text-gray-200 flex-shrink-0 flex flex-col">

      <!-- ロゴ -->
      <div class="px-4 py-4 border-b border-gray-700">
        <router-link to="/dashboard" class="font-bold text-base text-white hover:opacity-80 block">
          WBS管理
        </router-link>
      </div>

      <!-- ナビゲーション -->
      <nav class="flex-1 px-3 py-4 overflow-y-auto text-sm space-y-0.5">

        <!-- グローバルメニュー -->
        <p class="text-xs text-gray-500 px-2 py-1 uppercase tracking-wide">メニュー</p>

        <router-link
          to="/dashboard"
          class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors"
          active-class="bg-gray-700 text-white"
        >
          <span>ダッシュボード</span>
        </router-link>

        <router-link
          to="/projects"
          class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors"
          active-class="bg-gray-700 text-white"
        >
          <span>プロジェクト一覧</span>
        </router-link>

        <router-link
          to="/templates"
          class="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors"
          active-class="bg-gray-700 text-white"
        >
          <span>テンプレート</span>
        </router-link>

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
          class="w-full text-left flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-700 transition-colors text-gray-400 hover:text-white"
          @click="handleLogout"
        >
          ログアウト
        </button>
      </div>
    </aside>

    <!-- メインコンテンツ -->
    <main class="flex-1 overflow-auto">
      <div class="px-4 py-4">
        <slot />
      </div>
    </main>

  </div>
</template>
