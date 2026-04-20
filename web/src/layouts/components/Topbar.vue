<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NotificationBadge from '@/components/notice/NotificationBadge.vue'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const authStore = useAuthStore()
const userStore = useUserStore()

const pageMetaMap: Record<string, string> = {
  chat: 'AI 对话课堂',
  path: '学习路径',
  evaluate: '测评中心',
  profile: '个人画像',
  notifications: '消息中心',
}

const currentTitle = computed(() => {
  const name = typeof route.name === 'string' ? route.name : ''
  return pageMetaMap[name] ?? 'CS Buddy'
})

const displayName = computed(() => authStore.nickname || userStore.userInfo.name)
const avatarText = computed(() => displayName.value.slice(0, 1).toUpperCase())
</script>

<template>
  <header class="topbar">
    <div class="topbar__left">
      <h1 class="topbar__title">{{ currentTitle }}</h1>
    </div>

    <div class="topbar__right">
      <NotificationBadge />

      <div class="topbar__user">
        <div class="topbar__user-avatar">{{ avatarText }}</div>
        <strong class="topbar__user-name">{{ displayName }}</strong>
      </div>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-height: 56px;
  padding: 10px 20px;
  background: linear-gradient(180deg, rgba(250, 250, 248, 0.96), rgba(250, 250, 248, 0.82));
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(55, 53, 47, 0.06);
}

.topbar__left,
.topbar__right {
  display: flex;
  align-items: center;
}

.topbar__right {
  gap: 12px;
}

.topbar__title {
  margin: 0;
  font-size: 20px;
  line-height: 1.2;
  color: var(--text-primary);
}

.topbar__user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 10px 4px 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
}

.topbar__user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--accent-primary);
  color: var(--bg-card);
  font-size: 12px;
  font-weight: 700;
}

.topbar__user-name {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 600;
}

.topbar :deep(.notification-trigger) {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  box-shadow: none;
}

@media (max-width: 720px) {
  .topbar {
    padding: 10px 16px;
  }

  .topbar__title {
    font-size: 18px;
  }

  .topbar__user-name {
    display: none;
  }
}
</style>
