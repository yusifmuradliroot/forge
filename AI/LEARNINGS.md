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

## Working with this user
- Approves fast ("ekle", "yaz", "evet", "devam") — execute immediately.
- Strategic calls stay with user; max 2-3 options, recommend one.
- When torn between designs, STOP and discuss (explicit user instruction).
