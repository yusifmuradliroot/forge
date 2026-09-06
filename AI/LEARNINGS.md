# LEARNINGS — AI memory (AI: append here, never delete)

## Conventions (taste-level, don't churn these)
- Branch names lowercase. Micro-steps: one decision per message, execute right after approval.

## Carried over from the 0.4.0 line (still valid for the rebuild)
- Tokenizer rules: string-aware (`' " \`` + `${}`), regex-aware, comments opaque.
  NEVER move the scan index backwards — it silently merges following code into strings.
- `short` (mangle): rename ONLY single-declaration names; skip properties (`obj.x`),
  object keys (`x:`), `new x`, globals, reserved words.
- `crypt`: skip short strings, `__*` markers, directives (`"use strict"`), object-key
  position (`{"k": v}` breaks if encrypted), templates with `${}`.
- Verification ladder: fixture → full chain → real biggest file → `node --check` →
  node runtime output identical. Fixtures prove the idea; only real files prove the pass.
- `pack` output carries a version tag so loaders can detect packed payloads.
- Minimalism reversal: decoys/fake notes were built then deleted — bloat. Never again.

## 2026-09-05 — v2 bug-hunt (found 2, fixed 2, battery green)
- Sig-side mismatch: python signed ciphertext blobs, JS verified decoded text.
  FIX: sign ciphertext on both sides (verify-before-decrypt falls out for free).
- UTF-8 pack bug (from ANALYSIS): fixed structurally — pack works on UTF-8 bytes,
  runner decodes via TextDecoder. Turkish/emoji proven.
- Scope lesson (honest downgrade): true chunked EXECUTION is impossible without a
  scope-aware splitter (separate Function calls share no lexical scope). FS:2 segments
  are transport-level; documented, not oversold. v3 needs a real compiler step.
- Battery that must stay green: FNV vector, e2e identical, tamper×3 refused,
  determinism, adversarial probes, 68KB byte-exact, checker PASS.
- Residual risk (untestable here): devtools-open path, mobile Firefox + Violentmonkey.

## 2026-09-05 — release checklist gap
- README went stale during the v2 rush (missing --dev, FS:2, version note) and the user
  caught it. Lesson: every version bump MUST include README + CHANGELOG + WHEREWEARE
  in the same commit. Docs are part of "done".

## Working with this user
- Approves fast ("ekle", "yaz", "evet", "devam") — execute immediately.
- Strategic calls stay with user; max 2-3 options, recommend one.
- When torn between designs, STOP and discuss (explicit user instruction).

## 2026-09-05 — regex/division disambiguation needs the pending buffer
- short.py treated `/` after `(` as division because `(` sat in the unflushed buf,
  invisible to the check. `replace(/\s+/g)` became `replace(/\s+/ah)` (flag eaten
  as identifier) → invalid regex in forged output. Caught only by running the FULL
  chain on real code (voyager), never by unit fixtures.
- FIX: check buf first; flags restricted to dgimsuvy. Lesson: tokenizer lookbehind
  must include unflushed state, and every tokenizer fix gets a torture fixture.
