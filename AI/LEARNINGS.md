# LEARNINGS — AI memory (AI: append here, never delete)

## Conventions (taste-level, don't churn these)
- Branch names lowercase. Never rename for style alone.
- Micro-steps: one decision per message, short answers, execute immediately after approval.

## 2026-09-05 — first pass
- `strip_comments` must be string-aware (`'...'`, `"..."`, `` `...` ``) or URLs and fake
  comment-like content inside strings get corrupted. State machine, not regex.
- Fixture-driven: `tests/basic.js` covers trailing/block/fake comments. Eyeball output each run.
