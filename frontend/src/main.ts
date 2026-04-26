import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// トークンが残っていればログイン状態を復元してからルーターを開始する
const authStore = useAuthStore()
authStore.init().finally(() => {
  app.mount('#app')
})
