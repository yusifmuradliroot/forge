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

## 2026-09-08 — v2.10.0 ELO round (G1-G4 from elo-gains-v1)
- Finding: 2.9.0 salted pack but crypt still XOR-0x5A static across ALL files.
  Fix: per-build key via FORGE_SEED, default 0x5A (diffable), stub carries its
  own key literal (old files unaffected). Default short output proven
  byte-identical to 2.9.0 (old-vs-new differential on the same input).
- short sorted+sequential renamed identically forever; FORGE_SEED now shuffles
  assignment order (mangled-shuffled precedent, cheap form).
- uni: short ASCII strings were plaintext; \xNN escapes with crypt's skip-set,
  disjoint by length (<12). Non-ASCII skipped (unicode_escape round-trip unsafe).
- scan.py gained sig_text + template_inner_spans; crypt imports them (its own
  copies deleted) and uni shares them -- ONE scanner implementation per concept.
- seed.py is the single variance source; pack keeps its proven copy untouched.
- Declined again with cause: control-flow/VM/dead-code/HMAC/domainLock.
  Predicted score 58 -> ~65 (names +1, strings +3, workflow +3).

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

## 2026-09-05 — bootstrap proof (embedded runner == original)
- Question was how the runner gets embedded safely the FIRST time and how forge
  verifies it. Answer: --embed checks size cap + must-contain, then the host chain
  processes it inline. Proof: same .fs through embedded-renamed runner and original
  runner returned identical results (42=42). No separate bootstrap step needed —
  the chain IS the bootstrap, differentially verified.
- Test-design lesson: Function-constructed code returns undefined without explicit
  `return` (spec) — fixtures for behavior comparison must return values.

## 2026-09-05 — false alarm: compare like with like
- A pack round-trip "mismatch" was my test bug: decoded output (post-crypt bytes)
  was compared against the PRE-chain file. crypt legitimately grows size (hex).
  Correct check: decode === --dev output (same stage). It matched byte-exact.
- Lesson: differential tests must pin the EXACT stage on both sides.
