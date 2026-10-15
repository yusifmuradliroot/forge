# forge LIMITS — what this tool does NOT do (read before relying on it)

## 1. The signature is accident-check, not authenticity (default)
FNV-1a is not a MAC, and the format + key schedule + shuffle are public in
this repo. Anyone can mint a fully-valid `.fs` for arbitrary content.
The trust chain is: private raw + TLS transport + pinned URLs + no write
access. The sig only catches truncation, bad manually-edited files, and
our own pack regressions.

**Hardened option**: set `FORGE_SIGN_KEY` to enable HMAC-SHA256 signatures
(`alg: "hmac"` in the manifest). The runner verifies HMAC before decoding.
Without the key, forgery is computationally infeasible.

## 2. The runner is readable; the content is what's hidden
Obscurity of source, not of method. A determined reader with the `.fs` and
this repo recovers everything. Budget accordingly (this stops the curious and
free-AI readers, not a funded analyst).

## 3. Plaintext exists in memory at execution time
Chunked execution (never-full-plaintext) needs a scope-aware splitter — a real
compiler step. FS:2 segments are transport-level. Not oversold, not scheduled.

## 4. Mangling limits (short is conservative; these never rename correctly)
- `eval("name")` / `with (obj)` + renamed locals: rename breaks them. Keep
  eval/with out of forged sources. (`--audit` flags both; FORGE_SCOPE=1
  additionally refuses any function whose body holds eval/with/arguments/
  nested functions — but the base rule stands: audit first.)
- `export` bindings keep their names verbatim (importers must match).
  Forge targets bundles; `--audit` flags every `export` so it is reviewed.
- `import x from "..."`: the specifier is now protected by poison.py and
  will NOT be renamed or encrypted. However, bundling first is still
  recommended for cross-file safety.
- Bare class fields (`class A { x = 1 }`): field names are not renamed
  (conservative), but external `.x` access patterns are out of scope.
- Cross-file references: each file is renamed independently. Shared globals
  must go through the GLOBALS list or property access.

## 5. `--strict` mode refuses risky constructs
When `--strict` is passed, forge refuses to build if any of the following
are present: `console.*`, `debugger`, `eval(`, `new Function()`,
`innerHTML`/`outerHTML`/`insertAdjacentHTML`, `document.write`, `export`,
`with(`. Use `--yes` to override (not recommended for production).

## 6. `debugger` gate + silent refusal
The runner returns null (no error) when tampered-with or debugger-paused.
Silence is the point (anti-tamper), but it makes OUR debugging blind too —
diagnose via the battery + decrypted `--dev` output, never by staring at null.
Set `FORGE_DEBUG=1` to see rejection reasons during development.

## 7. Untested fronts (residual risk)
Devtools-open path, mobile Firefox + Violentmonkey at scale. The battery runs
node only. Real-room verification stays mandatory per release.

## 8. HMAC key management
If you use `FORGE_SIGN_KEY`, treat the key like a secret: never commit it,
rotate it periodically, and provision it only to trusted build/runner
environments. Lost keys mean old `.fs` files can no longer be verified
by HMAC-enabled runners.
