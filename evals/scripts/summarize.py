from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


METRIC_KEYS = ("answer_quality", "faithfulness", "answer_relevancy", "context_recall")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _mean_metric(records: list[dict[str, Any]], key: str) -> float | None:
    values = [record.get(key) for record in records if record.get(key) is not None]
    return round(mean(float(value) for value in values), 4) if values else None


def _git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    case_ids = sorted({record["case_id"] for record in records})
    passed_case_ids = {
        record["case_id"]
        for record in records
        if record.get("case_pass") is True
    }
    per_case_counts: dict[str, int] = {}
    for record in records:
        per_case_counts[record["case_id"]] = per_case_counts.get(record["case_id"], 0) + 1

    aggregate: dict[str, Any] = {
        "pass_rate": len(passed_case_ids) / len(case_ids) if case_ids else 0.0,
        "n_cases": len(case_ids),
        "k_samples": max(per_case_counts.values()) if per_case_counts else 0,
        "total_records": len(records),
        "failed_records": sum(1 for record in records if not record.get("layer1_pass")),
    }
    for key in METRIC_KEYS:
        aggregate[key] = _mean_metric(records, key)
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest", default="evals/results/latest.jsonl")
    parser.add_argument("--history", default="evals/results/history.jsonl")
    args = parser.parse_args()

    records = _load_jsonl(Path(args.latest))
    aggregate = _aggregate(records)
    history_path = Path(args.history)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "aggregate": aggregate,
    }
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(history_record, ensure_ascii=False, separators=(",", ":")) + "\n")

    rows = [
        ("pass_rate", f"{aggregate['pass_rate']:.3f}"),
        ("n_cases", str(aggregate["n_cases"])),
        ("k_samples", str(aggregate["k_samples"])),
        ("failed_records", str(aggregate["failed_records"])),
    ]
    rows.extend((key, str(aggregate[key])) for key in METRIC_KEYS)
    print("metric\tvalue", file=sys.stdout)
    for key, value in rows:
        print(f"{key}\t{value}", file=sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
