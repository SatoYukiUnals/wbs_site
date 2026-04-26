<script setup lang="ts">
// 06-01-00 プロダクトロードマップ画面
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { mockRoadmapItems, mockQuarters } from '@/mocks/data'
import type { RoadmapItem, RoadmapStatus } from '@/types'

const route = useRoute()
const authStore = useAuthStore()
const projectId = route.params.projectId as string

const quarters = mockQuarters.filter(q => q.project_id === projectId)
const items = ref<RoadmapItem[]>(mockRoadmapItems.filter(i => i.project_id === projectId))
const isAdmin = authStore.currentUser?.role !== 'member'

/** クォーターごとのアイテム一覧を返す */
const itemsForQuarter = (quarterId: string) =>
  items.value.filter(i => i.quarter_id === quarterId)

/** ステータスに対応する色クラス */
const statusColor = (status: RoadmapStatus): string => {
  const map: Record<RoadmapStatus, string> = {
    '計画中': 'bg-gray-100 text-gray-600 border-gray-200',
    '進行中': 'bg-blue-50 text-blue-700 border-blue-200',
    '完了': 'bg-green-50 text-green-700 border-green-200',
    '保留': 'bg-red-50 text-red-600 border-red-200',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600 border-gray-200'
}

/** 削除ダイアログ */
const showDeleteDialog = ref(false)
const deleteTargetId = ref('')

const handleDelete = () => {
  items.value = items.value.filter(i => i.id !== deleteTargetId.value)
  showDeleteDialog.value = false
}
</script>

<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">プロダクトロードマップ</h1>
    </div>

    <div v-if="isAdmin" class="flex justify-end mb-4">
      <router-link
        :to="`/projects/${projectId}/roadmap/new`"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
      >
        + アイテム追加
      </router-link>
    </div>

    <!-- マトリクス表示（クォーター × アイテム） -->
    <div class="grid gap-6" :style="{ gridTemplateColumns: `repeat(${quarters.length}, minmax(200px, 1fr))` }">
      <div v-for="quarter in quarters" :key="quarter.id">
        <!-- クォーターヘッダー -->
        <div class="bg-gray-700 text-white text-sm font-medium px-4 py-2 rounded-t mb-2">
          {{ quarter.title }}
          <span class="text-gray-300 text-xs ml-2">{{ quarter.start_date }} 〜 {{ quarter.end_date }}</span>
        </div>

        <!-- アイテムカード一覧 -->
        <div class="space-y-2 min-h-[120px]">
          <div
            v-for="item in itemsForQuarter(quarter.id)"
            :key="item.id"
            data-testid="roadmap-item-card"
            :class="statusColor(item.status)"
            class="border rounded p-3"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ item.title }}</p>
                <p class="text-xs mt-0.5 truncate opacity-80">{{ item.description }}</p>
              </div>
              <span :class="statusColor(item.status)" class="text-xs px-1.5 py-0.5 rounded border flex-shrink-0">
                {{ item.status }}
              </span>
            </div>
            <div v-if="isAdmin" class="flex gap-2 mt-2">
              <router-link
                :to="`/projects/${projectId}/roadmap/${item.id}/edit`"
                class="text-xs text-blue-600 hover:underline"
              >
                編集
              </router-link>
              <button
                class="text-xs text-red-500 hover:text-red-700"
                @click="deleteTargetId = item.id; showDeleteDialog = true"
              >
                削除
              </button>
            </div>
          </div>

          <div
            v-if="itemsForQuarter(quarter.id).length === 0"
            class="text-gray-300 text-xs text-center py-4"
          >
            アイテムなし
          </div>
        </div>
      </div>
    </div>

    <!-- 削除確認ダイアログ -->
    <div
      v-if="showDeleteDialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">このアイテムを削除しますか？</p>
        <div class="flex justify-end gap-2">
          <button class="px-4 py-2 text-sm border rounded hover:bg-gray-50" @click="showDeleteDialog = false">
            キャンセル
          </button>
          <button class="px-4 py-2 text-sm text-white bg-red-500 rounded hover:bg-red-600" @click="handleDelete">
            削除する
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
