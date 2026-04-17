<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { ChatDotRound, Guide, EditPen, User } from '@element-plus/icons-vue'
import NotificationBell from '@/components/notification/NotificationBell.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const menuItems = [
  { title: '智能对话', icon: ChatDotRound, route: '/app/chat' },
  { title: '学习路径', icon: Guide, route: '/app/path' },
  { title: '知识测评', icon: EditPen, route: '/app/evaluate' },
  { title: '个人中心', icon: User, route: '/app/profile' },
]

const userInitials = computed(() => {
  const name = authStore.nickname || '?'
  return name.charAt(0).toUpperCase()
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-leaf">🌿</span>
        <span class="logo-name">CS Buddy</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.route"
          :to="item.route"
          class="nav-item"
          :class="{ 'is-active': route.path === item.route }"
        >
          <el-icon :size="17"><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-row">
          <div class="user-avatar">{{ userInitials }}</div>
          <span class="user-name">{{ authStore.nickname || '用户' }}</span>
        </div>
        <div class="footer-actions">
          <NotificationBell
            :count="notificationStore.unreadCount"
            @click="router.push('/app/notifications')"
          />
          <button class="logout-btn" @click="handleLogout">退出</button>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px 20px;
}

.logo-leaf {
  font-size: 20px;
}

.logo-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  color: var(--text-tertiary);
  font-size: 14px;
  font-weight: 450;
  text-decoration: none;
  transition: all 0.15s ease;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.is-active {
  background: var(--bg-hover);
  color: var(--text-primary);
  font-weight: 550;
}

.sidebar-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 8px 0;
  border-top: 1px solid var(--border);
  margin-top: 8px;
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.user-name {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 450;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: inherit;
  transition: all 0.15s ease;
}

.logout-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 32px;
  background: var(--bg-primary);
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
