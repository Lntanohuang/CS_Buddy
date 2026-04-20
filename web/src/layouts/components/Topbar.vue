<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Expand, Fold } from '@element-plus/icons-vue'
import NotificationBadge from '@/components/notice/NotificationBadge.vue'
import { useAuthStore } from '@/stores/auth'
import { useLayoutStore } from '@/stores/layout'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const authStore = useAuthStore()
const layoutStore = useLayoutStore()
const userStore = useUserStore()

const pageMetaMap: Record<string, { title: string; subtitle: string }> = {
  chat: {
    title: 'AI 对话课堂',
    subtitle: '图文、代码、讲解卡片在同一空间协同出现。',
  },
  path: {
    title: '学习路径总览',
    subtitle: '按知识点依赖关系拆出下一步最值得投入的任务。',
  },
  evaluate: {
    title: '测评与反馈',
    subtitle: '把测评结果即时回灌到学习画像和推荐流。',
  },
  profile: {
    title: '多模态学习画像',
    subtitle: '查看能力雷达、掌握热区和通知流的联动情况。',
  },
  notifications: {
    title: '消息中心',
    subtitle: '汇总 AI 导师提醒、测评结果和路径更新通知。',
  },
}

const currentMeta = computed(() => {
  const name = typeof route.name === 'string' ? route.name : ''
  return pageMetaMap[name] ?? {
    title: 'CS Buddy',
    subtitle: '为 AI 多模态学习场景设计的前端工作台。',
  }
})

const displayName = computed(() => authStore.nickname || userStore.userInfo.name)
const weeklyHours = computed(() => Math.round((userStore.userInfo.weeklyMinutes / 60) * 10) / 10)
</script>

<template>
  <header class="topbar">
    <div class="topbar__left">
      <button class="topbar__toggle" type="button" @click="layoutStore.toggleCollapse()">
        <el-icon :size="18">
          <component :is="layoutStore.isCollapse ? Expand : Fold" />
        </el-icon>
      </button>

      <div class="topbar__title-group">
        <p class="topbar__eyebrow">Learning Control Deck</p>
        <h1 class="topbar__title">{{ currentMeta.title }}</h1>
        <p class="topbar__subtitle">{{ currentMeta.subtitle }}</p>
      </div>
    </div>

    <div class="topbar__right">
      <div class="topbar__chip">
        <span class="topbar__chip-label">本周投入</span>
        <strong>{{ weeklyHours }}h</strong>
      </div>

      <div class="topbar__chip topbar__chip--accent">
        <span class="topbar__chip-label">当前模式</span>
        <strong>{{ userStore.displayPreferredStyle }}</strong>
      </div>

      <NotificationBadge />

      <div class="topbar__user">
        <div class="topbar__user-avatar">
          <img :src="userStore.userInfo.avatar" :alt="displayName" />
        </div>
        <div class="topbar__user-copy">
          <strong>{{ displayName }}</strong>
          <span>{{ userStore.displayGoal }}</span>
        </div>
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
  gap: 18px;
  padding: 22px 28px 20px;
  background: linear-gradient(180deg, rgba(250, 250, 248, 0.96), rgba(250, 250, 248, 0.82));
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(55, 53, 47, 0.06);
}

.topbar__left,
.topbar__right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.topbar__left {
  min-width: 0;
}

.topbar__toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--text-primary);
  box-shadow: 0 12px 24px rgba(55, 53, 47, 0.08);
  cursor: pointer;
}

.topbar__title-group {
  min-width: 0;
}

.topbar__eyebrow {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.topbar__title {
  margin: 0;
  font-size: 28px;
  line-height: 1.15;
  color: var(--text-primary);
}

.topbar__subtitle {
  margin: 6px 0 0;
  font-size: 14px;
  color: var(--text-tertiary);
}

.topbar__chip {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 14px;
  min-width: 96px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 12px 24px rgba(55, 53, 47, 0.05);
}

.topbar__chip--accent {
  background: linear-gradient(180deg, rgba(237, 245, 242, 1), rgba(255, 255, 255, 0.92));
}

.topbar__chip-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.topbar__chip strong {
  font-size: 14px;
  color: var(--text-primary);
}

.topbar__user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 6px 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 12px 24px rgba(55, 53, 47, 0.05);
}

.topbar__user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  overflow: hidden;
}

.topbar__user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.topbar__user-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.topbar__user-copy strong {
  font-size: 14px;
  color: var(--text-primary);
}

.topbar__user-copy span {
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 1100px) {
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .topbar__right {
    width: 100%;
    flex-wrap: wrap;
  }
}

@media (max-width: 720px) {
  .topbar {
    padding: 18px 18px 16px;
  }

  .topbar__title {
    font-size: 22px;
  }

  .topbar__right {
    gap: 10px;
  }

  .topbar__chip {
    min-width: unset;
  }

  .topbar__user {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
