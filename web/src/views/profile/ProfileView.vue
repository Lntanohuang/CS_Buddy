<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import UserRadarChart from '@/components/charts/UserRadarChart.vue'
import { useNotificationStore } from '@/stores/notification'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const showRefreshDialog = ref(false)

const TOPIC_LABELS: Record<string, string> = {
  array: '数组基础',
  linked_list: '链表操作',
  stack: '栈与队列',
  queue: '队列模型',
  sorting: '排序策略',
  hash_table: '哈希表',
  binary_tree: '二叉树',
  graph: '图搜索',
}

const STYLE_LABELS: Record<string, string> = {
  code_example: '代码示例驱动',
  analogy: '类比讲解',
  text: '结构化图文',
}

onMounted(() => {
  userStore.fetchMockUserData()
})

const heroStats = computed(() => [
  {
    label: '学习连胜',
    value: `${userStore.userInfo.streakDays} 天`,
    hint: '过去两周保持稳定打卡。',
  },
  {
    label: '周投入',
    value: `${Math.round(userStore.userInfo.weeklyMinutes / 60)} 小时`,
    hint: '根据每日目标自动换算。',
  },
  {
    label: '画像完成度',
    value: `${userStore.userInfo.masteryRate}%`,
    hint: '由掌握度、测评和通知反馈共同更新。',
  },
])

const abilityCards = computed(() =>
  userStore.radarMetrics.map((metric, index) => ({
    ...metric,
    score: userStore.currentScores[index] ?? 0,
  })),
)

const masteryEntries = computed(() =>
  Object.entries(userStore.knowledgeMastery)
    .map(([key, value]) => ({
      key,
      label: TOPIC_LABELS[key] ?? key,
      score: Math.round(value * 100),
      isWeak: userStore.weakPoints.includes(key),
    }))
    .sort((left, right) => right.score - left.score),
)

const preferenceEntries = computed(() =>
  Object.entries(userStore.styleWeights)
    .map(([key, value]) => ({
      key,
      label: STYLE_LABELS[key] ?? key,
      score: Math.round(value * 100),
    }))
    .sort((left, right) => right.score - left.score),
)

const recentMessages = computed(() => notificationStore.messageList.slice(0, 4))

function masteryBarColor(score: number) {
  if (score >= 80) return 'linear-gradient(90deg, #4A7C6F, #70A28F)'
  if (score >= 60) return 'linear-gradient(90deg, #E8C07A, #E9D48F)'
  return 'linear-gradient(90deg, #C4554D, #E17B71)'
}

function formatNotificationTime(value: string) {
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleSimulateNotification() {
  notificationStore.receiveNewMessage({
    type: 'STUDY_REMINDER',
    title: 'AI 导师发来新的提醒',
    content: '建议把今晚的 20 分钟留给“树与图的关系图谱”，通知角标和铃铛动画会同步更新。',
    actionUrl: '/app/profile',
  })
}

function handleOpenRefreshDialog() {
  showRefreshDialog.value = true
}

function handleCloseRefreshDialog() {
  showRefreshDialog.value = false
}

function handleStartProfileRefresh() {
  showRefreshDialog.value = false
  router.push({
    path: '/welcome',
    query: {
      mode: 'refresh-profile',
      redirect: '/app/profile',
    },
  })
}
</script>

<template>
  <div class="profile-dashboard">
    <section class="hero-card">
      <div class="hero-card__main">
        <div class="hero-card__avatar">
          <img :src="userStore.userInfo.avatar" :alt="userStore.userInfo.name" />
        </div>

        <div class="hero-card__copy">
          <p class="hero-card__eyebrow">Multimodal Learning Portrait</p>
          <h1>{{ userStore.userInfo.name }}</h1>
          <p class="hero-card__bio">{{ userStore.userInfo.bio }}</p>

          <div class="hero-card__tags">
            <span class="hero-card__tag">{{ userStore.displayLevel }}</span>
            <span class="hero-card__tag">{{ userStore.displayGoal }}</span>
            <span class="hero-card__tag">{{ userStore.displayPreferredStyle }}</span>
            <span class="hero-card__tag">{{ userStore.displayCognitiveStyle }}</span>
          </div>

          <div class="hero-card__subjects">
            <span
              v-for="subject in userStore.displaySubjects"
              :key="subject"
              class="hero-card__subject"
            >
              {{ subject }}
            </span>
          </div>
        </div>
      </div>

      <div class="hero-card__stats">
        <article v-for="item in heroStats" :key="item.label" class="hero-stat">
          <span class="hero-stat__label">{{ item.label }}</span>
          <strong class="hero-stat__value">{{ item.value }}</strong>
          <span class="hero-stat__hint">{{ item.hint }}</span>
        </article>
      </div>
    </section>

    <section class="overview-grid">
      <article class="panel panel--radar">
        <div class="panel__header">
          <div>
            <p class="panel__eyebrow">能力雷达</p>
            <h2>学习能力五维评分</h2>
          </div>
          <span class="panel__meta">侧栏折叠时会自动 resize</span>
        </div>

        <div class="panel__chart">
          <UserRadarChart :metrics="userStore.radarMetrics" :values="userStore.currentScores" />
        </div>
      </article>

      <article class="panel panel--brief">
        <div class="panel__header">
          <div>
            <p class="panel__eyebrow">本周策略</p>
            <h2>从通知流回灌到学习路径</h2>
          </div>
          <button class="panel__action" type="button" @click="handleSimulateNotification">
            模拟新增通知
          </button>
        </div>

        <div class="strategy-card">
          <span class="strategy-card__step">01</span>
          <div>
            <strong>先看能力短板</strong>
            <p>把树、图和复杂度表达作为本周优先补强对象。</p>
          </div>
        </div>

        <div class="strategy-card">
          <span class="strategy-card__step">02</span>
          <div>
            <strong>再接多模态材料</strong>
            <p>图示理解 + 代码演练混合推进，减少纯文字吸收的疲劳感。</p>
          </div>
        </div>

        <div class="strategy-card">
          <span class="strategy-card__step">03</span>
          <div>
            <strong>最后由通知强提醒</strong>
            <p>顶部铃铛会在未读数增加时震动，提醒你及时切回当前任务。</p>
          </div>
        </div>
      </article>
    </section>

    <section class="ability-grid">
      <article v-for="card in abilityCards" :key="card.key" class="ability-card">
        <div class="ability-card__top">
          <p>{{ card.label }}</p>
          <strong>{{ card.score }}</strong>
        </div>
        <div class="ability-card__track">
          <span class="ability-card__fill" :style="{ width: `${card.score}%` }" />
        </div>
        <p class="ability-card__desc">{{ card.description }}</p>
      </article>
    </section>

    <section class="detail-grid">
      <article class="panel">
        <div class="panel__header">
          <div>
            <p class="panel__eyebrow">知识热区</p>
            <h2>掌握度分布</h2>
          </div>
        </div>

        <div class="mastery-list">
          <div v-for="item in masteryEntries" :key="item.key" class="mastery-item">
            <div class="mastery-item__top">
              <span class="mastery-item__label">{{ item.label }}</span>
              <div class="mastery-item__meta">
                <span v-if="item.isWeak" class="mastery-item__weak">待强化</span>
                <strong>{{ item.score }}%</strong>
              </div>
            </div>
            <div class="mastery-item__track">
              <span
                class="mastery-item__fill"
                :style="{
                  width: `${item.score}%`,
                  background: masteryBarColor(item.score),
                }"
              />
            </div>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel__header">
          <div>
            <p class="panel__eyebrow">多模态偏好</p>
            <h2>内容消费结构</h2>
          </div>
        </div>

        <div class="preference-list">
          <div v-for="item in preferenceEntries" :key="item.key" class="preference-item">
            <div class="preference-item__top">
              <span>{{ item.label }}</span>
              <strong>{{ item.score }}%</strong>
            </div>
            <div class="preference-item__track">
              <span class="preference-item__fill" :style="{ width: `${item.score}%` }" />
            </div>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel__header">
          <div>
            <p class="panel__eyebrow">AI 提醒流</p>
            <h2>最近四条通知</h2>
          </div>
        </div>

        <div class="message-list">
          <div
            v-for="message in recentMessages"
            :key="message.id"
            class="message-card"
            :class="{ 'message-card--unread': !message.read }"
          >
            <div class="message-card__top">
              <strong>{{ message.title }}</strong>
              <span>{{ formatNotificationTime(message.createdAt) }}</span>
            </div>
            <p>{{ message.content }}</p>
          </div>
        </div>
      </article>
    </section>

    <button
      class="refresh-fab"
      type="button"
      aria-label="更新画像"
      @click="handleOpenRefreshDialog"
    >
      更新画像
    </button>

    <div
      v-if="showRefreshDialog"
      class="refresh-dialog-backdrop"
      @click.self="handleCloseRefreshDialog"
    >
      <div class="refresh-dialog" role="dialog" aria-modal="true" aria-labelledby="refresh-dialog-title">
        <p class="refresh-dialog__eyebrow">欢迎问答</p>
        <h3 id="refresh-dialog-title">重新生成学习画像</h3>
        <p class="refresh-dialog__desc">
          将再次进入欢迎界面的问答流程。问答结束后系统会自动更新画像，并返回个人中心。
        </p>
        <div class="refresh-dialog__actions">
          <button type="button" class="refresh-dialog__cancel" @click="handleCloseRefreshDialog">
            取消
          </button>
          <button type="button" class="refresh-dialog__confirm" @click="handleStartProfileRefresh">
            开始更新
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-dashboard {
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding-top: 4px;
}

.hero-card,
.panel,
.ability-card {
  border: 1px solid rgba(55, 53, 47, 0.08);
  box-shadow: 0 18px 32px rgba(55, 53, 47, 0.05);
}

.hero-card {
  position: relative;
  overflow: hidden;
  padding: 28px;
  border-radius: 28px;
  background:
    radial-gradient(circle at top left, rgba(232, 192, 122, 0.36), transparent 30%),
    radial-gradient(circle at bottom right, rgba(74, 124, 111, 0.2), transparent 28%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(247, 246, 243, 0.96));
}

.hero-card__main {
  display: flex;
  gap: 20px;
  align-items: center;
}

.hero-card__avatar {
  width: 112px;
  height: 112px;
  border-radius: 28px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 24px 36px rgba(55, 53, 47, 0.14);
}

.hero-card__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-card__copy h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.1;
  color: var(--text-primary);
}

.hero-card__eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}

.hero-card__bio {
  margin: 12px 0 0;
  max-width: 760px;
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-tertiary);
}

.hero-card__tags,
.hero-card__subjects {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.hero-card__tag,
.hero-card__subject {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

.hero-card__tag {
  background: rgba(255, 255, 255, 0.9);
  color: var(--text-primary);
}

.hero-card__subject {
  background: rgba(74, 124, 111, 0.12);
  color: var(--accent-primary);
}

.hero-card__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.hero-stat {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.82);
}

.hero-stat__label {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}

.hero-stat__value {
  font-size: 24px;
  color: var(--text-primary);
}

.hero-stat__hint {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-tertiary);
}

.overview-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.95fr);
  gap: 22px;
}

.panel {
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
}

.panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel__header h2 {
  margin: 0;
  font-size: 22px;
  color: var(--text-primary);
}

.panel__eyebrow {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.panel__meta {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.panel__action {
  border: none;
  border-radius: 999px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  padding: 10px 16px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.panel__chart {
  height: 360px;
}

.strategy-card {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr);
  gap: 14px;
  align-items: flex-start;
  padding: 14px 0;
  border-bottom: 1px solid rgba(55, 53, 47, 0.08);
}

.strategy-card:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.strategy-card__step {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 18px;
  background: linear-gradient(145deg, rgba(74, 124, 111, 0.14), rgba(232, 192, 122, 0.22));
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 800;
}

.strategy-card strong {
  color: var(--text-primary);
}

.strategy-card p {
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-tertiary);
}

.ability-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.ability-card {
  padding: 18px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 246, 243, 0.96));
}

.ability-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.ability-card__top p {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.ability-card__top strong {
  font-size: 28px;
  line-height: 1;
  color: var(--accent-primary);
}

.ability-card__track {
  height: 8px;
  margin: 16px 0 14px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(55, 53, 47, 0.08);
}

.ability-card__fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
}

.ability-card__desc {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-tertiary);
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.95fr) minmax(0, 1fr);
  gap: 22px;
}

.mastery-list,
.preference-list,
.message-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mastery-item__top,
.preference-item__top,
.message-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.mastery-item__label,
.preference-item__top span {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.mastery-item__meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mastery-item__meta strong,
.preference-item__top strong {
  font-size: 14px;
  color: var(--text-primary);
}

.mastery-item__weak {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(196, 85, 77, 0.12);
  color: var(--status-error);
  font-size: 12px;
  font-weight: 700;
}

.mastery-item__track,
.preference-item__track {
  height: 10px;
  margin-top: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(55, 53, 47, 0.08);
}

.mastery-item__fill,
.preference-item__fill {
  display: block;
  height: 100%;
  border-radius: inherit;
}

.preference-item__fill {
  background: linear-gradient(90deg, rgba(74, 124, 111, 0.9), rgba(232, 192, 122, 0.9));
}

.message-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(247, 246, 243, 0.86);
}

.message-card--unread {
  background: rgba(237, 245, 242, 0.96);
}

.message-card__top strong {
  font-size: 14px;
  color: var(--text-primary);
}

.message-card__top span {
  font-size: 11px;
  color: var(--text-secondary);
}

.message-card p {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-tertiary);
}

.refresh-fab {
  position: fixed;
  right: 34px;
  bottom: 34px;
  z-index: 40;
  border: none;
  border-radius: 999px;
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #4a7c6f, #3b6b5f);
  box-shadow: 0 16px 34px rgba(55, 53, 47, 0.2);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.refresh-fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 38px rgba(55, 53, 47, 0.24);
}

.refresh-dialog-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(30, 30, 30, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.refresh-dialog {
  width: min(460px, 100%);
  border-radius: 22px;
  padding: 24px;
  background: #ffffff;
  border: 1px solid rgba(55, 53, 47, 0.12);
  box-shadow: 0 24px 50px rgba(30, 30, 30, 0.2);
}

.refresh-dialog__eyebrow {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.refresh-dialog h3 {
  margin: 10px 0 8px;
  font-size: 24px;
  color: var(--text-primary);
}

.refresh-dialog__desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-tertiary);
}

.refresh-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.refresh-dialog__cancel,
.refresh-dialog__confirm {
  border: none;
  border-radius: 10px;
  min-height: 38px;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.refresh-dialog__cancel {
  background: rgba(55, 53, 47, 0.08);
  color: var(--text-primary);
}

.refresh-dialog__confirm {
  background: var(--accent-primary);
  color: #ffffff;
}

@media (max-width: 1360px) {
  .ability-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1080px) {
  .overview-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .hero-card__stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .profile-dashboard {
    gap: 18px;
  }

  .hero-card,
  .panel,
  .ability-card {
    padding: 18px;
    border-radius: 22px;
  }

  .hero-card__main {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-card__copy h1 {
    font-size: 28px;
  }

  .ability-grid {
    grid-template-columns: 1fr;
  }

  .refresh-fab {
    right: 20px;
    bottom: 20px;
  }
}
</style>
