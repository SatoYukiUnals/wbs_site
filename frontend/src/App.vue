<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

const route = useRoute()

/** 認証画面はレイアウト不要 */
const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))
</script>

<template>
  <div class="text-sky-900">
    <!-- 認証画面はレイアウトなしで表示 -->
    <router-view v-if="isAuthPage" />
    <!-- それ以外はアプリレイアウト内で表示 -->
    <app-layout v-else>
      <router-view />
    </app-layout>
  </div>
</template>
