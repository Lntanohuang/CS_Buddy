<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NotificationBadge from '@/components/notice/NotificationBadge.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

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

const displayName = computed(() => authStore.nickname || '用户')
const avatarText = computed(() => displayName.value.slice(0, 1).toUpperCase())
const recommendationText = computed(() => {
  const recommendation = notificationStore.todayRecommendation
  return `${recommendation.title} · ${recommendation.est_minutes} 分钟`
})
</script>

<template>
  <header class="topbar">
    <div class="topbar__left">
      <div class="topbar__brand">
        <span class="topbar__logo">🌿</span>
        <strong class="topbar__brand-name">CS Buddy</strong>
      </div>
      <span class="topbar__divider" />
      <h1 class="topbar__title">{{ currentTitle }}</h1>
    </div>

    <div class="topbar__right">
      <div class="topbar__recommend" :title="notificationStore.todayRecommendation.reason">
        <span class="topbar__recommend-label">今日推荐</span>
        <span class="topbar__recommend-value">{{ recommendationText }}</span>
      </div>

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
  position: relative;
  z-index: 18;
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
.topbar__right,
.topbar__brand,
.topbar__user,
.topbar__recommend {
  display: flex;
  align-items: center;
}

.topbar__left {
  gap: 12px;
  min-width: 0;
}

.topbar__right {
  gap: 12px;
}

.topbar__brand {
  gap: 8px;
  flex-shrink: 0;
}

.topbar__logo {
  font-size: 18px;
  line-height: 1;
}

.topbar__brand-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 700;
}

.topbar__divider {
  width: 1px;
  height: 18px;
  background: rgba(55, 53, 47, 0.12);
}

.topbar__title {
  margin: 0;
  font-size: 19px;
  line-height: 1.2;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar__recommend {
  gap: 8px;
  max-width: 360px;
  padding: 0 12px;
  min-height: 36px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  white-space: nowrap;
}

.topbar__recommend-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-primary);
  letter-spacing: 0.04em;
}

.topbar__recommend-value {
  font-size: 12px;
  color: var(--text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar__user {
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

@media (max-width: 1100px) {
  .topbar__recommend {
    max-width: 250px;
  }
}

@media (max-width: 720px) {
  .topbar {
    padding: 10px 14px;
  }

  .topbar__divider,
  .topbar__brand-name,
  .topbar__recommend-label,
  .topbar__user-name {
    display: none;
  }

  .topbar__title {
    font-size: 18px;
  }

  .topbar__recommend {
    max-width: 140px;
    padding: 0 10px;
  }
}
</style>
