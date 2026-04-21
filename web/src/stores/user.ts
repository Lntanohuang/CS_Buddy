import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import heroAvatar from '@/assets/hero.png'
import type { DashboardUserInfo, LearningRadarMetric, UserProfile } from '@/types'

type DialoguePayload = {
  major: string
  learning_goal: string
  current_level: string
  preferred_style: string
  cognitive_style: UserProfile['cognitive_style']
  daily_time_minutes: number
  subjects: string[]
}

const LEVEL_LABELS: Record<string, string> = {
  BEGINNER: '入门',
  ELEMENTARY: '初级',
  INTERMEDIATE: '中级',
  ADVANCED: '高级',
}

const GOAL_LABELS: Record<string, string> = {
  EXAM_PREP: '考试与面试冲刺',
  INTEREST: '兴趣探索',
  SKILL_UP: '技能提升',
}

const STYLE_LABELS: Record<string, string> = {
  VIDEO: '视频讲解',
  TEXT: '图文精读',
  PRACTICE: '代码实战',
  MIXED: '多模态混合',
}

const COGNITIVE_STYLE_LABELS: Record<UserProfile['cognitive_style'], string> = {
  THEORETICAL: '理论推导型',
  PRACTICAL: '实践操作型',
  VISUAL: '可视化理解型',
  MIXED: '混合协同型',
}

const SUBJECT_LABELS: Record<string, string> = {
  DATA_STRUCTURE: '数据结构',
  ALGORITHM: '算法设计',
  SYSTEM_DESIGN: '系统设计',
  COMPUTER_NETWORK: '计算机网络',
}

const RADAR_METRICS: LearningRadarMetric[] = [
  { key: 'foundation', label: '基础掌握', max: 100, description: '核心知识点的稳定掌握程度。' },
  { key: 'coding', label: '编码实战', max: 100, description: '把知识转为代码实现的速度和准确度。' },
  { key: 'analysis', label: '分析推理', max: 100, description: '拆解问题、归纳规律和解释思路的能力。' },
  { key: 'multimodal', label: '多模态吸收', max: 100, description: '图文、代码、视频等多通道协同学习效率。' },
  { key: 'momentum', label: '学习韧性', max: 100, description: '持续投入、复盘和完成学习目标的稳定性。' },
]

const DEFAULT_KNOWLEDGE_MASTERY: Record<string, number> = {
  array: 0.86,
  linked_list: 0.79,
  stack: 0.75,
  queue: 0.7,
  sorting: 0.74,
  hash_table: 0.69,
  binary_tree: 0.48,
  graph: 0.42,
}

const DEFAULT_STYLE_WEIGHTS: Record<string, number> = {
  code_example: 0.52,
  analogy: 0.22,
  text: 0.26,
}

const DEFAULT_ERROR_PATTERNS = [
  '递归边界条件偶尔遗漏，导致树题稳定性不足。',
  '图遍历时容易混淆 visited 标记与入队时机。',
  '复杂度分析表达不够完整，口述时容易漏掉空间复杂度。',
]

const DEFAULT_SUBJECTS = ['DATA_STRUCTURE', 'ALGORITHM', 'SYSTEM_DESIGN']

function clamp(value: number, min = 0, max = 100) {
  return Math.min(max, Math.max(min, value))
}

function average(values: number[]) {
  if (values.length === 0) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}

export const useUserStore = defineStore('user', () => {
  const hasLoaded = ref(false)
  const userId = ref('usr_dashboard_001')
  const major = ref('计算机科学与技术')
  const currentLevel = ref('INTERMEDIATE')
  const learningGoal = ref('EXAM_PREP')
  const preferredStyle = ref('MIXED')
  const cognitiveStyle = ref<UserProfile['cognitive_style']>('VISUAL')
  const dailyTimeMinutes = ref(75)
  const subjects = ref<string[]>([...DEFAULT_SUBJECTS])
  const knowledgeMastery = ref<Record<string, number>>({ ...DEFAULT_KNOWLEDGE_MASTERY })
  const styleWeights = ref<Record<string, number>>({ ...DEFAULT_STYLE_WEIGHTS })
  const errorPatterns = ref<string[]>([...DEFAULT_ERROR_PATTERNS])
  const weakPoints = ref<string[]>([])
  const profileComplete = ref(true)
  const updatedAt = ref(new Date().toISOString())
  const userInfo = ref<DashboardUserInfo>({
    id: userId.value,
    name: '林知夏',
    avatar: heroAvatar,
    role: 'AI 多模态学习营学员',
    goal: '考试与面试冲刺',
    major: major.value,
    bio: '偏好图示 + 代码示例联动学习，适合在结构化节奏里快速建立知识地图。',
    streakDays: 12,
    weeklyMinutes: dailyTimeMinutes.value * 7,
    masteryRate: 0,
  })
  const radarMetrics = ref<LearningRadarMetric[]>([...RADAR_METRICS])
  const radarScoreMap = ref<Record<string, number>>({})

  const currentScores = computed(() =>
    radarMetrics.value.map((metric) => radarScoreMap.value[metric.key] ?? 0),
  )

  const displayLevel = computed(() => LEVEL_LABELS[currentLevel.value] ?? currentLevel.value)
  const displayGoal = computed(() => GOAL_LABELS[learningGoal.value] ?? learningGoal.value)
  const displayPreferredStyle = computed(() => STYLE_LABELS[preferredStyle.value] ?? preferredStyle.value)
  const displayCognitiveStyle = computed(
    () => COGNITIVE_STYLE_LABELS[cognitiveStyle.value] ?? cognitiveStyle.value,
  )
  const displaySubjects = computed(() =>
    subjects.value.map((subject) => SUBJECT_LABELS[subject] ?? subject),
  )

  function syncWeakPoints() {
    weakPoints.value = Object.entries(knowledgeMastery.value)
      .filter(([, score]) => score < 0.6)
      .map(([key]) => key)
  }

  function syncRadarScores() {
    const mastery = knowledgeMastery.value
    const foundation = average([
      mastery.array,
      mastery.linked_list,
      mastery.stack,
      mastery.queue,
      mastery.hash_table,
    ]) * 100
    const coding = (average([mastery.sorting, mastery.stack, mastery.hash_table]) * 100)
      + styleWeights.value.code_example * 15
    const analysis = average([mastery.binary_tree, mastery.graph, mastery.sorting]) * 100
    const multimodal = (
      average(Object.values(styleWeights.value)) * 100
      + (cognitiveStyle.value === 'VISUAL' ? 14 : cognitiveStyle.value === 'MIXED' ? 9 : 4)
    )
    const momentum = 52 + dailyTimeMinutes.value / 1.4 + (profileComplete.value ? 10 : 0) - errorPatterns.value.length * 3

    radarScoreMap.value = {
      foundation: Math.round(clamp(foundation)),
      coding: Math.round(clamp(coding)),
      analysis: Math.round(clamp(analysis)),
      multimodal: Math.round(clamp(multimodal)),
      momentum: Math.round(clamp(momentum)),
    }

    const masteryRate = Math.round(average(Object.values(mastery)) * 100)
    userInfo.value = {
      ...userInfo.value,
      id: userId.value,
      major: major.value,
      goal: displayGoal.value,
      weeklyMinutes: dailyTimeMinutes.value * 7,
      masteryRate,
    }
  }

  function applyMockData() {
    userId.value = 'usr_dashboard_001'
    major.value = '计算机科学与技术'
    currentLevel.value = 'INTERMEDIATE'
    learningGoal.value = 'EXAM_PREP'
    preferredStyle.value = 'MIXED'
    cognitiveStyle.value = 'VISUAL'
    dailyTimeMinutes.value = 75
    subjects.value = [...DEFAULT_SUBJECTS]
    knowledgeMastery.value = { ...DEFAULT_KNOWLEDGE_MASTERY }
    styleWeights.value = { ...DEFAULT_STYLE_WEIGHTS }
    errorPatterns.value = [...DEFAULT_ERROR_PATTERNS]
    profileComplete.value = true
    updatedAt.value = new Date().toISOString()
    userInfo.value = {
      id: userId.value,
      name: '林知夏',
      avatar: heroAvatar,
      role: 'AI 多模态学习营学员',
      goal: GOAL_LABELS.EXAM_PREP,
      major: major.value,
      bio: '正在用图示、代码和任务拆解并行学习数据结构与算法，适合高反馈的多模态课堂。',
      streakDays: 12,
      weeklyMinutes: dailyTimeMinutes.value * 7,
      masteryRate: 0,
    }
    syncWeakPoints()
    syncRadarScores()
  }

  function fetchMockUserData() {
    if (hasLoaded.value) return
    applyMockData()
    hasLoaded.value = true
  }

  function updateProfile(updates: Partial<UserProfile>) {
    fetchMockUserData()

    if (updates.major !== undefined) major.value = updates.major
    if (updates.current_level !== undefined) currentLevel.value = updates.current_level
    if (updates.learning_goal !== undefined) learningGoal.value = updates.learning_goal
    if (updates.preferred_style !== undefined) preferredStyle.value = updates.preferred_style
    if (updates.cognitive_style !== undefined) cognitiveStyle.value = updates.cognitive_style
    if (updates.daily_time_minutes !== undefined) dailyTimeMinutes.value = updates.daily_time_minutes
    if (updates.subjects !== undefined) subjects.value = [...updates.subjects]
    if (updates.style_weights !== undefined) styleWeights.value = { ...updates.style_weights }
    if (updates.error_patterns !== undefined) errorPatterns.value = [...updates.error_patterns]
    if (updates.knowledge_mastery !== undefined) {
      knowledgeMastery.value = { ...updates.knowledge_mastery }
    }
    if (updates.profile_complete !== undefined) profileComplete.value = updates.profile_complete

    updatedAt.value = new Date().toISOString()
    syncWeakPoints()
    syncRadarScores()
  }

  function updateMastery(knowledgePoint: string, value: number) {
    fetchMockUserData()
    knowledgeMastery.value = {
      ...knowledgeMastery.value,
      [knowledgePoint]: clamp(value, 0, 1),
    }
    updatedAt.value = new Date().toISOString()
    syncWeakPoints()
    syncRadarScores()
  }

  function initFromDialogue(data: DialoguePayload) {
    fetchMockUserData()
    major.value = data.major
    learningGoal.value = data.learning_goal
    currentLevel.value = data.current_level
    preferredStyle.value = data.preferred_style
    cognitiveStyle.value = data.cognitive_style
    dailyTimeMinutes.value = data.daily_time_minutes
    subjects.value = [...data.subjects]
    profileComplete.value = true
    updatedAt.value = new Date().toISOString()
    syncWeakPoints()
    syncRadarScores()
  }

  return {
    hasLoaded,
    userInfo,
    radarMetrics,
    currentScores,
    major,
    currentLevel,
    learningGoal,
    preferredStyle,
    cognitiveStyle,
    dailyTimeMinutes,
    subjects,
    displayLevel,
    displayGoal,
    displayPreferredStyle,
    displayCognitiveStyle,
    displaySubjects,
    knowledgeMastery,
    styleWeights,
    errorPatterns,
    weakPoints,
    profileComplete,
    updatedAt,
    fetchMockUserData,
    updateProfile,
    updateMastery,
    initFromDialogue,
  }
})
