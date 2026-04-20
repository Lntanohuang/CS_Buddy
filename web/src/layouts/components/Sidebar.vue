<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChatDotRound, EditPen, Fold, Guide, Setting, SwitchButton, User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useLayoutStore } from '@/stores/layout'
import { useUserStore } from '@/stores/user'

defineProps<{
  isMobile: boolean
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const layoutStore = useLayoutStore()
const userStore = useUserStore()
const settingsVisible = ref(false)

const menuItems = [
  { title: 'AI 对话课堂', icon: ChatDotRound, route: '/app/chat' },
  { title: '学习路径', icon: Guide, route: '/app/path' },
  { title: '测评中心', icon: EditPen, route: '/app/evaluate' },
  { title: '个人画像', icon: User, route: '/app/profile' },
]

const displayName = computed(() => authStore.nickname || userStore.userInfo.name)
const avatarText = computed(() => displayName.value.slice(0, 1).toUpperCase())

function isActive(path: string) {
  return route.path === path || route.path.startsWith(`${path}/`)
}

function handleMenuClick() {
  if (typeof window !== 'undefined' && window.innerWidth < 960) {
    layoutStore.setCollapse(true)
  }
}

function handleLogout() {
  settingsVisible.value = false
  authStore.logout()
  layoutStore.setCollapse(typeof window !== 'undefined' ? window.innerWidth < 960 : false)
  void router.push('/login')
}
</script>

<template>
  <aside class="sidebar" :class="{ 'is-collapse': layoutStore.isCollapse }">
    <div class="sidebar__top">
      <div class="sidebar-logo">
        <span class="logo-leaf">🌶</span>
        <transition name="sidebar-fade">
          <span v-if="!layoutStore.isCollapse" class="logo-name">CS Buddy</span>
        </transition>
      </div>

      <button class="sidebar__toggle" type="button" @click="layoutStore.toggleCollapse()">
        <el-icon :size="18"><Fold /></el-icon>
      </button>
    </div>

    <nav class="sidebar__nav">
      <router-link
        v-for="item in menuItems"
        :key="item.route"
        :to="item.route"
        class="sidebar__link"
        :class="{ 'is-active': isActive(item.route) }"
        :title="layoutStore.isCollapse ? item.title : ''"
        @click="handleMenuClick"
      >
        <span class="sidebar__icon">
          <el-icon :size="18">
            <component :is="item.icon" />
          </el-icon>
        </span>
        <transition name="sidebar-fade">
          <span v-if="!layoutStore.isCollapse" class="sidebar__label">{{ item.title }}</span>
        </transition>
      </router-link>
    </nav>

    <div class="sidebar__footer">
      <div class="sidebar__user">
        <div class="sidebar__avatar">{{ avatarText }}</div>
        <transition name="sidebar-fade">
          <div v-if="!layoutStore.isCollapse" class="sidebar__user-copy">
            <strong>{{ displayName }}</strong>
            <span>{{ userStore.displayLevel }}</span>
          </div>
        </transition>
      </div>

      <el-popover
        v-model:visible="settingsVisible"
        placement="top-end"
        trigger="click"
        :width="168"
        popper-class="sidebar-settings-popover"
      >
        <template #reference>
          <button
            class="sidebar__settings"
            :class="{ 'is-collapse': layoutStore.isCollapse }"
            type="button"
            aria-label="打开设置"
          >
            <el-icon :size="16"><Setting /></el-icon>
            <transition name="sidebar-fade">
              <span v-if="!layoutStore.isCollapse">设置</span>
            </transition>
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
  position: relative;
  z-index: 35;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  padding: 18px 14px 16px;
  background:
    radial-gradient(circle at top left, rgba(232, 192, 122, 0.18), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 246, 243, 0.98));
  border-right: 1px solid rgba(55, 53, 47, 0.08);
  backdrop-filter: blur(18px);
}

.sidebar__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 4px 6px 18px;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-leaf {
  font-size: 20px;
  line-height: 1;
}

.logo-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.4px;
}

.sidebar__toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border: none;
  border-radius: 10px;
  background: rgba(55, 53, 47, 0.05);
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}

.sidebar__toggle:hover {
  background: rgba(74, 124, 111, 0.1);
  color: var(--accent-primary);
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.sidebar__link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 46px;
  padding: 0 14px;
  border-radius: 12px;
  color: var(--text-tertiary);
  transition: background 0.18s ease, color 0.18s ease;
}

.sidebar__link:hover {
  background: rgba(74, 124, 111, 0.08);
  color: var(--text-primary);
}

.sidebar__link.is-active {
  background: rgba(74, 124, 111, 0.05);
  color: var(--accent-primary);
}

.sidebar__link.is-active::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 10px;
  bottom: 10px;
  width: 2px;
  border-radius: 999px;
  background: var(--accent-primary);
}

.sidebar__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
}

.sidebar__label {
  font-size: 14px;
  font-weight: 500;
}

.sidebar__footer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid rgba(55, 53, 47, 0.08);
}

.sidebar__user {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.sidebar__avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--accent-primary);
  color: var(--bg-card);
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.sidebar__user-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.sidebar__user-copy strong {
  font-size: 13px;
  color: var(--text-primary);
}

.sidebar__user-copy span {
  font-size: 12px;
  color: var(--text-secondary);
}

.sidebar__settings {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 34px;
  padding: 0 12px;
  border: none;
  border-radius: 10px;
  background: rgba(55, 53, 47, 0.05);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}

.sidebar__settings:hover {
  background: rgba(74, 124, 111, 0.1);
  color: var(--accent-primary);
}

.sidebar__settings.is-collapse {
  width: 34px;
  padding: 0;
}

.sidebar__settings-panel {
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
  background: rgba(74, 124, 111, 0.08);
}

.sidebar-fade-enter-active,
.sidebar-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.sidebar-fade-enter-from,
.sidebar-fade-leave-to {
  opacity: 0;
  transform: translateX(-6px);
}

:global(.sidebar-settings-popover) {
  border-radius: 14px !important;
  padding: 6px !important;
}
</style>
