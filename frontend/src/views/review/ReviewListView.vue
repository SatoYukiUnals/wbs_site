<script setup lang="ts">
// 08-01-00 レビュー一覧画面
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import type { Review, ReviewStatus } from '@/types'

const route = useRoute()
const projectId = route.params.projectId as string

const reviews = ref<Review[]>([])
const filterStatus = ref<ReviewStatus | ''>('')

onMounted(async () => {
  reviews.value = await api.reviews.listByProject(projectId)
})

const filteredReviews = computed<Review[]>(() =>
  filterStatus.value
    ? reviews.value.filter(r => r.status === filterStatus.value)
    : reviews.value
)

/** ステータスラベルと色 */
const statusLabel = (status: ReviewStatus): string => {
  const map: Record<ReviewStatus, string> = {
    pending: 'レビュー待ち',
    approved: '承認済み',
    rejected: '差し戻し',
    '確認待ち': '確認待ち',
    '完了': '完了',
  }
  return map[status] ?? status
}

const statusColor = (status: ReviewStatus): string => {
  const map: Record<ReviewStatus, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-600',
    '確認待ち': 'bg-blue-100 text-blue-700',
    '完了': 'bg-gray-100 text-gray-600',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}
</script>

<template>
  <div id="review_list__container">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}`" class="text-blue-600 hover:underline text-sm">
        ← プロジェクト詳細
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">レビュー一覧</h1>
    </div>

    <!-- フィルター -->
    <div id="review_list__filter_area" class="flex items-center gap-3 mb-4">
      <select
        id="review_list__status_select"
        v-model="filterStatus"
        class="border border-gray-300 rounded px-3 py-1.5 text-sm"
      >
        <option value="">ステータス：全て</option>
        <option value="pending">レビュー待ち</option>
        <option value="approved">承認済み</option>
        <option value="rejected">差し戻し</option>
        <option value="確認待ち">確認待ち</option>
        <option value="完了">完了</option>
      </select>
    </div>

    <!-- レビュー一覧テーブル -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table id="review_list__table" class="w-full text-sm">
        <thead id="review_list__thead" class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">タスク名</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">ステータス</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">レビュワー</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">依頼日</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody id="review_list__tbody">
          <tr
            v-for="review in filteredReviews"
            :key="review.id"
            :id="`review_list__row_${review.id}`"
            data-testid="review-row"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3 font-medium text-sky-900">{{ review.task_title }}</td>
            <td class="px-4 py-3">
              <span :class="statusColor(review.status)" class="px-2 py-0.5 rounded-full text-xs">
                {{ statusLabel(review.status) }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ review.reviewer_name ?? '未割り当て' }}</td>
            <td class="px-4 py-3 text-gray-600 text-xs">{{ review.created_at.slice(0, 10) }}</td>
            <td class="px-4 py-3 text-right">
              <router-link
                :to="`/projects/${projectId}/tasks/${review.task_id}/reviews`"
                class="text-blue-600 hover:underline text-xs"
              >
                詳細
              </router-link>
            </td>
          </tr>
          <tr v-if="filteredReviews.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">レビューがありません</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
