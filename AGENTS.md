# LearnPal — Agent Notes

Use this file for Codex or other non-Claude agents. `CLAUDE.md` is still the full project rulebook; `.claude/` hooks are Claude-specific automation only.

## Required Checks

After code changes, run:

```bash
bash scripts/preflight.sh
bash scripts/smoke.sh
```

`smoke.sh` starts FastAPI on port 8010, checks `/health`, verifies real SSE tokens from `POST /api/v1/chat/stream`, runs Playwright against the Vite app, and scans the server log.

## Environment

- Default Python: `/opt/anaconda3/envs/Langchain-sgg/bin/python`
- Override with `LEARNPAL_PYTHON=/path/to/python`
- MongoDB must be reachable at `mongodb://localhost:27017`
- Keep localhost out of proxies; `smoke.sh` sets `NO_PROXY` and uses `curl --noproxy '*'`

## Guardrails

- Do not weaken `scripts/smoke.sh` or `e2e/*.spec.ts` to hide a product bug.
- Do not set `SKIP_SMOKE=1`; that escape hatch is for the user.
- If external LLM or Mongo is unavailable, report the exact failed check instead of claiming completion.
