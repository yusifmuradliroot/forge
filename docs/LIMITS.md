# forge LIMITS — what this tool does NOT do (read before relying on it)

## 1. The signature is accident-check, not authenticity
FNV-1a is not a MAC, and the format + key schedule + shuffle are public in
this repo. Anyone can mint a fully-valid `.fs` for arbitrary content
(demonstrated in `ai-reports/2026-09-06-deep-audit-v2.5.0.md`). The trust chain
is: private raw + TLS transport + pinned URLs + no write access. The sig only
catches truncation, bad manually-edited files, and our own pack regressions.

## 2. The runner is readable; the content is what's hidden
Obscurity of source, not of method. A determined reader with the `.fs` and
this repo recovers everything. Budget accordingly (this stops the curious and
free-AI readers, not a funded analyst).

## 3. Plaintext exists in memory at execution time
Chunked execution (never-full-plaintext) needs a scope-aware splitter — a real
compiler step. FS:2 segments are transport-level. Not oversold, not scheduled.

## 4. Mangling limits (short is conservative; these never rename correctly)
- `eval("name")` / `with (obj)` + renamed locals: rename breaks them. Keep
  eval/with out of forged sources.
- `export function f`: renamed (breaks importers). Forge targets bundles.
- `import x from "..."`: a long specifier would be encrypted (bundles: none).
- Bare class fields (`class A { x = 1 }`): field names are not renamed
  (conservative), but external `.x` access patterns are out of scope.
- Cross-file references: each file is renamed independently. Shared globals
  must go through the GLOBALS list or property access.

## 5. `debugger` gate + silent refusal
The runner returns null (no error) when tampered-with or debugger-paused.
Silence is the point (anti-tamper), but it makes OUR debugging blind too —
diagnose via the battery + decrypted `--dev` output, never by staring at null.

## 6. Untested fronts (residual risk)
Devtools-open path, mobile Firefox + Violentmonkey at scale. The battery runs
node only. Real-room verification stays mandatory per release.
