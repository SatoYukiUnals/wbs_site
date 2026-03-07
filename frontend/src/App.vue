<script setup lang="ts">
import { ref, onMounted } from 'vue'
import WBSTable from './components/WBSTable.vue'
import WBSForm from './components/WBSForm.vue'
import { wbsApi } from './api/wbs'
import type { WBSItem, WBSItemCreate } from './types/wbs'

const items = ref<WBSItem[]>([])
const loading = ref(false)
const showForm = ref(false)
const editingItem = ref<WBSItem | null>(null)
const error = ref<string | null>(null)

const fetchItems = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await wbsApi.getAll()
    items.value = response.data
  } catch (e) {
    error.value = 'データの取得に失敗しました'
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleCreate = async (data: WBSItemCreate) => {
  try {
    await wbsApi.create(data)
    await fetchItems()
    showForm.value = false
  } catch (e) {
    error.value = 'アイテムの作成に失敗しました'
    console.error(e)
  }
}

const handleUpdate = async (id: number, data: WBSItemCreate) => {
  try {
    await wbsApi.update(id, data)
    await fetchItems()
    editingItem.value = null
    showForm.value = false
  } catch (e) {
    error.value = 'アイテムの更新に失敗しました'
    console.error(e)
  }
}

const handleDelete = async (id: number) => {
  if (!confirm('このアイテムを削除しますか？')) return
  try {
    await wbsApi.delete(id)
    await fetchItems()
  } catch (e) {
    error.value = 'アイテムの削除に失敗しました'
    console.error(e)
  }
}

const handleEdit = (item: WBSItem) => {
  editingItem.value = item
  showForm.value = true
}

const handleCancel = () => {
  editingItem.value = null
  showForm.value = false
}

onMounted(fetchItems)
</script>

<template>
  <div class="app">
    <header class="header">
      <h1>📋 WBS管理システム</h1>
      <button class="btn btn-primary" @click="showForm = true; editingItem = null">
        ＋ 新規タスク追加
      </button>
    </header>

    <main class="main">
      <div v-if="error" class="error-message">{{ error }}</div>

      <div v-if="showForm" class="modal-overlay" @click.self="handleCancel">
        <div class="modal">
          <WBSForm
            :item="editingItem"
            :all-items="items"
            @submit="editingItem ? handleUpdate(editingItem.id, $event) : handleCreate($event)"
            @cancel="handleCancel"
          />
        </div>
      </div>

      <div v-if="loading" class="loading">読み込み中...</div>
      <WBSTable
        v-else
        :items="items"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </main>
  </div>
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

.app {
  min-height: 100vh;
}

.header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 1.5rem;
}

.main {
  padding: 2rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-success {
  background-color: #2ecc71;
  color: white;
}

.btn-success:hover {
  background-color: #27ae60;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.error-message {
  background-color: #fde8e8;
  color: #e74c3c;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #f5c6cb;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
</style>
