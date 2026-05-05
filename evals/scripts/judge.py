from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(SERVER_DIR / ".env")

from app.agent.model import create_chat_model  # noqa: E402


SCORE_KEYS = ("answer_quality", "faithfulness", "answer_relevancy", "context_recall")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _message_text(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts)
    return str(content)


def _extract_json_object(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            raise
        parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("judge response is not a JSON object")
    return parsed


def _format_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _render_prompt(rubric: str, record: dict[str, Any]) -> str:
    trace = record.get("trace") or {}
    replacements = {
        "{query}": str(record.get("query", "")),
        "{answer}": str(record.get("answer", "")),
        "{expected_skill}": str(record.get("expected_skill", "")),
        "{expected_facts}": _format_json(record.get("expected_facts", [])),
        "{must_not_contain}": _format_json(record.get("must_not_contain", [])),
        "{retrieved_contexts}": _format_json(trace.get("retrieved_contexts", [])),
        "{expected_contexts}": _format_json(record.get("expected_contexts", [])),
    }
    prompt = rubric
    for slot, value in replacements.items():
        prompt = prompt.replace(slot, value)
    return prompt


def _apply_null_scores(record: dict[str, Any]) -> None:
    for key in SCORE_KEYS:
        record[key] = None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest", default="evals/results/latest.jsonl")
    parser.add_argument("--rubric", default="evals/rubrics/unified_judge.txt")
    parser.add_argument("--judge-model", default="lite")
    args = parser.parse_args()

    latest_path = Path(args.latest)
    rubric = Path(args.rubric).read_text(encoding="utf-8")
    records = _load_jsonl(latest_path)
    model = create_chat_model(temperature=0)
    if args.judge_model:
        model = model.model_copy(update={"model": args.judge_model})

    for record in records:
        answer = record.get("answer")
        if not answer:
            _apply_null_scores(record)
            record["judge_error"] = record.get("error") or "empty answer; judge skipped"
            print(f"judge skipped {record.get('case_id')} sample={record.get('sample_idx')}")
            continue

        prompt = _render_prompt(rubric, record)
        raw_text = ""
        try:
            response = model.invoke(prompt)
            raw_text = _message_text(response)
            parsed = _extract_json_object(raw_text)
            for key in SCORE_KEYS:
                value = parsed.get(key)
                record[key] = None if value is None else float(value)
            record["judge_rationale"] = parsed.get("rationale", "")
            record["judge_issues"] = parsed.get("issues", [])
            record.pop("judge_error", None)
        except Exception as exc:
            _apply_null_scores(record)
            record["judge_error"] = str(exc)
            if raw_text:
                record["judge_raw"] = raw_text
        print(f"judged {record.get('case_id')} sample={record.get('sample_idx')}")

    tmp_path = latest_path.with_suffix(latest_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp_path.replace(latest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
