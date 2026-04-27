<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChatDotRound,
  EditPen,
  Expand,
  Fold,
  Guide,
  Plus,
  Setting,
  SwitchButton,
  User,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useLayoutStore } from '@/stores/layout'

const props = defineProps<{
  isMobile: boolean
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const layoutStore = useLayoutStore()
const chatStore = useChatStore()
const settingsVisible = ref(false)

const menuItems = [
  { title: 'AI 对话课堂', icon: ChatDotRound, route: '/app/chat' },
  { title: '学习路径', icon: Guide, route: '/app/path' },
  { title: '测评中心', icon: EditPen, route: '/app/evaluate' },
  { title: '个人画像', icon: User, route: '/app/profile' },
]

const sessions = computed(() => chatStore.sessions)
const activeSessionId = computed(() => chatStore.activeSessionId)

function isActive(path: string) {
  return route.path === path || route.path.startsWith(`${path}/`)
}

function handleMenuClick() {
  if (props.isMobile) {
    layoutStore.setCollapse(true)
  }
}

function handleCreateSession() {
  chatStore.createSession()
  void router.push('/app/chat')

  if (props.isMobile) {
    layoutStore.setCollapse(true)
  }
}

function handleSelectSession(id: string) {
  chatStore.selectSession(id)
  void router.push('/app/chat')

  if (props.isMobile) {
    layoutStore.setCollapse(true)
  }
}

function handleLogout() {
  settingsVisible.value = false
  authStore.logout()
  void router.push('/login')
}

function formatSessionTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  if (diffHour < 24) return `${diffHour} 小时前`
  if (diffDay < 7) return `${diffDay} 天前`

  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
  })
}
</script>

<template>
  <aside
    class="sidebar"
    :class="{
      'is-collapse': layoutStore.isCollapse,
      'is-mobile': isMobile,
    }"
  >
    <div class="sidebar__top">
      <button
        class="sidebar__toggle"
        type="button"
        :aria-label="layoutStore.isCollapse ? '展开侧边栏' : '折叠侧边栏'"
        @click="layoutStore.toggleCollapse()"
      >
        <span class="sidebar__icon">
          <el-icon :size="18">
            <component :is="layoutStore.isCollapse ? Expand : Fold" />
          </el-icon>
        </span>
        <span class="sidebar__label">导航</span>
      </button>
    </div>

    <nav class="sidebar__nav">
      <router-link
        v-for="item in menuItems"
        :key="item.route"
        :to="item.route"
        class="sidebar__link"
        :class="{ 'is-active': isActive(item.route) }"
        :title="item.title"
        @click="handleMenuClick"
      >
        <span class="sidebar__icon">
          <el-icon :size="18">
            <component :is="item.icon" />
          </el-icon>
        </span>
        <span class="sidebar__label">{{ item.title }}</span>
      </router-link>
    </nav>

    <section class="sidebar__history">
      <div class="sidebar__history-header">
        <div>
          <p class="sidebar__eyebrow">历史对话</p>
          <h3 class="sidebar__history-title">最近会话</h3>
        </div>

        <button class="sidebar__new-chat" type="button" @click="handleCreateSession">
          <el-icon :size="14"><Plus /></el-icon>
          <span>新对话</span>
        </button>
      </div>

      <div class="sidebar__history-list">
        <button
          v-for="session in sessions"
          :key="session.session_id"
          class="sidebar__history-item"
          :class="{ 'is-active': session.session_id === activeSessionId }"
          type="button"
          @click="handleSelectSession(session.session_id)"
        >
          <span class="sidebar__history-item-title">{{ session.title }}</span>
          <span class="sidebar__history-item-time">{{ formatSessionTime(session.updated_at) }}</span>
        </button>
      </div>
    </section>

    <div class="sidebar__footer">
      <el-popover
        v-model:visible="settingsVisible"
        placement="top-start"
        trigger="click"
        :width="264"
        popper-class="sidebar-settings-popover"
      >
        <template #reference>
          <button
            class="sidebar__settings"
            type="button"
            aria-label="打开设置"
          >
            <span class="sidebar__icon">
              <el-icon :size="18"><Setting /></el-icon>
            </span>
            <span class="sidebar__label">设置</span>
          </button>
        </template>

        <div class="sidebar__settings-panel">
          <button class="sidebar__settings-action" type="button" @click="handleLogout">
            <el-icon :size="15"><SwitchButton /></el-icon>
            <span>退出登录</span>
          </button>
        </div>
      </el-popover>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 40;
  width: 304px;
  padding: 16px 12px 12px;
  background: var(--bg-card);
  border-right: 0;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: width 0.24s ease;
  display: flex;
  flex-direction: column;
}

.sidebar.is-collapse {
  width: 72px;
}

.sidebar__top {
  display: flex;
  justify-content: flex-start;
  padding-bottom: 12px;
}

.sidebar__toggle,
.sidebar__settings {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  align-items: center;
  width: 100%;
  min-height: 48px;
  padding: 0 10px 0 0;
  border: none;
  border-radius: 14px;
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}

.sidebar.is-collapse .sidebar__toggle,
.sidebar.is-collapse .sidebar__settings {
  padding-right: 0;
}

.sidebar__toggle:hover,
.sidebar__settings:hover {
  background: var(--bg-hover);
  color: var(--accent-primary);
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.sidebar__link {
  position: relative;
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  align-items: center;
  min-height: 48px;
  padding: 0 10px 0 0;
  border-radius: 14px;
  color: var(--text-tertiary);
  transition: background 0.18s ease, color 0.18s ease;
  white-space: nowrap;
}

.sidebar__link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar__link.is-active {
  background: var(--accent-primary-light);
  color: var(--accent-primary);
}

.sidebar__link.is-active::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 11px;
  bottom: 11px;
  width: 2px;
  border-radius: 999px;
  background: var(--accent-primary);
}

.sidebar__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  flex-shrink: 0;
}

.sidebar__label {
  font-size: 14px;
  font-weight: 500;
  opacity: 1;
  transform: translateX(0);
  transition: opacity 0.18s ease, transform 0.18s ease;
  overflow: hidden;
}

.sidebar.is-collapse .sidebar__label {
  opacity: 0;
  width: 0;
  transform: translateX(-6px);
}

.sidebar__history {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
  min-height: 0;
  margin-top: 16px;
  opacity: 1;
  transform: translateX(0);
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.sidebar.is-collapse .sidebar__history {
  opacity: 0;
  pointer-events: none;
  transform: translateX(-8px);
}

.sidebar__history-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.sidebar__eyebrow {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.sidebar__history-title {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
}

.sidebar__new-chat {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 32px;
  padding: 0 10px;
  border: none;
  border-radius: 999px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.sidebar__history-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 0;
  overflow: auto;
  padding-right: 2px;
}

.sidebar__history-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  padding: 12px 14px;
  border: none;
  border-radius: 14px;
  background: var(--bg-card);
  cursor: pointer;
  text-align: left;
  transition: background 0.18s ease, box-shadow 0.18s ease;
}

.sidebar__history-item:hover {
  background: var(--bg-hover);
  box-shadow: var(--shadow-sm);
}

.sidebar__history-item.is-active {
  background: var(--accent-primary-light);
  box-shadow: none;
}

.sidebar__history-item-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar__history-item-time {
  font-size: 11px;
  color: var(--text-secondary);
}

.sidebar__footer {
  display: flex;
  align-items: flex-end;
  padding-top: 12px;
}

.sidebar__settings-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
}

.sidebar__settings-action {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
}

.sidebar__settings-action:hover {
  background: var(--bg-hover);
}

@media (max-width: 959px) {
  .sidebar {
    width: min(84vw, 304px);
  }

  .sidebar.is-collapse {
    width: 72px;
  }
}

:global(.sidebar-settings-popover) {
  border-radius: 14px !important;
  padding: 6px !important;
}
</style>
