import { ref } from 'vue'

/** 画面遷移中のローディング状態（Router と AppLayout で共有） */
export const isPageLoading = ref(false)
