# ELO roadmap — 74 to ~99 without leaving the league
Date: 2026-09-06 | base: 2.8.0 (74/100) | v1

Constraints (non-negotiable): sub-second builds, single-digit-ms runtime,
offline, zero deps, mobile-safe. Anything violating these is OUT, however
strong. HMAC dropped for cause (public runner = public key = theater).

## Batch 1 — crypto round (+12): per-file salt, rotation, splitting, numbers
- Salt in manifest (`"k": <hex>`): XOR schedule + shuffle seed derive from
  salt, not constants. Same input, different bytes per build. Determinism
  becomes seed-determinism (`--seed`, default random? NO — default fixed for
  diffable builds; flag opts into variance).
- Segment rotation: rotate each blob by salt-derived offset pre-base64.
- splitStrings: long literals split + runtime concat (AST-free: string split
  at token level is safe — no scope analysis needed).
- numbersToExpressions: decimal ints to hex + trivial arithmetic (`200`→`0xc8`).
- All four are representation-only (semantics provably untouched) → battery
  extends naturally (decrypt-compare + run-compare already cover them).

## Batch 2 — integrity round (+8): tripwire, seed, cross-file cache
- Runner self-tripwire: `forgescript.js` embeds its own length hash; boot
  compares, mismatch → silent null. Beautifiers/tamperers trip it. Zero
  runtime cost past one integer compare. (Runner content changes per forge
  version only — hash generated at forge build... note: runner is SOURCE here,
  hash must be injected at forge release time, not per-consumer build. Design:
  `tools/seal_runner.py` run by US on runner edits; checker verifies seal.)
- `--seed N`: shuffle + salt derive from N. Default: fixed (today's behavior).
- Cross-file identifier cache (`--cache f.json`): consistent short names
  across files (smaller total, harder per-file analysis). Opt-in; default off
  (independent builds stay default).

## Batch 3 — simplify round (+5): constant folding, boolean squeeze
- `true`→`!0`, `false`→`!1`, `undefined`→`void 0` (careful: keep `undefined`
  where it can be shadowed — function-scope check or skip inside functions
  with an `undefined` param... simplest: only top-level/module scope? NO —
  simplest SAFE: `void 0` only where no shadowing possible = never inside a
  scope declaring `undefined`. Implement via poison-style scope scan, or skip
  undefined entirely and do true/false only (always safe).
- Constant folding for pure numeric/string-binary ops (`2+3`→`5`). Needs
  paren-aware expression scan on mask — bounded, no AST.
- Dead-branch drop (`if(false){...}`, `while(false)...`)? RISKY without data
  flow (side effects hide in branches... `if(false){foo()}` IS safe to drop
  (unreachable), `if(true){a}else{b}` → keep `a`... `if` with truthy/falsy
  LITERALS only. Small, safe subset. Optional within batch.

## Explicitly NOT queued (league exit or theater)
- Control-flow flattening, VM bytecode, debugProtection intervals (perf/mobile).
- HMAC with public runner (theater — see decision note).
- DomainLock (owner-declined: developer choice, not forge).
- Dead-code injection (violates minimalism rule; noise ≠ protection).

## Verification per batch
- Battery extends: decrypt-compare covers crypto; run-compare covers simplify;
  tripwire tested by flipping one runner byte (must refuse).
- Version per batch (2.9/2.10/2.11?) or single 2.9.0 — owner call at build time.

## 2.9.0 scope notes (2026-09-06, honest cuts)
- Runner self-tripwire: DROPPED as designed (self-measurement is impossible
  without self-read; a dev-time seal would merely duplicate git). The refusal
  paths + battery stay the integrity story.
- Cross-file ident cache: DEFERRED to 2.10 (order-dependent builds need a
  cache-invalidation story first; wrong cache = silent cross-file breakage).
- Shipped in 2.9.0: salt+rotation+seed, splitStrings, num, simp, DEFAULT.
