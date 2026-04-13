// ---- Auth ----
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  nickname: string
  email: string
  password: string
  survey: SurveyData | null
}

export interface SurveyData {
  learning_goal: 'EXAM_PREP' | 'INTEREST' | 'SKILL_UP'
  current_level: 'BEGINNER' | 'ELEMENTARY' | 'INTERMEDIATE' | 'ADVANCED'
  daily_time_minutes: number
  preferred_style: 'VIDEO' | 'TEXT' | 'PRACTICE' | 'MIXED'
  subjects: string[]
}

export interface AuthUser {
  user_id: string
  nickname: string
  role: 'STUDENT' | 'TEACHER'
  access_token: string
  refresh_token: string
  expires_in: number
}

// ---- Profile ----
export interface UserProfile {
  user_id: string
  current_level: string
  learning_goal: string
  preferred_style: string
  daily_time_minutes: number
  knowledge_mastery: Record<string, number>
  weak_points: string[]
  style_weights: Record<string, number>
  subjects: string[]
  updated_at: string
}

// ---- Chat ----
export interface ChatSession {
  session_id: string
  title: string
  status: string
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
  metadata?: Record<string, unknown>
  created_at: string
}

export interface SSEChunk {
  type: 'token' | 'metadata' | 'resource_card' | 'done' | 'heartbeat'
  content?: string
  agent?: string
  knowledge_point?: string
  title?: string
  difficulty?: string
  est_minutes?: number
  message_id?: string
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
