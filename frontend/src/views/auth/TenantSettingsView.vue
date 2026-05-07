<script setup lang="ts">
// 01-03-00 テナント設定画面（master のみ更新可）
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'

const authStore = useAuthStore()
const isMaster = authStore.currentUser?.role === 'master'

const isLoading = ref(true)
const isSavingName = ref(false)
const isSavingWeekdays = ref(false)

const tenantName = ref('')
const holidayWeekdays = ref<number[]>([])  // 0=月..6=日

const message = ref<{ type: 'ok' | 'err'; text: string } | null>(null)

// 会社休日一覧
const holidays = ref<{ id: string; date: string; name: string }[]>([])
const newHoliday = reactive({ date: '', name: '' })

const WEEKDAY_LABELS = ['月', '火', '水', '木', '金', '土', '日']

onMounted(async () => {
  const [t, hs] = await Promise.all([
    api.auth.getTenant(),
    api.auth.listTenantHolidays(),
  ])
  tenantName.value = t.name
  holidayWeekdays.value = [...t.holiday_weekdays]
  holidays.value = hs
  isLoading.value = false
})

const saveName = async () => {
  if (!tenantName.value.trim()) return
  isSavingName.value = true
  message.value = null
  try {
    const updated = await api.auth.updateTenant({
      name: tenantName.value.trim(),
    })
    tenantName.value = updated.name
    message.value = { type: 'ok', text: 'テナント名を更新しました。' }
  } catch (err) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const e = err as any
    message.value = {
      type: 'err',
      text: e.response?.data?.detail ?? '更新に失敗しました。',
    }
  } finally {
    isSavingName.value = false
  }
}

const toggleWeekday = (n: number) => {
  if (!isMaster) return
  const idx = holidayWeekdays.value.indexOf(n)
  if (idx === -1) holidayWeekdays.value.push(n)
  else holidayWeekdays.value.splice(idx, 1)
}

const saveWeekdays = async () => {
  isSavingWeekdays.value = true
  message.value = null
  try {
    const updated = await api.auth.updateTenant({
      holiday_weekdays: [...holidayWeekdays.value],
    })
    holidayWeekdays.value = [...updated.holiday_weekdays]
    message.value = { type: 'ok', text: '休みの曜日を更新しました。' }
  } catch (err) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const e = err as any
    message.value = {
      type: 'err',
      text: e.response?.data?.detail ?? '更新に失敗しました。',
    }
  } finally {
    isSavingWeekdays.value = false
  }
}

const addHoliday = async () => {
  if (!newHoliday.date) return
  const created = await api.auth.addTenantHoliday(
    newHoliday.date, newHoliday.name.trim(),
  )
  // 既存と重複していなければ追加
  if (!holidays.value.find(h => h.date === created.date)) {
    holidays.value.push(created)
    holidays.value.sort((a, b) => a.date.localeCompare(b.date))
  }
  newHoliday.date = ''
  newHoliday.name = ''
}

const removeHoliday = async (date: string) => {
  await api.auth.removeTenantHoliday(date)
  holidays.value = holidays.value.filter(h => h.date !== date)
}
</script>

<template>
  <div id="tenant_settings__container" class="max-w-2xl">
    <h1 class="text-xl font-bold text-sky-900 mb-4">テナント設定</h1>

    <div v-if="isLoading" class="text-gray-500 py-8 text-center">読み込み中...</div>

    <template v-else>
      <!-- テナント名 -->
      <section class="bg-white rounded-lg shadow p-6 mb-4">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">テナント名</h2>
        <div class="flex items-center gap-2">
          <input
            v-model="tenantName"
            type="text"
            :disabled="!isMaster"
            maxlength="100"
            class="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
          />
          <button
            v-if="isMaster"
            :disabled="isSavingName || !tenantName.trim()"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            @click="saveName"
          >
            {{ isSavingName ? '保存中...' : '保存' }}
          </button>
        </div>
        <p v-if="!isMaster" class="text-xs text-gray-500 mt-1">
          テナント名の変更は master ロールのみ可能です。
        </p>
      </section>

      <!-- 休みの曜日 -->
      <section class="bg-white rounded-lg shadow p-6 mb-4">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">休みの曜日（毎週）</h2>
        <div class="flex items-center flex-wrap gap-3 mb-3">
          <label
            v-for="(label, i) in WEEKDAY_LABELS"
            :key="i"
            class="inline-flex items-center gap-1 text-sm cursor-pointer select-none"
            :class="!isMaster ? 'opacity-60 cursor-not-allowed' : ''"
          >
            <input
              type="checkbox"
              :checked="holidayWeekdays.includes(i)"
              :disabled="!isMaster"
              @change="toggleWeekday(i)"
            />
            {{ label }}
          </label>
        </div>
        <div class="flex justify-end">
          <button
            v-if="isMaster"
            :disabled="isSavingWeekdays"
            class="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            @click="saveWeekdays"
          >
            {{ isSavingWeekdays ? '保存中...' : '保存' }}
          </button>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          チェックを入れた曜日は毎週の会社休みとして扱われます。自動割り振りはこの曜日をスキップします。
        </p>
      </section>

      <!-- 会社休日（個別日） -->
      <section class="bg-white rounded-lg shadow p-6 mb-4">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">会社休日（個別の日）</h2>
        <div v-if="isMaster" class="flex items-center gap-2 mb-3">
          <input
            v-model="newHoliday.date"
            type="date"
            class="border border-gray-300 rounded px-3 py-2 text-sm"
          />
          <input
            v-model="newHoliday.name"
            type="text"
            placeholder="名称（任意）"
            class="flex-1 border border-gray-300 rounded px-3 py-2 text-sm"
          />
          <button
            :disabled="!newHoliday.date"
            class="bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            @click="addHoliday"
          >
            追加
          </button>
        </div>
        <div v-if="holidays.length === 0" class="text-xs text-gray-500">
          会社休日は登録されていません。
        </div>
        <ul v-else class="divide-y divide-gray-200 border border-gray-200 rounded">
          <li
            v-for="h in holidays" :key="h.id"
            class="flex items-center px-3 py-2 text-sm"
          >
            <span class="font-mono text-sky-900 w-32">{{ h.date }}</span>
            <span class="flex-1 text-gray-700">{{ h.name || '—' }}</span>
            <button
              v-if="isMaster"
              class="text-red-500 hover:text-red-700 text-xs"
              @click="removeHoliday(h.date)"
            >
              削除
            </button>
          </li>
        </ul>
        <p class="text-xs text-gray-500 mt-2">
          指定した日付は自動割り振りでスキップされます。祝日・年末年始などをここで登録します。
        </p>
      </section>

      <p
        v-if="message"
        :class="message.type === 'ok' ? 'text-green-600' : 'text-red-600'"
        class="text-sm"
      >
        {{ message.text }}
      </p>
    </template>
  </div>
</template>
