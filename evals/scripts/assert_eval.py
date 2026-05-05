from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp_path.replace(path)


def _contains_markdown(answer: str) -> bool:
    return bool(re.search(r"```|^#{1,6}\s|^\s*[-*+]\s|\n\d+\.\s", answer, re.MULTILINE))


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    match = re.search(r"```(?:json)?\s*\n([\s\S]*?)```", stripped)
    if match:
        return match.group(1).strip()
    return stripped


def _actionable_contexts(expected_contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in expected_contexts
        if item.get("source") and item.get("source") != "TODO_FILL_SOURCE_MD"
    ]


def _context_pair(context: dict[str, Any]) -> tuple[str, str]:
    return (str(context.get("source", "")), str(context.get("header_1", "")))


def _record_verdict(record: dict[str, Any]) -> tuple[bool, list[str], bool | None]:
    reasons: list[str] = []
    answer = record.get("answer") or ""
    answer_lower = answer.lower()
    trace = record.get("trace") or {}

    if not answer:
        reasons.append(record.get("error") or "empty answer")

    expected_skill = record.get("expected_skill")
    actual_skill = trace.get("skill_id")
    if expected_skill != actual_skill:
        reasons.append(f"expected_skill={expected_skill} trace.skill_id={actual_skill}")

    for fact in record.get("expected_facts", []):
        if str(fact).lower() not in answer_lower:
            reasons.append(f"missing expected_fact={fact}")

    for forbidden in record.get("must_not_contain", []):
        if str(forbidden).lower() in answer_lower:
            reasons.append(f"must_not_contain present={forbidden}")

    must_format = record.get("must_format", "none")
    if must_format == "json_array":
        # LLM 经常把 JSON 包在 ```json ... ``` 里，先去 fence 再 parse
        try:
            parsed = json.loads(_strip_code_fence(answer))
            if not isinstance(parsed, list):
                reasons.append("must_format=json_array parsed value is not a list")
        except json.JSONDecodeError as exc:
            reasons.append(f"must_format=json_array parse failed: {exc}")
    elif must_format == "markdown" and not _contains_markdown(answer):
        reasons.append("must_format=markdown markers not found")

    context_recall_pass: bool | None = None
    expected_contexts = _actionable_contexts(record.get("expected_contexts", []))
    if expected_contexts:
        actual_pairs = {
            _context_pair(item)
            for item in trace.get("retrieved_contexts", [])
            if isinstance(item, dict)
        }
        expected_pairs = {_context_pair(item) for item in expected_contexts}
        context_recall_pass = bool(actual_pairs & expected_pairs)
        if not context_recall_pass:
            reasons.append("expected_contexts not found in trace.retrieved_contexts")

    return not reasons, reasons, context_recall_pass


def _normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def _two_proportion_p_value(current: float, previous: float, n_current: int, n_previous: int) -> float:
    if n_current <= 0 or n_previous <= 0:
        return 1.0
    x_current = current * n_current
    x_previous = previous * n_previous
    p_pool = (x_current + x_previous) / (n_current + n_previous)
    denom = math.sqrt(p_pool * (1 - p_pool) * (1 / n_current + 1 / n_previous))
    if denom == 0:
        return 1.0
    z = (current - previous) / denom
    return _normal_cdf(z)


def _previous_aggregate(history_path: Path) -> dict[str, Any] | None:
    if not history_path.exists():
        return None
    for line in reversed(history_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        aggregate = record.get("aggregate")
        if isinstance(aggregate, dict) and "pass_rate" in aggregate:
            return aggregate
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest", default="evals/results/latest.jsonl")
    parser.add_argument("--history", default="evals/results/history.jsonl")
    args = parser.parse_args()

    latest_path = Path(args.latest)
    records = _load_jsonl(latest_path)
    failures: list[str] = []
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        passed, reasons, context_recall_pass = _record_verdict(record)
        record["layer1_pass"] = passed
        record["layer1_reasons"] = reasons
        record["context_recall_pass"] = context_recall_pass
        by_case[record["case_id"]].append(record)

    passed_cases = 0
    case_verdicts: dict[str, bool] = {}
    for case_id, case_records in sorted(by_case.items()):
        sample_count = len(case_records)
        threshold = math.ceil(sample_count * 2 / 3)
        passed_count = sum(1 for record in case_records if record.get("layer1_pass"))
        case_passed = passed_count >= threshold
        case_verdicts[case_id] = case_passed
        if case_passed:
            passed_cases += 1
        else:
            reason_text = "; ".join(
                f"sample {record.get('sample_idx')}: {', '.join(record.get('layer1_reasons', []))}"
                for record in case_records
                if record.get("layer1_reasons")
            )
            failures.append(f"{case_id}: {passed_count}/{sample_count} passed; {reason_text}")

    for record in records:
        record["case_pass"] = case_verdicts.get(record["case_id"], False)
    _write_jsonl(latest_path, records)

    enabled_cases = len(by_case)
    pass_rate = passed_cases / enabled_cases if enabled_cases else 0.0
    blocked_by_history = False
    previous = _previous_aggregate(Path(args.history))
    if previous:
        previous_rate = float(previous.get("pass_rate", 0.0))
        previous_n = int(previous.get("n_cases") or enabled_cases)
        if pass_rate < previous_rate:
            print(
                f"warn: pass_rate dropped from {previous_rate:.3f} to {pass_rate:.3f}",
                file=sys.stderr,
            )
        if pass_rate <= previous_rate - 0.02:
            p_value = _two_proportion_p_value(pass_rate, previous_rate, enabled_cases, previous_n)
            if p_value < 0.05:
                blocked_by_history = True
                failures.append(
                    f"aggregate: pass_rate {pass_rate:.3f} vs previous {previous_rate:.3f}, p={p_value:.4f}"
                )

    if failures:
        print("verification failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    if blocked_by_history:
        return 1

    print(f"layer1 pass_rate={pass_rate:.3f} ({passed_cases}/{enabled_cases})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
