# ANALYSIS.md — SUPERSEDED

This file described v1.0.0 theory (FS:1 tag, pending v2 list). Everything in its v2 work list shipped (FS:2 segments, signature,
per-segment keys, dev mode). Kept verbatim below for history; for the
current model read `FORMAT.md` (spec), `LIMITS.md` (honest limits) and
`../ai-reports/2026-09-06-deep-audit-v2.5.0.md` (findings).

---

# forge deep analysis (v1.0.0) — how it works, where it breaks, what v2 holds

This file records theory + probe-tested results. Deliberately plain language.

## 1. What the pipeline does (proven)

`strip → short → crypt → pack` — every step is a text transform, code is never executed.

| Step | Guarantee | Proof |
|---|---|---|
| `strip` | removes comments, never touches strings/regex/templates | fixture + division-vs-regex probe (`a/b/2` vs `/ab+c/gi` distinguished) |
| `short` | renames ONLY single-declaration names; shadowing, properties (`o.x`), keys (`{x:}`), `new x`, globals untouched | torture fixture: shadowed `alpha` kept, `beta` as key/property kept, regex/string content intact |
| `crypt` | encrypts long strings; short/`__*`/directive/key/template strings kept | node-verified identical output |
| `pack` | whole file into a blob, `FS:1` tag | node `--check` OK |
| runner | reads tag → gate (anti-debug) → decrypts → runs → wipes; refuses on bad tag | wrong tag/empty input → null, nothing runs |

End to end: raw JS → `.fs` → runner → **identical behavior** (also on a 68KB real file).

## 2. BUG found (hotfix required)

**Non-ASCII content breaks in pack.** Turkish identifiers/literals or emoji turn into
garbage at pack time. Cause: pack fits every char into 2 hex digits; Turkish/emoji
don't fit, the stream misaligns. Fix: pack must work on UTF-8 bytes first, runner
opens via `TextDecoder`. Turkish content is unavoidable → fix before v1 is called done.

## 3. Limits (by design, not bugs)

- The runner is PLAIN text: the algorithm is readable, the content is what's hidden.
- Memory guarantee is best-effort: plaintext exists in memory at execution time.
  Chunked execution (v2) closes this.
- The `debugger` gate is light: stops the curious, not the determined.
- Single static key: recovering one file's stream reveals the method (not the content).

## 4. v2 work list (prioritized)

**Hotfix (before v1 is done):**
1. pack UTF-8 + runner `TextDecoder` (the bug above).

**Features:**
2. Chunked IR (`FS:2`): segments + map, full plaintext never in memory.
3. Integrity signature: runner verifies before running (tampered `.fs` never runs).
4. Per-segment keys: one recovered stream is no longer enough.
5. Real-environment test: mobile Firefox + Violentmonkey (`Function`, gate threshold, speed).
6. Developer mode: readable output skipping stage 2 (for our own debugging).

**Optimizations:**
7. Blob hex→base64 (size ~2x → ~1.37x; needs a format flag).
8. Threshold tuning: crypt length limit by measurement.

**Dead code:**
9. None dead right now (fresh rebuild). Old 0.4.0 line stays in history, fine.

**Other work:**
10. Orbit embedding + export line + `mustContain` interplay (packed `.fs` hides markers →
    the loading side must see the tag and open it first).
11. Docs rewrite: DESIGN/TUTORIAL/CLI/FAQ rewritten for v1 (wipe took them,
    only FORMAT.md exists).
