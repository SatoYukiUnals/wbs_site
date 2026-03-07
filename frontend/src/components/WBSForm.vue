<script setup lang="ts">
import { ref, watch } from 'vue'
import type { WBSItem, WBSItemCreate } from '../types/wbs'

interface Props {
  item?: WBSItem | null
  allItems: WBSItem[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [data: WBSItemCreate]
  cancel: []
}>()

const form = ref<WBSItemCreate>({
  title: '',
  description: '',
  status: 'not_started',
  priority: 2,
  assignee: '',
  start_date: null,
  end_date: null,
  progress: 0,
  parent: null,
  order: 0,
})

watch(() => props.item, (newItem) => {
  if (newItem) {
    form.value = {
      title: newItem.title,
      description: newItem.description,
      status: newItem.status,
      priority: newItem.priority,
      assignee: newItem.assignee,
      start_date: newItem.start_date,
      end_date: newItem.end_date,
      progress: newItem.progress,
      parent: newItem.parent,
      order: newItem.order,
    }
  } else {
    form.value = {
      title: '',
      description: '',
      status: 'not_started',
      priority: 2,
      assignee: '',
      start_date: null,
      end_date: null,
      progress: 0,
      parent: null,
      order: 0,
    }
  }
}, { immediate: true })

const handleSubmit = () => {
  if (!form.value.title.trim()) {
    alert('タイトルは必須です')
    return
  }
  emit('submit', { ...form.value })
}

const flatItems = (items: WBSItem[], depth = 0): { item: WBSItem; depth: number }[] => {
  const result: { item: WBSItem; depth: number }[] = []
  for (const item of items) {
    if (!props.item || item.id !== props.item.id) {
      result.push({ item, depth })
      if (item.children && item.children.length > 0) {
        result.push(...flatItems(item.children, depth + 1))
      }
    }
  }
  return result
}
</script>

<template>
  <div class="wbs-form">
    <h2>{{ item ? 'タスク編集' : '新規タスク追加' }}</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>タイトル <span class="required">*</span></label>
        <input v-model="form.title" type="text" class="form-control" placeholder="タイトルを入力" required />
      </div>

      <div class="form-group">
        <label>説明</label>
        <textarea v-model="form.description" class="form-control" rows="3" placeholder="説明を入力"></textarea>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>ステータス</label>
          <select v-model="form.status" class="form-control">
            <option value="not_started">未着手</option>
            <option value="in_progress">進行中</option>
            <option value="completed">完了</option>
            <option value="on_hold">保留</option>
          </select>
        </div>

        <div class="form-group">
          <label>優先度</label>
          <select v-model.number="form.priority" class="form-control">
            <option :value="1">低</option>
            <option :value="2">中</option>
            <option :value="3">高</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>担当者</label>
        <input v-model="form.assignee" type="text" class="form-control" placeholder="担当者名を入力" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>開始日</label>
          <input v-model="form.start_date" type="date" class="form-control" />
        </div>

        <div class="form-group">
          <label>終了日</label>
          <input v-model="form.end_date" type="date" class="form-control" />
        </div>
      </div>

      <div class="form-group">
        <label>進捗率: {{ form.progress }}%</label>
        <input v-model.number="form.progress" type="range" min="0" max="100" class="form-range" />
      </div>

      <div class="form-group">
        <label>親タスク</label>
        <select v-model.number="form.parent" class="form-control">
          <option :value="null">なし（ルートタスク）</option>
          <option
            v-for="{ item: parentItem, depth } in flatItems(allItems)"
            :key="parentItem.id"
            :value="parentItem.id"
          >
            {{ '　'.repeat(depth) }}{{ parentItem.title }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>順序</label>
        <input v-model.number="form.order" type="number" class="form-control" min="0" />
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="emit('cancel')">キャンセル</button>
        <button type="submit" class="btn btn-primary">{{ item ? '更新' : '追加' }}</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.wbs-form h2 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  color: #555;
  font-size: 0.875rem;
}

.required {
  color: #e74c3c;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.875rem;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-range {
  width: 100%;
  cursor: pointer;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
</style>
