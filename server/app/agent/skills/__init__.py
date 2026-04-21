from app.agent.skills.clarify import CLARIFY_PROMPT
from app.agent.skills.explain import EXPLAIN_PROMPT
from app.agent.skills.quiz import QUIZ_PROMPT

SKILLS = {
    "clarify": CLARIFY_PROMPT,
    "explain": EXPLAIN_PROMPT,
    "quiz": QUIZ_PROMPT,
}

__all__ = ["SKILLS", "CLARIFY_PROMPT", "EXPLAIN_PROMPT", "QUIZ_PROMPT"]
