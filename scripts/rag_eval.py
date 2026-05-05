#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from app.rag.retriever import retrieve  # noqa: E402


DEFAULT_CASES = [
    {
        "id": "os_process",
        "query": "什么是进程？",
        "expected_source_contains": "进程",
    },
    {
        "id": "os_interrupt",
        "query": "操作系统中断的作用是什么？",
        "expected_source_contains": "中断",
    },
]


def load_cases(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return DEFAULT_CASES
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("case file must contain a JSON array")
    return payload


def evaluate_case(case: dict[str, Any], top_k: int) -> dict[str, Any]:
    start = time.monotonic()
    results = retrieve(str(case["query"]), top_k=top_k)
    latency_ms = int((time.monotonic() - start) * 1000)
    expected_source = str(case.get("expected_source_contains", ""))
    source_hit = (
        not expected_source
        or any(expected_source in str(item.get("source", "")) for item in results)
    )
    return {
        "id": case.get("id"),
        "query": case["query"],
        "passed": bool(results) and source_hit,
        "source_hit": source_hit,
        "result_count": len(results),
        "latency_ms": latency_ms,
        "top_sources": [item.get("source", "") for item in results],
        "top_scores": [item.get("score") for item in results],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run offline RAG retrieval checks.")
    parser.add_argument("--cases", type=Path, help="JSON array of eval cases")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    results = [evaluate_case(case, args.top_k) for case in cases]
    passed = sum(1 for item in results if item["passed"])
    report = {
        "passed": passed,
        "total": len(results),
        "pass_rate": round(passed / len(results), 3) if results else 0,
        "results": results,
    }

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
