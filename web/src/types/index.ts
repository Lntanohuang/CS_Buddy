// ---- Auth ----
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  nickname: string
  email: string
  password: string
}

export interface AuthUser {
  user_id: string
  nickname: string
  role: 'STUDENT' | 'TEACHER'
  access_token: string
  refresh_token: string
  expires_in: number
  has_profile: boolean
}

export interface DashboardUserInfo {
  id: string
  name: string
  avatar: string
  role: string
  goal: string
  major: string
  bio: string
  streakDays: number
  weeklyMinutes: number
  masteryRate: number
}

export interface LearningRadarMetric {
  key: string
  label: string
  max: number
  description: string
}

// ---- Profile (7 dimensions) ----
export interface UserProfile {
  user_id: string
  major: string                              // 专业背景
  knowledge_mastery: Record<string, number>  // 知识基础
  cognitive_style: 'THEORETICAL' | 'PRACTICAL' | 'VISUAL' | 'MIXED' // 认知风格
  error_patterns: string[]                   // 易错点偏好
  preferred_style: string                    // 学习风格
  daily_time_minutes: number                 // 学习节奏
  learning_goal: string                      // 学习目标
  current_level: string
  weak_points: string[]
  style_weights: Record<string, number>
  subjects: string[]
  profile_complete: boolean
  updated_at: string
}

// ---- Chat ----
export interface ChatSession {
  session_id: string
  title: string
  status: string
  session_type: 'NORMAL' | 'WELCOME'
  message_count: number
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  message_id: string
  session_id: string
  role: 'USER' | 'ASSISTANT'
  content: string
  intent?: string
  resource_type?: 'doc' | 'mindmap' | 'quiz' | 'video' | 'code' | 'mermaid'
  metadata?: Record<string, unknown>
  created_at: string
}

// ---- Learning Path ----
export interface LearningPath {
  path_id: string
  subject: string
  goal: string
  total_nodes: number
  completed_nodes: number
  status: 'ACTIVE' | 'COMPLETED' | 'PAUSED'
  est_total_hours: number
  nodes: PathNode[]
  created_at: string
}

export interface PathNode {
  node_id: string
  title: string
  knowledge_point: string
  order: number
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED'
  difficulty: string
  est_minutes: number
  prerequisites: string[]
  is_supplement: boolean
  completed_at?: string
}

// ---- Evaluation ----
export interface Evaluation {
  eval_id: string
  type: 'MINI_QUIZ' | 'STAGE_TEST' | 'USER_REQUEST'
  knowledge_point: string
  score?: number
  mastery_level?: number
  learning_efficiency?: number
  progress_trend?: 'UP' | 'STABLE' | 'DOWN'
  weak_point_analysis?: string[]
  question_count: number
  correct_count?: number
  time_spent_seconds?: number
  status: 'PENDING' | 'SUBMITTED' | 'ANALYZED'
  questions: EvalQuestion[]
  recommendation?: EvalRecommendation
  created_at: string
}

export interface EvalQuestion {
  question_id: string
  type: 'SINGLE_CHOICE' | 'FILL_BLANK' | 'CODE'
  content: string
  options?: { key: string; value: string }[]
  correct_answer: string
  explanation?: string
  user_answer?: string
  is_correct?: boolean
}

export interface EvalRecommendation {
  action: 'ADVANCE' | 'SUPPLEMENT' | 'RETREAT'
  message: string
  next_node_id?: string
}

// ---- Notification ----
export type NotificationType =
  | 'DAILY_RECOMMEND'
  | 'STUDY_REMINDER'
  | 'INACTIVE_RECALL'
  | 'EVAL_RESULT'
  | 'ACHIEVEMENT'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  content: string
  is_read: boolean
  created_at: string
  action_url?: string
  read?: boolean
  time?: string
  actionUrl?: string
  createdAt?: string
}

export interface NotificationMessage {
  id: string
  type: NotificationType
  title: string
  content: string
  time: string
  read: boolean
  createdAt: string
  is_read: boolean
  created_at: string
  actionUrl?: string
  action_url?: string
}

// ---- Agent Status ----
export interface AgentStep {
  agent: string
  icon: string
  label: string
  status: 'pending' | 'working' | 'done'
}

// ---- Resource Feedback ----
export interface ResourceFeedback {
  resource_id: string
  message_id: string
  feedback: 'USEFUL' | 'NOT_USEFUL'
  comment?: string
}

// ---- API Response ----
export interface ApiResult<T = unknown> {
  code: number
  message: string
  data: T
  timestamp: number
}
