// 認証ストア
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { mockCurrentUser } from '@/mocks/data'

export const useAuthStore = defineStore('auth', () => {
  // MOCKではadminユーザーとしてログイン済み状態を初期値とする
  const currentUser = ref<User | null>(mockCurrentUser)
  const isLoggedIn = ref(true)

  /**
   * ログイン処理（MOCK：常に成功）
   */
  const login = (_email: string, _password: string): boolean => {
    currentUser.value = mockCurrentUser
    isLoggedIn.value = true
    return true
  }

  /**
   * ログアウト処理
   */
  const logout = () => {
    currentUser.value = null
    isLoggedIn.value = false
  }

  return { currentUser, isLoggedIn, login, logout }
})
