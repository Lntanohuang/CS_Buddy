<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Setting, SwitchButton } from '@element-plus/icons-vue'
import NotificationBadge from '@/components/notice/NotificationBadge.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const settingsVisible = ref(false)

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

function handleLogout() {
  settingsVisible.value = false
  authStore.logout()
  void router.push('/login')
}
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
      <NotificationBadge />

      <el-popover
        v-model:visible="settingsVisible"
        placement="bottom-end"
        trigger="click"
        :width="172"
      >
        <template #reference>
          <button class="topbar__settings" type="button" aria-label="打开设置">
            <el-icon :size="16"><Setting /></el-icon>
          </button>
        </template>

        <button class="topbar__settings-action" type="button" @click="handleLogout">
          <el-icon :size="15"><SwitchButton /></el-icon>
          <span>退出登录</span>
        </button>
      </el-popover>

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
.topbar__user {
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

.topbar__settings {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.84);
  color: var(--text-primary);
  cursor: pointer;
}

.topbar__settings-action {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  text-align: left;
}

.topbar__settings-action:hover {
  background: rgba(74, 124, 111, 0.08);
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

@media (max-width: 720px) {
  .topbar {
    padding: 10px 14px;
  }

  .topbar__divider,
  .topbar__brand-name,
  .topbar__user-name {
    display: none;
  }

  .topbar__title {
    font-size: 18px;
  }
}
</style>
