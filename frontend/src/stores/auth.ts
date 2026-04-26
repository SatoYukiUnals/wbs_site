// 認証ストア（JWT ベース）
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { api, getToken, setTokens, clearTokens } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref<User | null>(null)
  const isLoggedIn = ref(false)

  /** アプリ起動時にトークンが残っていればユーザー情報を復元する */
  const init = async (): Promise<void> => {
    if (!getToken()) return
    try {
      currentUser.value = await api.auth.getProfile()
      isLoggedIn.value = true
    } catch {
      clearTokens()
    }
  }

  /** ログイン処理 */
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const result = await api.auth.login(email, password)
      setTokens(result.access, result.refresh)
      currentUser.value = result.user
      isLoggedIn.value = true
      return true
    } catch {
      return false
    }
  }

  /** ログアウト処理 */
  const logout = (): void => {
    clearTokens()
    currentUser.value = null
    isLoggedIn.value = false
  }

  return { currentUser, isLoggedIn, init, login, logout }
})
