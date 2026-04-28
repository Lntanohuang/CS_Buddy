import type {
  AuthUser,
  UserProfile,
  ChatSession,
  ChatMessage,
  LearningPath,
  Evaluation,
  Notification,
  AgentStep,
} from '@/types'

// ---- Auth ----
export const mockUser: AuthUser = {
  user_id: 'usr_a1b2c3d4',
  nickname: '林知夏',
  role: 'STUDENT',
  access_token: 'mock_access_token_xxx',
  refresh_token: 'mock_refresh_token_xxx',
  expires_in: 7200,
  has_profile: true,
}

export const mockNewUser: AuthUser = {
  ...mockUser,
  has_profile: false,
}

// ---- Profile (7 dimensions) ----
export const mockProfile: UserProfile = {
  user_id: 'usr_a1b2c3d4',
  major: '计算机科学与技术',
  current_level: 'INTERMEDIATE',
  learning_goal: 'EXAM_PREP',
  preferred_style: 'PRACTICE',
  cognitive_style: 'PRACTICAL',
  error_patterns: ['混淆栈和队列的出入顺序', '递归终止条件遗漏', '时间复杂度分析错误'],
  daily_time_minutes: 60,
  knowledge_mastery: {
    array: 0.85,
    linked_list: 0.72,
    stack: 0.68,
    queue: 0.65,
    binary_tree: 0.3,
    sorting: 0.55,
    graph: 0.1,
    hash_table: 0.6,
  },
  weak_points: ['binary_tree', 'graph'],
  style_weights: { code_example: 0.6, analogy: 0.25, text: 0.15 },
  subjects: ['DATA_STRUCTURE', 'ALGORITHM'],
  profile_complete: true,
  updated_at: '2026-04-13T14:30:00Z',
}

// ---- Welcome dialogue script ----
export const welcomeDialogueScript: { role: 'USER' | 'ASSISTANT'; content: string; delay: number }[] = [
  { role: 'ASSISTANT', content: '你好！欢迎来到CS Buddy 🌿\n\n我是你的 AI 学习搭档，接下来我会通过几个简单的问题来了解你，以便为你提供最适合的学习体验。\n\n**你目前是什么专业/领域？**', delay: 800 },
  { role: 'USER', content: '我是计算机科学与技术专业的大二学生', delay: 0 },
  { role: 'ASSISTANT', content: '计算机专业，很棒！💻\n\n**你目前最想学习或提升的方向是什么？**\n比如：备考期末、准备面试、学习新技术...', delay: 600 },
  { role: 'USER', content: '主要是备战秋招面试，想系统复习数据结构和算法', delay: 0 },
  { role: 'ASSISTANT', content: '明白了，秋招备战是很多同学的刚需。\n\n**你觉得自己目前的数据结构基础怎么样？**\n可以简单说说你已经学过哪些内容、哪些部分比较薄弱。', delay: 600 },
  { role: 'USER', content: '数组、链表、栈这些基础的还行，但是树和图相关的比较薄弱，递归的题经常写不对', delay: 0 },
  { role: 'ASSISTANT', content: '了解了！树、图和递归确实是面试高频考点，我们会重点关注这些。\n\n**你更喜欢哪种学习方式？**\n- 看代码示例边学边练\n- 先看理论再做题\n- 看视频讲解\n- 都可以，混合着来', delay: 600 },
  { role: 'USER', content: '我比较喜欢看代码示例，纯理论看不下去', delay: 0 },
  { role: 'ASSISTANT', content: '好的，我记住了 ✨\n\n**最后一个问题——你每天大概能投入多少时间学习？**', delay: 600 },
  { role: 'USER', content: '大概一个小时吧', delay: 0 },
  { role: 'ASSISTANT', content: '完美！我已经了解你的情况了：\n\n- 📚 **专业**：计算机科学\n- 🎯 **目标**：秋招面试备战\n- 📊 **基础**：基础数据结构掌握良好，树/图/递归待加强\n- 💡 **偏好**：代码示例驱动学习\n- ⏰ **时间**：每天约 1 小时\n\n我已经为你创建了个性化学习画像，接下来会据此为你规划学习路径和推荐资源。\n\n**准备好开始学习了吗？** 🚀', delay: 800 },
]

// ---- Chat Sessions ----
export const mockSessions: ChatSession[] = [
  {
    session_id: 'sess_001',
    title: '数据结构学习',
    status: 'ACTIVE',
    session_type: 'NORMAL',
    message_count: 6,
    created_at: '2026-04-13T10:00:00Z',
    updated_at: '2026-04-13T14:30:00Z',
  },
  {
    session_id: 'sess_002',
    title: '排序算法复习',
    status: 'ACTIVE',
    session_type: 'NORMAL',
    message_count: 4,
    created_at: '2026-04-12T09:00:00Z',
    updated_at: '2026-04-12T11:00:00Z',
  },
]

export const mockMessages: ChatMessage[] = [
  {
    message_id: 'msg_001',
    session_id: 'sess_001',
    role: 'USER',
    content: '帮我讲讲快速排序的原理',
    created_at: '2026-04-13T14:00:00Z',
  },
  {
    message_id: 'msg_002',
    session_id: 'sess_001',
    role: 'ASSISTANT',
    content: `## 快速排序（Quick Sort）

快速排序是一种基于**分治思想**的高效排序算法，平均时间复杂度为 **O(n log n)**。

### 核心思想

1. **选取基准**（Pivot）：从数组中选一个元素作为基准
2. **分区**（Partition）：将数组分为两部分——小于基准的放左边，大于基准的放右边
3. **递归**：对左右两部分分别递归执行快速排序

### 代码示例

\`\`\`python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
\`\`\`

### 复杂度分析

| 情况 | 时间复杂度 |
|------|-----------|
| 最优 | O(n log n) |
| 平均 | O(n log n) |
| 最差 | O(n²) |

> 💡 **记忆技巧**：快排就像整理书架——先随便选一本书作为标准，比它矮的放左边，比它高的放右边，然后对左右两堆重复操作。`,
    intent: 'learn',
    resource_type: 'doc',
    metadata: {
      type: 'resource_card',
      resource_type: 'doc',
      title: '快速排序讲解',
      difficulty: 'INTERMEDIATE',
      est_minutes: 15,
      knowledge_point: 'quick_sort',
      agent: 'DocAgent',
    },
    created_at: '2026-04-13T14:00:05Z',
  },
  {
    message_id: 'msg_003',
    session_id: 'sess_001',
    role: 'USER',
    content: '给我生成一个排序算法的思维导图',
    created_at: '2026-04-13T14:10:00Z',
  },
  {
    message_id: 'msg_004',
    session_id: 'sess_001',
    role: 'ASSISTANT',
    content: '已为你生成排序算法的知识思维导图：',
    intent: 'learn',
    resource_type: 'mindmap',
    metadata: {
      type: 'resource_card',
      resource_type: 'mindmap',
      title: '排序算法知识图谱',
      agent: 'MindmapAgent',
      mindmap_data: {
        name: '排序算法',
        children: [
          { name: '比较排序', children: [
            { name: '冒泡排序', children: [{ name: 'O(n²)' }, { name: '稳定' }] },
            { name: '快速排序', children: [{ name: 'O(n log n)' }, { name: '不稳定' }] },
            { name: '归并排序', children: [{ name: 'O(n log n)' }, { name: '稳定' }] },
            { name: '堆排序', children: [{ name: 'O(n log n)' }, { name: '不稳定' }] },
          ]},
          { name: '非比较排序', children: [
            { name: '计数排序', children: [{ name: 'O(n+k)' }] },
            { name: '桶排序', children: [{ name: 'O(n+k)' }] },
            { name: '基数排序', children: [{ name: 'O(nk)' }] },
          ]},
        ],
      },
    },
    created_at: '2026-04-13T14:10:08Z',
  },
  {
    message_id: 'msg_005',
    session_id: 'sess_001',
    role: 'USER',
    content: '给我一个快排的代码实操案例',
    created_at: '2026-04-13T14:15:00Z',
  },
  {
    message_id: 'msg_006',
    session_id: 'sess_001',
    role: 'ASSISTANT',
    content: `下面是一个完整的快速排序实操案例，包含原地排序和测试用例：`,
    intent: 'learn',
    resource_type: 'code',
    metadata: {
      type: 'resource_card',
      resource_type: 'code',
      title: '快速排序 — 原地分区实现',
      agent: 'CodeAgent',
      language: 'python',
      code: `def quick_sort(arr, low=0, high=None):
    """原地快速排序"""
    if high is None:
        high = len(arr) - 1
    if low < high:
        pivot_idx = partition(arr, low, high)
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)
    return arr

def partition(arr, low, high):
    """Lomuto 分区方案"""
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# 测试
data = [38, 27, 43, 3, 9, 82, 10]
print(f"排序前: {data}")
print(f"排序后: {quick_sort(data)}")
# 输出: 排序后: [3, 9, 10, 27, 38, 43, 82]`,
      expected_output: '排序后: [3, 9, 10, 27, 38, 43, 82]',
    },
    created_at: '2026-04-13T14:15:08Z',
  },
]

// ---- Simulated streaming reply ----
export const mockStreamReply = `## 二叉树（Binary Tree）

二叉树是一种每个节点**最多有两个子节点**的树形数据结构。

### 基本概念

- **根节点**（Root）：树的顶部节点
- **叶节点**（Leaf）：没有子节点的节点
- **深度**（Depth）：从根到该节点的边数

### 常见类型

| 类型 | 特点 |
|------|------|
| 完全二叉树 | 除最后一层外，每层都是满的 |
| 满二叉树 | 每个节点要么有 0 个要么有 2 个子节点 |
| 平衡二叉树 | 任意节点的左右子树高度差 ≤ 1 |
| 二叉搜索树 | 左子树 < 根 < 右子树 |

### 代码实现

\`\`\`python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def preorder(root):
    if not root:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)
\`\`\`

\`\`\`mermaid
graph TD
    A[1] --> B[2]
    A --> C[3]
    B --> D[4]
    B --> E[5]
    C --> F[6]
    C --> G[7]
\`\`\`

> 💡 二叉树的遍历是面试高频考点，建议掌握前序、中序、后序和层序四种遍历方式。`

// ---- Learning Path ----
export const mockPath: LearningPath = {
  path_id: 'path_p1q2r3',
  subject: 'DATA_STRUCTURE',
  goal: '掌握数据结构基础，能解决中等难度的 LeetCode 题目',
  total_nodes: 10,
  completed_nodes: 4,
  status: 'ACTIVE',
  est_total_hours: 40,
  nodes: [
    { node_id: 'node_001', title: '数组基础', knowledge_point: 'array', order: 1, status: 'COMPLETED', difficulty: 'BEGINNER', est_minutes: 90, prerequisites: [], is_supplement: false, completed_at: '2026-04-10T10:00:00Z' },
    { node_id: 'node_002', title: '链表原理与实现', knowledge_point: 'linked_list', order: 2, status: 'COMPLETED', difficulty: 'BEGINNER', est_minutes: 120, prerequisites: ['node_001'], is_supplement: false, completed_at: '2026-04-10T14:00:00Z' },
    { node_id: 'node_003', title: '栈与队列', knowledge_point: 'stack', order: 3, status: 'COMPLETED', difficulty: 'BEGINNER', est_minutes: 90, prerequisites: ['node_002'], is_supplement: false, completed_at: '2026-04-11T10:00:00Z' },
    { node_id: 'node_004', title: '哈希表', knowledge_point: 'hash_table', order: 4, status: 'COMPLETED', difficulty: 'INTERMEDIATE', est_minutes: 120, prerequisites: ['node_001'], is_supplement: false, completed_at: '2026-04-12T10:00:00Z' },
    { node_id: 'node_005', title: '排序算法', knowledge_point: 'sorting', order: 5, status: 'IN_PROGRESS', difficulty: 'INTERMEDIATE', est_minutes: 180, prerequisites: ['node_001'], is_supplement: false },
    { node_id: 'node_005a', title: '排序算法补充练习', knowledge_point: 'sorting', order: 6, status: 'PENDING', difficulty: 'INTERMEDIATE', est_minutes: 60, prerequisites: ['node_005'], is_supplement: true },
    { node_id: 'node_006', title: '二叉树基础', knowledge_point: 'binary_tree', order: 7, status: 'PENDING', difficulty: 'INTERMEDIATE', est_minutes: 150, prerequisites: ['node_003'], is_supplement: false },
    { node_id: 'node_007', title: '二叉搜索树', knowledge_point: 'binary_search_tree', order: 8, status: 'PENDING', difficulty: 'INTERMEDIATE', est_minutes: 120, prerequisites: ['node_006'], is_supplement: false },
    { node_id: 'node_008', title: '堆与优先队列', knowledge_point: 'heap', order: 9, status: 'PENDING', difficulty: 'ADVANCED', est_minutes: 120, prerequisites: ['node_006'], is_supplement: false },
    { node_id: 'node_009', title: '图论基础', knowledge_point: 'graph', order: 10, status: 'PENDING', difficulty: 'ADVANCED', est_minutes: 180, prerequisites: ['node_006'], is_supplement: false },
  ],
  created_at: '2026-04-10T08:00:00Z',
}

// ---- Evaluation (with enhanced dimensions) ----
export const mockEvaluation: Evaluation = {
  eval_id: 'eval_e1f2g3',
  type: 'MINI_QUIZ',
  knowledge_point: 'sorting',
  question_count: 3,
  status: 'PENDING',
  questions: [
    { question_id: 'q_001', type: 'SINGLE_CHOICE', content: '快速排序的平均时间复杂度是？', options: [{ key: 'A', value: 'O(n)' }, { key: 'B', value: 'O(n log n)' }, { key: 'C', value: 'O(n²)' }, { key: 'D', value: 'O(log n)' }], correct_answer: 'B', explanation: '快速排序平均时间复杂度为 O(n log n)，最坏情况为 O(n²)。' },
    { question_id: 'q_002', type: 'FILL_BLANK', content: '归并排序的空间复杂度为 ____', correct_answer: 'O(n)', explanation: '归并排序需要额外 O(n) 的空间用于合并操作。' },
    { question_id: 'q_003', type: 'SINGLE_CHOICE', content: '以下哪种排序算法是稳定的？', options: [{ key: 'A', value: '快速排序' }, { key: 'B', value: '堆排序' }, { key: 'C', value: '归并排序' }, { key: 'D', value: '选择排序' }], correct_answer: 'C', explanation: '归并排序在合并过程中保持相同元素的相对顺序，因此是稳定排序。' },
  ],
  created_at: '2026-04-13T15:00:00Z',
}

export const mockEvalHistory: Evaluation[] = [
  { eval_id: 'eval_h001', type: 'MINI_QUIZ', knowledge_point: 'array', score: 100, mastery_level: 0.85, learning_efficiency: 0.92, progress_trend: 'UP', weak_point_analysis: [], question_count: 3, correct_count: 3, time_spent_seconds: 120, status: 'ANALYZED', questions: [], recommendation: { action: 'ADVANCE', message: '数组掌握良好，继续学习链表。' }, created_at: '2026-04-10T11:00:00Z' },
  { eval_id: 'eval_h002', type: 'MINI_QUIZ', knowledge_point: 'linked_list', score: 67, mastery_level: 0.72, learning_efficiency: 0.65, progress_trend: 'STABLE', weak_point_analysis: ['指针操作不熟练'], question_count: 3, correct_count: 2, time_spent_seconds: 180, status: 'ANALYZED', questions: [], recommendation: { action: 'ADVANCE', message: '链表基础掌握，建议继续。' }, created_at: '2026-04-10T15:00:00Z' },
  { eval_id: 'eval_h003', type: 'MINI_QUIZ', knowledge_point: 'stack', score: 100, mastery_level: 0.68, learning_efficiency: 0.88, progress_trend: 'UP', weak_point_analysis: [], question_count: 3, correct_count: 3, time_spent_seconds: 90, status: 'ANALYZED', questions: [], recommendation: { action: 'ADVANCE', message: '栈与队列掌握良好！' }, created_at: '2026-04-11T11:00:00Z' },
  { eval_id: 'eval_h004', type: 'MINI_QUIZ', knowledge_point: 'hash_table', score: 33, mastery_level: 0.45, learning_efficiency: 0.35, progress_trend: 'DOWN', weak_point_analysis: ['哈希冲突处理理解不足', '开放寻址法与链地址法混淆'], question_count: 3, correct_count: 1, time_spent_seconds: 240, status: 'ANALYZED', questions: [], recommendation: { action: 'SUPPLEMENT', message: '哈希表掌握不牢固，建议补充练习。' }, created_at: '2026-04-12T11:00:00Z' },
]

// ---- Notifications ----
export const mockNotifications: Notification[] = [
  { id: 'noti_001', type: 'DAILY_RECOMMEND', title: '今日推荐学习', content: '根据你的学习进度，建议今天学习「排序算法」，预计用时 30 分钟。', is_read: false, created_at: '2026-04-14T08:00:00Z', action_url: '/app/path' },
  { id: 'noti_002', type: 'EVAL_RESULT', title: '评估结果出炉', content: '你的「哈希表」评估得分 33 分，建议进行补充练习。', is_read: false, created_at: '2026-04-12T11:05:00Z', action_url: '/app/evaluate' },
  { id: 'noti_003', type: 'STUDY_REMINDER', title: '学习时间到啦', content: '你设定的每日学习时间到了，今天目标学习 60 分钟，加油！', is_read: true, created_at: '2026-04-13T19:00:00Z' },
  { id: 'noti_004', type: 'ACHIEVEMENT', title: '🏅 成就解锁', content: '连续学习 3 天！保持这个节奏，你会越来越棒的。', is_read: true, created_at: '2026-04-12T20:00:00Z' },
  { id: 'noti_005', type: 'INACTIVE_RECALL', title: '复习提醒', content: '距上次学习「链表」已过 3 天，根据遗忘曲线建议复习', is_read: false, created_at: '2026-04-14T09:00:00Z', action_url: '/app/chat' },
  { id: 'noti_006', type: 'INACTIVE_RECALL', title: '复习提醒', content: '距上次学习「栈与队列」已过 5 天，记忆可能衰退，建议巩固', is_read: false, created_at: '2026-04-14T09:30:00Z', action_url: '/app/chat' },
]

// ---- Agent Steps (multi-agent simulation) ----
export const mockAgentSteps: AgentStep[] = [
  { agent: 'OrchestratorAgent', icon: '🔍', label: '正在分析你的需求...', status: 'pending' },
  { agent: 'DocAgent', icon: '📄', label: '正在生成专业文档...', status: 'pending' },
  { agent: 'MindmapAgent', icon: '🧠', label: '正在整理思维导图...', status: 'pending' },
  { agent: 'QuizAgent', icon: '📝', label: '正在出题...', status: 'pending' },
  { agent: 'CodeAgent', icon: '💻', label: '正在编写代码案例...', status: 'pending' },
  { agent: 'VideoAgent', icon: '🎬', label: '正在生成教学视频...', status: 'pending' },
]

// ---- Personalized mock reply (references user profile) ----
export const mockPersonalizedReply = `## 二叉树入门

根据你的学习画像，你偏好**代码示例驱动**的学习方式，认知风格为**实践型**，所以我用大量代码来讲解。

### 什么是二叉树？

二叉树是每个节点最多有两个子节点的树形结构。

\`\`\`python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# 构建一棵简单的二叉树
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)
\`\`\`

### 前序遍历

\`\`\`python
def preorder(root):
    if not root:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)

print(preorder(root))  # [1, 2, 4, 5, 3]
\`\`\`

> 💡 你之前在递归终止条件上容易出错，所以特别注意 \`if not root: return []\` 这个 base case。

\`\`\`mermaid
graph TD
    A[1] --> B[2]
    A --> C[3]
    B --> D[4]
    B --> E[5]
\`\`\`

> ✅ 已根据本次对话更新你的学习画像`

// ---- Today Recommendation ----
export const mockTodayRecommendation = {
  knowledge_point: 'sorting',
  title: '排序算法',
  reason: '你正在学习排序算法，距离掌握还差一点点',
  est_minutes: 30,
  path_node_id: 'node_005',
}
