<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChatDotRound, EditPen, Guide, User, SwitchButton } from '@element-plus/icons-vue'
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
  authStore.logout()
  layoutStore.setCollapse(typeof window !== 'undefined' ? window.innerWidth < 960 : false)
  void router.push('/login')
}
</script>

<template>
  <aside class="sidebar" :class="{ 'is-collapse': layoutStore.isCollapse }">
    <div class="sidebar__brand">
      <div class="sidebar__brand-mark">CS</div>
      <transition name="sidebar-fade">
        <div v-if="!layoutStore.isCollapse" class="sidebar__brand-copy">
          <span class="sidebar__brand-eyebrow">AI Learning OS</span>
          <strong>CS Buddy</strong>
        </div>
      </transition>
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
        <div class="sidebar__avatar">
          <img v-if="userStore.userInfo.avatar" :src="userStore.userInfo.avatar" :alt="displayName" />
          <span v-else>{{ avatarText }}</span>
        </div>
        <transition name="sidebar-fade">
          <div v-if="!layoutStore.isCollapse" class="sidebar__user-copy">
            <strong>{{ displayName }}</strong>
            <span>{{ userStore.displayLevel }} / {{ userStore.displayPreferredStyle }}</span>
          </div>
        </transition>
      </div>

      <button
        class="sidebar__logout"
        :class="{ 'is-collapse': layoutStore.isCollapse }"
        type="button"
        @click="handleLogout"
      >
        <el-icon :size="16"><SwitchButton /></el-icon>
        <transition name="sidebar-fade">
          <span v-if="!layoutStore.isCollapse">退出登录</span>
        </transition>
      </button>
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
  padding: 22px 16px 18px;
  background:
    radial-gradient(circle at top left, rgba(232, 192, 122, 0.18), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 246, 243, 0.98));
  border-right: 1px solid rgba(55, 53, 47, 0.08);
  backdrop-filter: blur(18px);
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 6px 22px;
}

.sidebar__brand-mark {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 16px;
  background: linear-gradient(145deg, var(--accent-primary), #30584e);
  color: #fff;
  font-weight: 800;
  letter-spacing: 0.04em;
  box-shadow: 0 18px 24px rgba(74, 124, 111, 0.18);
}

.sidebar__brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar__brand-copy strong {
  font-size: 18px;
  color: var(--text-primary);
}

.sidebar__brand-eyebrow {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 52px;
  padding: 0 14px;
  border-radius: 18px;
  color: var(--text-tertiary);
  transition: transform 0.18s ease, background 0.18s ease, color 0.18s ease;
}

.sidebar__link:hover {
  background: rgba(74, 124, 111, 0.08);
  color: var(--text-primary);
  transform: translateX(2px);
}

.sidebar__link.is-active {
  background: linear-gradient(135deg, rgba(74, 124, 111, 0.14), rgba(232, 192, 122, 0.16));
  color: var(--text-primary);
  box-shadow: inset 0 0 0 1px rgba(74, 124, 111, 0.1);
}

.sidebar__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
}

.sidebar__label {
  font-size: 14px;
  font-weight: 600;
}

.sidebar__footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 18px;
  border-top: 1px solid rgba(55, 53, 47, 0.08);
}

.sidebar__user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar__avatar {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  overflow: hidden;
  display: grid;
  place-items: center;
  background: rgba(74, 124, 111, 0.12);
  color: var(--accent-primary);
  font-weight: 700;
}

.sidebar__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sidebar__user-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.sidebar__user-copy strong {
  font-size: 14px;
  color: var(--text-primary);
}

.sidebar__user-copy span {
  font-size: 12px;
  color: var(--text-secondary);
}

.sidebar__logout {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  border: none;
  border-radius: 16px;
  background: rgba(55, 53, 47, 0.05);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.sidebar__logout.is-collapse {
  width: 44px;
  align-self: center;
  border-radius: 14px;
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
</style>
