from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request


def _split_top_level(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in value:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
            current.append(char)
            continue
        if char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _strip_comment(line: str) -> str:
    quote: str | None = None
    for idx, char in enumerate(line):
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char == "#":
            return line[:idx]
    return line


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [_parse_scalar(item) for item in _split_top_level(inner)]
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1].strip()
        result: dict[str, Any] = {}
        if not inner:
            return result
        for item in _split_top_level(inner):
            key, raw_val = item.split(":", 1)
            result[key.strip()] = _parse_scalar(raw_val)
        return result
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def _load_cases(path: str | Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_key: str | None = None

    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw_line).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if stripped == "cases:":
            continue
        if indent == 2 and stripped.startswith("- "):
            current = {}
            cases.append(current)
            current_key = None
            item = stripped[2:].strip()
            if item:
                key, value = item.split(":", 1)
                current[key.strip()] = _parse_scalar(value)
            continue
        if current is None:
            raise ValueError(f"Invalid cases.yaml line before first case: {raw_line}")
        if indent == 4 and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                current[key] = _parse_scalar(value)
                current_key = None
            else:
                current[key] = []
                current_key = key
            continue
        if indent == 6 and stripped.startswith("- ") and current_key:
            current[current_key].append(_parse_scalar(stripped[2:].strip()))
            continue
        raise ValueError(f"Unsupported cases.yaml line: {raw_line}")

    return cases


def _iter_sse_events(response: Any) -> Any:
    data_lines: list[str] = []
    for raw_line in response:
        line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
        if not line:
            if data_lines:
                payload = "\n".join(data_lines)
                data_lines = []
                yield json.loads(payload)
            continue
        if line.startswith(":"):
            continue
        if line.startswith("data:"):
            data_lines.append(line.removeprefix("data:").strip())
    if data_lines:
        yield json.loads("\n".join(data_lines))


def _run_one(server_url: str, case: dict[str, Any], sample_idx: int) -> dict[str, Any]:
    epoch_ms = int(time.time() * 1000)
    body = {
        "session_id": f"eval-{case['id']}-{sample_idx}-{epoch_ms}",
        "message": case["query"],
    }
    req = urllib_request.Request(
        url=f"{server_url.rstrip('/')}/api/v1/chat/stream",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
        },
    )

    answer_parts: list[str] = []
    trace: dict[str, Any] | None = None
    with urllib_request.urlopen(req, timeout=90) as response:
        for event in _iter_sse_events(response):
            event_type = event.get("type")
            if event_type == "token":
                answer_parts.append(event.get("content") or "")
            elif event_type == "done":
                data = event.get("data") or {}
                trace = data.get("trace")
            elif event_type == "error":
                raise RuntimeError(event.get("content") or "stream returned error event")

    return {
        "case_id": case["id"],
        "sample_idx": sample_idx,
        "query": case["query"],
        "answer": "".join(answer_parts),
        "trace": trace,
        **{key: value for key, value in case.items() if key not in {"id", "query"}},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="evals/cases.yaml")
    parser.add_argument("--n", type=int, default=12)
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument("--out", default="evals/results/latest.jsonl")
    parser.add_argument("--server-url", default="http://localhost:8010")
    args = parser.parse_args()

    cases = [case for case in _load_cases(args.cases) if case.get("enabled", True)]
    selected = cases[: args.n]
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("", encoding="utf-8")

    with out_path.open("a", encoding="utf-8") as f:
        for case in selected:
            for sample_idx in range(1, args.k + 1):
                try:
                    record = _run_one(args.server_url, case, sample_idx)
                except (urllib_error.URLError, TimeoutError, OSError, RuntimeError) as exc:
                    record = {
                        "case_id": case["id"],
                        "sample_idx": sample_idx,
                        "query": case["query"],
                        "answer": None,
                        "error": str(exc),
                        "trace": None,
                        **{key: value for key, value in case.items() if key not in {"id", "query"}},
                    }
                f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                f.flush()
                print(f"recorded {record['case_id']} sample={sample_idx}", file=sys.stdout)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
