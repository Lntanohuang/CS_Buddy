from langchain_core.tools import tool


@tool
def get_profile(user_id: str) -> dict:
    """获取用户画像（模拟数据）。"""
    return {
        "user_id": "usr_a1b2c3d4",
        "major": "计算机科学与技术",
        "current_level": "INTERMEDIATE",
        "learning_goal": "EXAM_PREP",
        "preferred_style": "PRACTICE",
        "cognitive_style": "PRACTICAL",
        "error_patterns": [
            "容易混淆时间复杂度和空间复杂度",
            "对递归边界条件不敏感",
            "经常忽略空指针与越界检查",
        ],
        "daily_time_minutes": 60,
        "knowledge_mastery": {
            "数组": 0.78,
            "链表": 0.72,
            "栈与队列": 0.66,
            "树": 0.51,
            "图": 0.43,
        },
        "weak_points": ["图的遍历", "动态规划状态设计", "红黑树性质"],
        "style_weights": {
            "示例驱动": 0.5,
            "步骤拆解": 0.3,
            "类比解释": 0.2,
        },
    }


@tool
def search_knowledge(query: str) -> str:
    """搜索知识库（模拟数据）。"""
    return (
        "【知识库命中】数据结构是组织和存储数据的方式，目标是在不同场景下实现更高效的访问与修改。"
        "常见数据结构包括数组、链表、栈、队列、哈希表、树、图。"
        "选择数据结构时应优先结合操作类型（查找/插入/删除）、数据规模和时间复杂度要求。"
        f"当前查询：{query}。"
    )
