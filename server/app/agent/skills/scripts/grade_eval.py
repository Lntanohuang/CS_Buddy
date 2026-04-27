from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

EVALS_FILE = Path(__file__).resolve().parents[1] / "evals" / "evals.json"
REQUIRED_FIELDS = {"question_id", "type", "correct_answer", "explanation"}
ALLOWED_TYPES = {"SINGLE_CHOICE", "FILL_BLANK"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="对 TutorAgent 评测结果进行启发式打分")
    parser.add_argument("results_file", help="run_eval.py 输出的结果 JSON 文件路径")
    return parser.parse_args()


def load_eval_map() -> dict[int, dict[str, Any]]:
    payload = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload.get("evals", [])}


def load_results(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload["results"]
    raise ValueError("结果文件格式无效，应为列表或包含 results 列表的对象")


def _has_code_block(text: str) -> bool:
    return bool(re.search(r"```[\s\S]*?```", text))


def _strip_code_fence(text: str) -> str:
    """Strip markdown code fences (```json ... ```) from text."""
    stripped = text.strip()
    match = re.search(r"```(?:json)?\s*\n([\s\S]*?)```", stripped)
    if match:
        return match.group(1).strip()
    return stripped


def _parse_json_array(text: str) -> tuple[list[Any] | None, str]:
    clean = _strip_code_fence(text)
    try:
        data = json.loads(clean)
    except Exception as exc:
        return None, f"JSON 解析失败：{exc}"

    if not isinstance(data, list):
        return None, "JSON 解析成功，但顶层不是数组"

    return data, f"JSON 数组解析成功，长度为 {len(data)}"


def _extract_question_items(text: str) -> tuple[list[dict[str, Any]] | None, str]:
    arr, msg = _parse_json_array(text)
    if arr is None:
        return None, msg

    if not all(isinstance(item, dict) for item in arr):
        return None, "JSON 数组中存在非对象元素"

    return arr, msg


def _is_chinese_majority(text: str) -> tuple[bool, str]:
    letters = [ch for ch in text if unicodedata.category(ch).startswith("L")]
    if not letters:
        return False, "没有可统计的字母字符"

    cjk_count = sum(1 for ch in letters if "\u4e00" <= ch <= "\u9fff")
    ratio = cjk_count / len(letters)
    return ratio > 0.5, f"CJK 字符占比 {ratio:.2f}"


def _check_question_topic(text: str, keywords: list[str], topic_name: str) -> tuple[bool, str]:
    items, msg = _extract_question_items(text)
    if items is None:
        return False, msg

    corpus = " ".join(f"{item.get('question', '')} {item.get('explanation', '')}" for item in items)
    hits = [kw for kw in keywords if kw in corpus]
    if not hits:
        return False, f"未命中 {topic_name} 关键词"
    return True, f"命中 {topic_name} 关键词：{', '.join(hits[:4])}"


def _check_expectation(expectation: str, response: str) -> tuple[bool, str]:
    normalized = response.replace(" ", "").lower()

    if expectation == "output is markdown":
        markers = ["##", "```", "- ", "|"]
        hits = [m for m in markers if m in response]
        return bool(hits), f"Markdown 标记命中：{hits if hits else '无'}"

    if expectation == "contains code example":
        passed = _has_code_block(response)
        return passed, "检测到 ``` 代码块" if passed else "未检测到 ``` 代码块"

    if expectation == "mentions time complexity O(n log n)":
        passed = "o(nlogn)" in normalized or "o(nlogn)" in normalized
        if "o(nlogn)" not in normalized:
            passed = "o(nlogn)" in normalized or "o(nlogn)" in normalized
        # 兼容保留空格写法
        if not passed:
            passed = "o(nlogn)" in response.lower().replace(" ", "") or "o(n log n)" in response.lower()
        return passed, "命中 O(n log n) 复杂度描述" if passed else "未命中 O(n log n) 或 O(nlogn)"

    if expectation == "output is valid JSON array":
        arr, msg = _parse_json_array(response)
        return arr is not None, msg

    if expectation == "contains exactly 3 questions":
        items, msg = _extract_question_items(response)
        if items is None:
            return False, msg
        passed = len(items) == 3
        return passed, f"题目数量为 {len(items)}"

    if expectation == "each has question_id/type/correct_answer/explanation fields":
        items, msg = _extract_question_items(response)
        if items is None:
            return False, msg

        missing_records: list[str] = []
        for idx, item in enumerate(items, start=1):
            missing = sorted(REQUIRED_FIELDS - set(item.keys()))
            if missing:
                missing_records.append(f"第{idx}题缺少 {missing}")

        if missing_records:
            return False, "; ".join(missing_records)
        return True, "所有题目均包含必需字段"

    if expectation == "types are SINGLE_CHOICE or FILL_BLANK":
        items, msg = _extract_question_items(response)
        if items is None:
            return False, msg

        types = [str(item.get("type", "")) for item in items]
        invalid = [t for t in types if t not in ALLOWED_TYPES]
        if invalid:
            return False, f"存在非法题型：{invalid}"
        return True, f"题型合法：{types}"

    if expectation == "response contains follow-up question(s)":
        passed = "？" in response or "?" in response
        return passed, "检测到问号" if passed else "未检测到问号"

    if expectation in {"does NOT directly teach content", "does NOT give a full lesson"}:
        no_code = not _has_code_block(response)
        short_enough = len(response) < 500
        passed = no_code and short_enough
        return passed, f"长度 {len(response)}，代码块存在={not no_code}"

    if expectation == "uses bullet points":
        passed = "- " in response or "• " in response
        return passed, "检测到项目符号" if passed else "未检测到项目符号"

    if expectation == "is in Chinese":
        return _is_chinese_majority(response)

    if expectation == "explains BST property (left < root < right)":
        patterns = [
            "left<root<right",
            "左<根<右",
            "左子树<根<右子树",
            "左子树的值都小于根",
            "右子树的值都大于根",
        ]
        hits = [p for p in patterns if p in normalized or p in response]
        return bool(hits), f"BST 性质命中：{hits if hits else '无'}"

    if expectation == "contains comparison":
        keywords = ["区别", "对比", "相比", "比较"]
        hits = [kw for kw in keywords if kw in response]
        if "|" in response:
            hits.append("表格分隔符 |")
        return bool(hits), f"对比信息命中：{hits if hits else '无'}"

    if expectation == "mentions at least 2 methods (chaining, open addressing)":
        chain_hits = [kw for kw in ["chaining", "拉链", "链地址", "链式"] if kw in response.lower() or kw in response]
        open_hits = [kw for kw in ["open addressing", "开放寻址", "线性探测", "二次探测", "双重散列"] if kw in response.lower() or kw in response]
        passed = bool(chain_hits) and bool(open_hits)
        return passed, f"chaining={chain_hits if chain_hits else '无'}; open_addressing={open_hits if open_hits else '无'}"

    if expectation == "questions are about linked list concepts":
        keywords = ["链表", "单链表", "双链表", "next", "指针", "快慢指针"]
        return _check_question_topic(response, keywords, "链表")

    if expectation == "questions are about binary tree":
        keywords = ["二叉树", "树", "节点", "前序", "中序", "后序", "层序", "叶子", "高度"]
        return _check_question_topic(response, keywords, "二叉树")

    if expectation == "response asks about specific area/goal":
        has_question = "？" in response or "?" in response
        keywords = ["哪方面", "哪个方向", "具体", "目标", "想达到", "短期", "长期", "优先"]
        hits = [kw for kw in keywords if kw in response]
        passed = has_question and bool(hits)
        return passed, f"问号={has_question}，命中关键词={hits if hits else '无'}"

    if expectation == "friendly tone":
        markers = ["我们可以", "一起", "我来帮你", "别担心", "没关系", "一步步", "当然", "加油"]
        hits = [m for m in markers if m in response]
        return bool(hits), f"友好语气命中：{hits if hits else '无'}"

    if expectation == "response asks what specifically about data structures":
        has_question = "？" in response or "?" in response
        has_topic = "数据结构" in response
        specific_hits = [kw for kw in ["具体", "哪一块", "哪部分", "想学什么", "想了解什么", "比如"] if kw in response]
        passed = has_question and has_topic and bool(specific_hits)
        return passed, f"问号={has_question}，数据结构={has_topic}，具体化关键词={specific_hits if specific_hits else '无'}"

    if expectation == "asks about user's level or goal":
        has_question = "？" in response or "?" in response
        hits = [kw for kw in ["基础", "水平", "经验", "入门", "进阶", "目标", "考试", "面试", "项目"] if kw in response]
        passed = has_question and bool(hits)
        return passed, f"问号={has_question}，水平/目标关键词={hits if hits else '无'}"

    return False, "未实现该期望的启发式规则"


def main() -> None:
    args = parse_args()
    results_path = Path(args.results_file)

    eval_map = load_eval_map()
    results = load_results(results_path)

    expectation_results: list[dict[str, Any]] = []

    for result in results:
        eval_id = result.get("eval_id")
        if eval_id not in eval_map:
            continue

        response = str(result.get("response", ""))
        expectations = eval_map[eval_id].get("expectations", [])

        for expectation in expectations:
            passed, evidence = _check_expectation(expectation, response)
            expectation_results.append(
                {
                    "eval_id": eval_id,
                    "text": expectation,
                    "passed": passed,
                    "evidence": evidence,
                }
            )

    passed_count = sum(1 for item in expectation_results if item["passed"])
    total_count = len(expectation_results)
    failed_count = total_count - passed_count
    pass_rate = round((passed_count / total_count), 2) if total_count else 0.0

    grading = {
        "expectations": expectation_results,
        "summary": {
            "passed": passed_count,
            "failed": failed_count,
            "total": total_count,
            "pass_rate": pass_rate,
        },
    }

    output_path = results_path.with_name(f"grading_{results_path.stem}.json")
    output_path.write_text(json.dumps(grading, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(grading, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
