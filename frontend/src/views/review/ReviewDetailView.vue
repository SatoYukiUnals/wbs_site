<script setup lang="ts">
// 08-01-03 レビュー詳細画面
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import type { Review, ReviewComment, ReviewHistory, ReviewStatus } from '@/types'

const route = useRoute()
const authStore = useAuthStore()
const projectId = route.params.projectId as string
const taskId = route.params.taskId as string

const review = ref<Review | null>(null)
const comments = ref<ReviewComment[]>([])
const history = ref<ReviewHistory[]>([])
const currentStatus = ref<ReviewStatus>('pending')
const isAdmin = authStore.currentUser?.role !== 'member'
const isLoading = ref(true)
const newComment = ref('')

onMounted(async () => {
  const reviews = await api.reviews.list(projectId, taskId)
  if (reviews.length > 0) {
    review.value = reviews[0]
    currentStatus.value = reviews[0].status
    comments.value = await api.reviews.getComments(projectId, taskId, reviews[0].id)
  }
  isLoading.value = false
})

/** 完了ロック：承認済み or 完了の場合は操作不可 */
const isLocked = computed(() => currentStatus.value === '完了' || currentStatus.value === 'approved')

/** ステータスラベルと色 */
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

const statusLabel = (status: ReviewStatus): string => {
  const map: Record<ReviewStatus, string> = {
    pending: 'レビュー待ち', approved: '承認済み', rejected: '差し戻し', '確認待ち': '確認待ち', '完了': '完了',
  }
  return map[status] ?? status
}

/** 承認ダイアログ */
const showApproveDialog = ref(false)

const handleApprove = async () => {
  isLoading.value = true
  await api.reviews.approve(projectId, taskId)
  currentStatus.value = 'approved'
  history.value.push({
    id: `rh${Date.now()}`,
    review_id: review.value?.id ?? '',
    action: 'approve',
    user_id: authStore.currentUser?.id ?? '',
    user_name: authStore.currentUser?.display_name ?? '',
    created_at: new Date().toISOString(),
  })
  isLoading.value = false
  showApproveDialog.value = false
}

/** 差し戻しダイアログ */
const showRejectDialog = ref(false)
const rejectReason = ref('')

const handleReject = async () => {
  if (!rejectReason.value.trim()) return
  isLoading.value = true
  await api.reviews.reject(projectId, taskId, rejectReason.value)
  currentStatus.value = 'rejected'
  history.value.push({
    id: `rh${Date.now()}`,
    review_id: review.value?.id ?? '',
    action: 'reject',
    user_id: authStore.currentUser?.id ?? '',
    user_name: authStore.currentUser?.display_name ?? '',
    created_at: new Date().toISOString(),
  })
  isLoading.value = false
  showRejectDialog.value = false
  rejectReason.value = ''
}

/** コメント投稿 */
const handleAddComment = async () => {
  if (!newComment.value.trim() || !review.value) return
  isLoading.value = true
  const added = await api.reviews.addComment(projectId, taskId, review.value.id, newComment.value.trim())
  comments.value.push(added)
  newComment.value = ''
  isLoading.value = false
}
</script>

<template>
  <div v-if="isLoading" class="text-gray-500 py-8 text-center">読み込み中...</div>
  <div v-else-if="!review" class="text-gray-500 py-8 text-center">
    レビューが見つかりません
  </div>

  <div v-else id="review_detail__container" class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <router-link :to="`/projects/${projectId}/reviews`" class="text-blue-600 hover:underline text-sm">
        ← レビュー一覧
      </router-link>
      <h1 class="text-xl font-bold text-sky-900">レビュー詳細</h1>
      <span :class="statusColor(currentStatus)" class="px-2 py-0.5 rounded-full text-xs ml-auto">
        {{ statusLabel(currentStatus) }}
      </span>
    </div>

    <!-- タスク情報 -->
    <div class="bg-white rounded-lg shadow p-5 mb-4">
      <h2 class="text-sm font-semibold text-gray-600 mb-2">対象タスク</h2>
      <p class="font-medium text-sky-900">{{ review!.task_title }}</p>
    </div>

    <!-- アクションボタン（管理者のみ、未ロック時） -->
    <div v-if="isAdmin && !isLocked" class="flex gap-2 mb-4">
      <button
        id="review_detail__approve_btn"
        class="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700"
        data-testid="approve-button"
        @click="showApproveDialog = true"
      >
        承認する
      </button>
      <button
        id="review_detail__reject_btn"
        class="bg-red-500 text-white px-4 py-2 rounded text-sm hover:bg-red-600"
        data-testid="reject-button"
        @click="showRejectDialog = true"
      >
        差し戻す
      </button>
    </div>

    <!-- 完了ロック時のメッセージ -->
    <div v-if="isLocked" class="bg-gray-50 border border-gray-200 rounded p-3 mb-4 text-sm text-gray-500">
      このレビューは完了済みのため、操作できません。
    </div>

    <!-- コメント一覧 -->
    <div class="bg-white rounded-lg shadow p-5 mb-4">
      <h2 class="text-sm font-semibold text-gray-600 mb-3">コメント</h2>
      <div class="space-y-3">
        <div
          v-for="comment in comments"
          :key="comment.id"
          :id="`review_detail__comment_${comment.id}`"
          data-testid="review-comment"
          class="border-b pb-3 last:border-0 last:pb-0"
        >
          <div class="flex items-center gap-2 mb-1">
            <span class="text-sm font-medium text-gray-700">{{ comment.author_name }}</span>
            <span class="text-xs text-gray-400">{{ comment.created_at.slice(0, 16).replace('T', ' ') }}</span>
          </div>
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ comment.body }}</p>
        </div>
        <p v-if="comments.length === 0" class="text-sm text-gray-400">コメントはありません</p>
      </div>

      <!-- コメント入力（未ロック時） -->
      <div v-if="!isLocked" class="mt-4">
        <textarea
          id="review_detail__comment_textarea"
          v-model="newComment"
          rows="2"
          placeholder="コメントを入力..."
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <div class="flex justify-end mt-2">
          <button
            id="review_detail__submit_comment_btn"
            :disabled="!newComment.trim() || isLoading"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            @click="handleAddComment"
          >
            投稿
          </button>
        </div>
      </div>
    </div>

    <!-- 履歴 -->
    <div class="bg-white rounded-lg shadow p-5">
      <h2 class="text-sm font-semibold text-gray-600 mb-3">履歴</h2>
      <div class="space-y-2">
        <div
          v-for="h in history"
          :key="h.id"
          :id="`review_detail__history_${h.id}`"
          class="flex items-center gap-2 text-sm text-gray-600"
        >
          <span class="text-xs text-gray-400">{{ h.created_at.slice(0, 16).replace('T', ' ') }}</span>
          <span class="font-medium text-gray-700">{{ h.user_name }}</span>
          <span>が</span>
          <span>{{ h.action }}</span>
        </div>
        <p v-if="history.length === 0" class="text-sm text-gray-400">履歴はありません</p>
      </div>
    </div>

    <!-- 承認確認ダイアログ -->
    <div
      v-if="showApproveDialog"
      id="review_detail__approve_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-80">
        <p class="text-sky-900 mb-4">このレビューを承認しますか？</p>
        <div class="flex justify-end gap-2">
          <button id="review_detail__approve_cancel_btn" class="px-4 py-2 text-sm border rounded hover:bg-gray-50" @click="showApproveDialog = false">
            キャンセル
          </button>
          <button
            id="review_detail__approve_confirm_btn"
            class="px-4 py-2 text-sm text-white bg-green-600 rounded hover:bg-green-700 disabled:opacity-50"
            :disabled="isLoading"
            @click="handleApprove"
          >
            承認する
          </button>
        </div>
      </div>
    </div>

    <!-- 差し戻しダイアログ -->
    <div
      v-if="showRejectDialog"
      id="review_detail__reject_dialog"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-96">
        <h2 class="text-base font-semibold mb-3">差し戻し理由</h2>
        <textarea
          id="review_detail__reject_reason_textarea"
          v-model="rejectReason"
          rows="3"
          placeholder="差し戻し理由を入力してください"
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-4"
        />
        <div class="flex justify-end gap-2">
          <button id="review_detail__reject_cancel_btn" class="px-4 py-2 text-sm border rounded hover:bg-gray-50" @click="showRejectDialog = false">
            キャンセル
          </button>
          <button
            id="review_detail__reject_confirm_btn"
            :disabled="!rejectReason.trim() || isLoading"
            class="px-4 py-2 text-sm text-white bg-red-500 rounded hover:bg-red-600 disabled:opacity-50"
            @click="handleReject"
          >
            差し戻す
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
