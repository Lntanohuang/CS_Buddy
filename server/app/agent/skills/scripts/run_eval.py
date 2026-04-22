from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.messages import HumanMessage

from app.agent.graph import build_graph

EVALS_FILE = Path(__file__).resolve().parents[1] / "evals" / "evals.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行 TutorAgent 技能评测")
    parser.add_argument("--skill", choices=["explain", "quiz", "clarify"], help="只运行指定技能")
    parser.add_argument("--id", type=int, dest="eval_id", help="只运行指定评测 ID")
    parser.add_argument(
        "--output-dir",
        default="eval-results",
        help="结果输出目录（默认：eval-results）",
    )
    return parser.parse_args()


def load_evals(skill: str | None = None, eval_id: int | None = None) -> list[dict[str, Any]]:
    payload = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    evals = payload.get("evals", [])

    if skill is not None:
        evals = [item for item in evals if item.get("skill") == skill]
    if eval_id is not None:
        evals = [item for item in evals if item.get("id") == eval_id]

    return evals


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)

    return str(content) if content is not None else ""


async def run_single_eval(graph: Any, eval_case: dict[str, Any]) -> dict[str, Any]:
    timestamp = datetime.now().isoformat(timespec="seconds")
    state = {
        "messages": [HumanMessage(content=eval_case["prompt"])],
        "active_skill": eval_case["skill"],
    }

    try:
        result = await graph.ainvoke(state)
        messages = result.get("messages", [])

        response_text = ""
        if messages:
            last_message = messages[-1]
            response_text = _content_to_text(getattr(last_message, "content", ""))

        return {
            "eval_id": eval_case["id"],
            "skill": eval_case["skill"],
            "prompt": eval_case["prompt"],
            "response": response_text,
            "status": "success",
            "timestamp": timestamp,
        }
    except Exception as exc:  # pragma: no cover
        return {
            "eval_id": eval_case["id"],
            "skill": eval_case["skill"],
            "prompt": eval_case["prompt"],
            "response": str(exc),
            "status": "error",
            "timestamp": timestamp,
        }


async def main() -> None:
    args = parse_args()
    evals = load_evals(skill=args.skill, eval_id=args.eval_id)

    if not evals:
        print("未找到匹配的评测用例。")
        return

    graph = build_graph()
    results: list[dict[str, Any]] = []

    for eval_case in evals:
        results.append(await run_single_eval(graph, eval_case))

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"results_{run_timestamp}.json"
    output_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"评测完成，共 {len(results)} 条，结果文件：{output_file}")


if __name__ == "__main__":
    asyncio.run(main())
