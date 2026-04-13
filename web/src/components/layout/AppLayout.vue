<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ChatDotRound, Guide, EditPen, User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const menuItems = [
  { title: 'Chat', icon: ChatDotRound, route: '/app/chat' },
  { title: 'Learning Path', icon: Guide, route: '/app/path' },
  { title: 'Evaluation', icon: EditPen, route: '/app/evaluate' },
  { title: 'Profile', icon: User, route: '/app/profile' },
]

function handleMenuSelect(index: string) {
  router.push(index)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <h1>智伴</h1>
      </div>
      <el-menu
        :default-active="route.path"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item v-for="item in menuItems" :key="item.route" :index="item.route">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </aside>

    <div class="main-wrapper">
      <header class="top-bar">
        <div class="top-bar-spacer" />
        <div class="top-bar-right">
          <span class="user-nickname">{{ authStore.nickname }}</span>
          <el-button text @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <main class="main-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #1d1e1f;
  display: flex;
  flex-direction: column;
}

.sidebar-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-logo h1 {
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 2px;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  flex: 1;
}

.sidebar-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.7);
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  color: #fff;
  background: rgba(64, 158, 255, 0.2);
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  height: 56px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.top-bar-spacer {
  flex: 1;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-nickname {
  font-size: 14px;
  color: #606266;
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}
</style>
