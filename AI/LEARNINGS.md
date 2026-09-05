# LEARNINGS — AI memory (AI: append here, never delete)

## Conventions (taste-level, don't churn these)
- Branch names lowercase. Never rename for style alone.
- Micro-steps: one decision per message, short answers, execute immediately after approval.

## 2026-09-05 — first pass
- `strip_comments` must be string-aware (`'...'`, `"..."`, `` `...` ``) or URLs and fake
  comment-like content inside strings get corrupted. State machine, not regex.
- Fixture-driven: `tests/basic.js` covers trailing/block/fake comments. Eyeball output each run.

## 2026-09-05 — two real bugs caught by real code (68KB orbit.js)
- Template backtrack: tokenizer reset scan index backwards after `${...}`, swallowing the
  closing backtick and merging following code into a string token (idents silently unrenamed).
  FIX: linear scan with explicit segment tracking, never move the index backwards.
- Object-key encryption: `{"Cache-Control": ...}` became `{__f("..."): ...}` = syntax error.
  FIX: skip strings in key position (followed by `:` with `{`/`,` behind) + skip directives
  (`"use strict"`) + never touch `__*` markers.
- Lesson: fixtures prove the idea, only real files prove the pass. Always run the full chain
  on the biggest real file + `node --check` before calling a pass done.
