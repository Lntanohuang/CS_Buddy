<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Expand, Fold } from '@element-plus/icons-vue'
import NotificationBadge from '@/components/notice/NotificationBadge.vue'
import { useAuthStore } from '@/stores/auth'
import defaultAvatar from '@/assets/avatar-default.svg'
import { useNotificationStore } from '@/stores/notification'
import { useLayoutStore } from '@/stores/layout'

const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const layoutStore = useLayoutStore()
const isMobile = ref(typeof window !== 'undefined' ? window.innerWidth < 960 : false)

function handleResize() {
  if (typeof window === 'undefined') return
  isMobile.value = window.innerWidth < 960
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

const pageMetaMap: Record<string, string> = {
  chat: '对话课堂',
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
const recommendationText = computed(() => {
  const recommendation = notificationStore.todayRecommendation
  return `${recommendation.title} · ${recommendation.est_minutes} 分钟`
})
</script>

<template>
  <header class="topbar">
    <div class="topbar__left">
      <button
        v-if="isMobile"
        class="topbar__menu"
        type="button"
        :aria-label="layoutStore.isCollapse ? '打开侧边栏' : '折叠侧边栏'"
        @click="layoutStore.toggleCollapse()"
      >
        <el-icon :size="18">
          <component :is="layoutStore.isCollapse ? Expand : Fold" />
        </el-icon>
      </button>
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
        <div class="topbar__user-avatar">
          <img :src="defaultAvatar" :alt="displayName" />
        </div>
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
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom: 0;
  box-shadow: var(--shadow-sm);
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

.topbar__menu {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-primary);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
}

.topbar__menu:hover {
  background: var(--bg-hover);
  color: var(--accent-primary);
  border-color: color-mix(in srgb, var(--accent-primary) 20%, var(--border));
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
  background: var(--border);
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
  background: var(--bg-hover);
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
  background: var(--bg-hover);
}

.topbar__user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: transparent;
  overflow: hidden;
  border: 1px solid var(--border);
}

.topbar__user-avatar img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
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

@media (min-width: 960px) {
  .topbar__menu {
    display: none;
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
