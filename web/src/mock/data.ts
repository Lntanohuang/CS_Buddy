import type {
  AuthUser,
  UserProfile,
  ChatSession,
  ChatMessage,
  LearningPath,
  Evaluation,
} from '@/types'

// ---- Auth ----
export const mockUser: AuthUser = {
  user_id: 'usr_a1b2c3d4',
  nickname: '小明',
  role: 'STUDENT',
  access_token: 'mock_access_token_xxx',
  refresh_token: 'mock_refresh_token_xxx',
  expires_in: 7200,
}

// ---- Profile ----
export const mockProfile: UserProfile = {
  user_id: 'usr_a1b2c3d4',
  current_level: 'INTERMEDIATE',
  learning_goal: 'EXAM_PREP',
  preferred_style: 'PRACTICE',
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
  style_weights: {
    code_example: 0.6,
    analogy: 0.25,
    text: 0.15,
  },
  subjects: ['DATA_STRUCTURE', 'ALGORITHM'],
  updated_at: '2026-04-13T14:30:00Z',
}

// ---- Chat Sessions ----
export const mockSessions: ChatSession[] = [
  {
    session_id: 'sess_001',
    title: '数据结构学习',
    status: 'ACTIVE',
    message_count: 6,
    created_at: '2026-04-13T10:00:00Z',
    updated_at: '2026-04-13T14:30:00Z',
  },
  {
    session_id: 'sess_002',
    title: '排序算法复习',
    status: 'ACTIVE',
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
    metadata: {
      type: 'resource_card',
      title: '快速排序',
      difficulty: 'INTERMEDIATE',
      est_minutes: 15,
      knowledge_point: 'quick_sort',
    },
    created_at: '2026-04-13T14:00:05Z',
  },
  {
    message_id: 'msg_003',
    session_id: 'sess_001',
    role: 'USER',
    content: '最差情况什么时候会出现？',
    created_at: '2026-04-13T14:05:00Z',
  },
  {
    message_id: 'msg_004',
    session_id: 'sess_001',
    role: 'ASSISTANT',
    content: `最差情况出现在**每次选取的基准都是当前子数组的最大或最小元素**时。

### 典型场景

- 数组已经**完全有序**（升序或降序），且每次选第一个元素作为基准
- 数组中**所有元素相同**

### 为什么是 O(n²)？

每次分区只能减少一个元素，递归深度达到 n 层：
\`\`\`
[1, 2, 3, 4, 5]  pivot=1 → left=[], right=[2,3,4,5]
[2, 3, 4, 5]     pivot=2 → left=[], right=[3,4,5]
[3, 4, 5]        pivot=3 → left=[], right=[4,5]
...
\`\`\`

### 如何避免？

1. **随机选取基准**：\`pivot = arr[random.randint(0, len(arr)-1)]\`
2. **三数取中法**：取首、中、尾三个元素的中位数作为基准
3. 对小数组切换到插入排序（通常阈值为 10-20）`,
    intent: 'learn',
    created_at: '2026-04-13T14:05:08Z',
  },
]

// ---- Simulated streaming reply content ----
export const mockStreamReply = `## 二叉树（Binary Tree）

二叉树是一种每个节点**最多有两个子节点**的树形数据结构。

### 基本概念

- **根节点**（Root）：树的顶部节点
- **叶节点**（Leaf）：没有子节点的节点
- **深度**（Depth）：从根到该节点的边数
- **高度**（Height）：从该节点到最远叶节点的边数

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

# 前序遍历
def preorder(root):
    if not root:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)
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

// ---- Evaluation ----
export const mockEvaluation: Evaluation = {
  eval_id: 'eval_e1f2g3',
  type: 'MINI_QUIZ',
  knowledge_point: 'sorting',
  score: undefined,
  mastery_level: undefined,
  question_count: 3,
  status: 'PENDING',
  questions: [
    {
      question_id: 'q_001',
      type: 'SINGLE_CHOICE',
      content: '快速排序的平均时间复杂度是？',
      options: [
        { key: 'A', value: 'O(n)' },
        { key: 'B', value: 'O(n log n)' },
        { key: 'C', value: 'O(n²)' },
        { key: 'D', value: 'O(log n)' },
      ],
      correct_answer: 'B',
      explanation: '快速排序平均时间复杂度为 O(n log n)，最坏情况为 O(n²)。',
    },
    {
      question_id: 'q_002',
      type: 'FILL_BLANK',
      content: '归并排序的空间复杂度为 ____',
      correct_answer: 'O(n)',
      explanation: '归并排序需要额外 O(n) 的空间用于合并操作。',
    },
    {
      question_id: 'q_003',
      type: 'SINGLE_CHOICE',
      content: '以下哪种排序算法是稳定的？',
      options: [
        { key: 'A', value: '快速排序' },
        { key: 'B', value: '堆排序' },
        { key: 'C', value: '归并排序' },
        { key: 'D', value: '选择排序' },
      ],
      correct_answer: 'C',
      explanation: '归并排序在合并过程中保持相同元素的相对顺序，因此是稳定排序。',
    },
  ],
  created_at: '2026-04-13T15:00:00Z',
}

export const mockEvalHistory: Evaluation[] = [
  {
    eval_id: 'eval_h001',
    type: 'MINI_QUIZ',
    knowledge_point: 'array',
    score: 100,
    mastery_level: 0.85,
    question_count: 3,
    correct_count: 3,
    time_spent_seconds: 120,
    status: 'ANALYZED',
    questions: [],
    recommendation: { action: 'ADVANCE', message: '数组掌握良好，继续学习链表。' },
    created_at: '2026-04-10T11:00:00Z',
  },
  {
    eval_id: 'eval_h002',
    type: 'MINI_QUIZ',
    knowledge_point: 'linked_list',
    score: 67,
    mastery_level: 0.72,
    question_count: 3,
    correct_count: 2,
    time_spent_seconds: 180,
    status: 'ANALYZED',
    questions: [],
    recommendation: { action: 'ADVANCE', message: '链表基础掌握，建议继续。' },
    created_at: '2026-04-10T15:00:00Z',
  },
  {
    eval_id: 'eval_h003',
    type: 'MINI_QUIZ',
    knowledge_point: 'stack',
    score: 100,
    mastery_level: 0.68,
    question_count: 3,
    correct_count: 3,
    time_spent_seconds: 90,
    status: 'ANALYZED',
    questions: [],
    recommendation: { action: 'ADVANCE', message: '栈与队列掌握良好！' },
    created_at: '2026-04-11T11:00:00Z',
  },
  {
    eval_id: 'eval_h004',
    type: 'MINI_QUIZ',
    knowledge_point: 'hash_table',
    score: 33,
    mastery_level: 0.45,
    question_count: 3,
    correct_count: 1,
    time_spent_seconds: 240,
    status: 'ANALYZED',
    questions: [],
    recommendation: { action: 'SUPPLEMENT', message: '哈希表掌握不牢固，建议补充练习。' },
    created_at: '2026-04-12T11:00:00Z',
  },
]
