# LearnPal Verification Evals

This directory implements the V1-精简 verification system described in
`docs/VERIFICATION_ROADMAP.md`.

## cases.yaml

`cases.yaml` contains one top-level `cases:` list. Each enabled case has:

- `id`: stable id such as `q01`
- `query`: user message sent to `/api/v1/chat/stream`
- `expected_skill`: `quiz`, `explain`, or `clarify`
- `tags`: labels for filtering and summaries
- `expected_facts`: substrings that must appear in the answer
- `must_not_contain`: substrings that must not appear
- `must_format`: `markdown`, `json_array`, or `none`
- `expected_contexts`: optional RAG ground truth as `{source, header_1, header_2, header_3}`
- `difficulty`: `easy`, `medium`, or `hard`
- `enabled`: whether the runner includes the case

## Adding A Case

Append a new mapping under `cases:` and choose exact deterministic checks first.
Use short `expected_facts` that are likely to appear verbatim in a good answer,
then rely on the LLM judge for semantic quality.

## Labeling expected_contexts

For RAG-covered cases, inspect the retrieved markdown chunk identity and fill:

```yaml
expected_contexts:
  - {source: "file.md", header_1: "章标题", header_2: "节标题"}
```

The deterministic context rule currently checks `(source, header_1)`. Extra
headers are kept for judge context and future tightening.

## Fast vs Full

`scripts/verify.sh --fast` runs `k=2` samples per case. Majority voting means
both samples must pass. `--full` runs `k=3`, where at least two samples must
pass. Both modes run preflight, smoke, eval generation, judge, assertions, and
summary.

## Tunable thresholds

`evals/scripts/assert_eval.py` owns the blocking policy:

- Per-record deterministic checks
- Per-case 2/3 majority vote
- Aggregate pass-rate regression guard
- `2pp` drop threshold and two-proportion z-test `p < 0.05`

`history.jsonl` is append-only and acts as the regression baseline.
