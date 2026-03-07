<script setup lang="ts">
import type { WBSItem } from '../types/wbs'

interface Props {
  items: WBSItem[]
}

defineProps<Props>()

const emit = defineEmits<{
  edit: [item: WBSItem]
  delete: [id: number]
}>()

const statusConfig: Record<string, { label: string; color: string }> = {
  not_started: { label: '未着手', color: '#95a5a6' },
  in_progress: { label: '進行中', color: '#3498db' },
  completed: { label: '完了', color: '#2ecc71' },
  on_hold: { label: '保留', color: '#f39c12' },
}

const priorityConfig: Record<number, { label: string; color: string }> = {
  1: { label: '低', color: '#2ecc71' },
  2: { label: '中', color: '#f39c12' },
  3: { label: '高', color: '#e74c3c' },
}

const formatDate = (date: string | null): string => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('ja-JP')
}

const renderItems = (items: WBSItem[], depth = 0): { item: WBSItem; depth: number }[] => {
  const result: { item: WBSItem; depth: number }[] = []
  for (const item of items) {
    result.push({ item, depth })
    if (item.children && item.children.length > 0) {
      result.push(...renderItems(item.children, depth + 1))
    }
  }
  return result
}
</script>

<template>
  <div class="wbs-table-container">
    <div v-if="items.length === 0" class="empty-state">
      <p>タスクがありません。「新規タスク追加」ボタンからタスクを追加してください。</p>
    </div>
    <table v-else class="wbs-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>タイトル</th>
          <th>担当者</th>
          <th>開始日</th>
          <th>終了日</th>
          <th>進捗</th>
          <th>ステータス</th>
          <th>優先度</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="{ item, depth } in renderItems(items)" :key="item.id">
          <td>{{ item.id }}</td>
          <td>
            <span :style="{ paddingLeft: depth * 20 + 'px' }">
              <span v-if="depth > 0" class="child-indicator">└ </span>
              {{ item.title }}
            </span>
          </td>
          <td>{{ item.assignee || '-' }}</td>
          <td>{{ formatDate(item.start_date) }}</td>
          <td>{{ formatDate(item.end_date) }}</td>
          <td>
            <div class="progress-container">
              <div class="progress-bar" :style="{ width: item.progress + '%' }"></div>
              <span class="progress-text">{{ item.progress }}%</span>
            </div>
          </td>
          <td>
            <span
              class="badge"
              :style="{ backgroundColor: statusConfig[item.status]?.color || '#999' }"
            >
              {{ statusConfig[item.status]?.label || item.status }}
            </span>
          </td>
          <td>
            <span
              class="badge"
              :style="{ backgroundColor: priorityConfig[item.priority]?.color || '#999' }"
            >
              {{ priorityConfig[item.priority]?.label || item.priority }}
            </span>
          </td>
          <td>
            <button class="btn btn-sm btn-success" @click="emit('edit', item)">編集</button>
            <button class="btn btn-sm btn-danger" style="margin-left: 4px" @click="emit('delete', item.id)">削除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.wbs-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.wbs-table {
  width: 100%;
  border-collapse: collapse;
}

.wbs-table th,
.wbs-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.wbs-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
  font-size: 0.875rem;
}

.wbs-table tr:hover {
  background-color: #f8f9fa;
}

.child-indicator {
  color: #aaa;
}

.progress-container {
  position: relative;
  background-color: #eee;
  border-radius: 4px;
  height: 20px;
  min-width: 80px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #3498db;
  transition: width 0.3s;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: #333;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
}
</style>
