# Changelog

## [Unreleased]
- License: MIT -> FORGE CUSTOM LICENSE (inspect, customize and use freely,
  with mandatory attribution; the attributed part must be removed on the
  author's request). `check.py` enforces the new license markers.
- `selftest.sh`: portable scratch dir (`.selftest-tmp/` under the repo,
  cleaned on exit) instead of hardcoded `/tmp/st_*`. Windows-native
  python/node cannot resolve MSYS `/tmp` paths, so the battery never
  passed on `windows-latest` (ubuntu was green). No build output change.

## [2.12.0] — public release (behavior fixes + open-source packaging)
- License: custom source-available -> MIT. Internal files removed from the
  repo (`AGENTS.md`, `AI/`, `ai-reports/`); `.gitattributes` forces LF
  (Windows CRLF broke the FS:2 tag); `pyproject.toml` metadata (same version).
- `nolog`: `void console.*` is removed as a whole (was `void ;` SyntaxError).
- `crypt`/`uni`: live `${}` strings are now encrypted/escaped; template TEXT
  middles between `}` and `${` stay verbatim (was: everything skipped).
- `short`/`poison`: `export` bindings keep their names (`export function f`,
  `export const x`, `export {a}`); importer contract preserved. File-start
  keyword boundary fixed (`"" in "_$"` always-true guard).
- `forge.py`: CRLF inputs normalized to LF; output always LF (Windows builds
  byte-identical to Linux). `simp.py`: redundant inner import removed.
- `audit`: also reports `export` and `with` (rename-relevant, review first).
- Tests: `export.js`, `tpl_inner.js` fixtures + export/tpl-runtime/CRLF probes;
  `nolog.js` gains the void case. Battery is 21 probes, all green.
- Docs: `INSTALL.md`, `USAGE.md`, `FAQ.md`, `SUPPORT.md`, `SECURITY.md`;
  README/LIMITS/FORMAT/PASSES updated (2.12.0, no internal references).
- `check.py`: enforces MIT license, no internal dirs, `.gitattributes`,
  pyproject version ride, and regression vectors (void/template/export).

## [2.11.2] — public-ready packaging (no behavior change to builds)
- `./forge` command wrapper (repo root; same as `python3 tools/forge.py`).
- `examples/hello.js` + 5-minute QUICKSTART (build → run → dev → guards).
- `CONTRIBUTING.md` (pass contract, battery-green rule).
- `check.py --help` prints usage instead of running the suite.
- `selftest.sh` cleans its `/tmp/st_*` files on exit.
- `simp.py`: `import re` moved to module top (identical output).
- Docs: runner v5 (was v4), full pass list, CI badge.

## [2.11.1] — reserved strings
- `FORGE_KEEP`: comma-separated exact values uni/crypt never rewrite
  (j-obfuscator `reservedStrings` precedent). Unset by default: default
  builds byte-identical to 2.11.0. Selftest KEEP probe.

## [2.11.0] "golden gate era" — safe-max batch 1
- New `flow` pass (F1): comma-join, negation-flip, while-true -> for(;;).
  Text-only, zero runtime cost. Chain: num -> flow -> simp.
- `crypt` string table (S1): ONE shuffled hex table + index calls instead
  of inline decoders. Seeded stub/table names, chunk length, hex case (S2).
- `short` fixes + N1: named/generator function params are renamed at last
  (the scanner silently skipped them — found via N1 work); FORGE_SCOPE=1
  enables the shadowed-param prototype (flagged, experimental).
- CLI `--gate MS`: bake a stricter runner anti-debug threshold into
  --embed builds (default 100ms untouched; runner source unchanged).
- `short` guard checks pre-grouped by name (O(occurrences), was O(file)
  per candidate): 230KB adversarial input 15s -> 0.35s, same output.
- CI runs on ubuntu + windows (bash). Selftest: flow/scope/gate probes.

## [2.10.0] — string + determinism round
- `crypt` per-build key: XOR base derives from FORGE_SEED (default stays
  historic 0x5A, diffable; stub carries its own key literal, old files run).
- `short` seed-shuffled assignment order under FORGE_SEED (default sorted).
- New `uni` pass: short ASCII strings -> \xNN escapes (same skip-set as
  crypt, disjoint by length). DEFAULT gains uni (simp -> uni -> crypt).
- `src/seed.py`: single variance source; `scan.py` gains shared sig_text +
  template_inner_spans (crypt + uni import ONE impl).
- CI: GitHub workflow runs check + runner battery + selftest on push.
- Selftest: uni fixture, seed determinism + seeded e2e, error-path probes.

## [2.9.0] — crypto + simplify round
- Per-file salt (`"k"` in manifest): XOR schedule + shuffle derive from it;
  default salt = fnv(input) (diffable builds stay), FORGE_SEED=N overrides.
  Segment rotation on disk. Runner v5 reads both, legacy files keep working.
- `num`: decimal ints -> hex (token-based; floats/exponents/BigInt/dotted safe).
- `num`: decimal ints -> hex (token-based; floats/exponents/BigInt/dotted safe).
- `simp`: true->!0/false->!1, safe-int folding, string concat, literal dead
  branches (char-exact spans; else-if chains + if/while-named methods kept).
- DEFAULT is now nolog,strip,short,num,simp,crypt,pack.

## [2.8.0] — re-audit fixes
- crypt token-based: template-middle quotes no longer encrypted (was silent
  corruption); stub after directive prologue even without semicolon; __f
  collision check ignores comments/strings.
- poison: generator `function*` params covered.
- pack refuses <3-byte inputs (were unusable-but-valid-looking files).
- nolog drops `void console.*`; dead `off` var removed.
- short: dead imports out; name generator also skips GLOBALS.
- forge.py: fresh docstring, multi-marker warn, clean pass errors, --version.
- audit: timer-string, bare Function(, insertAdjacentHTML patterns.
- docs: PASSES.md (contracts), QUICKSTART.md, floors. selftest wires nolog.

## [2.7.2] — crypt was regex-blind (silent corruption)
- Token-based rewrite: only real string tokens encrypted. A regex like
  /42\["(10|34)",.../ was shredded (quotes looked like string bounds),
  killing ws_core outgoing-sid recovery in the shipped 2.9 build.
- fixtures: tests/crypt_regex.js + selftest gate.

## [2.7.1] — the exec-killer fix
- short GLOBALS += ForgeScript: the embedded runner kept being renamed
  (`var n`), while separately-forged files call it by global name. Every .fs
  plugin load since the .fs era failed on this. Regression test in selftest.

## [2.7.0]
- `--audit` gate: reports risky constructs (console/debugger/eval/sinks) in raw
  source with line numbers, builds only on approval (`--yes` to skip prompt).
  keep-log lines shown as KEPT. Catches what eyes miss before it ships.

## [2.6.0] — deep-audit fixes
- CRITICAL runner v4: concat-then-decode (per-segment TextDecoder corrupted
  split multibyte chars, invisibly). Multibyte battery (all 6 orders).
- HIGH short: never rename destructured/shorthand/method/BigInt-suffix names
  (src/poison.py). Regression probes in selftest.
- HIGH strip: regex-aware via shared src/scan.py (escaped-slash truncation).
- nolog rebuilt on scan tokens (comment/regex/template-correct).
- MEDIUM crypt: stub after directive prologue (strict kept); __f collision aborts.
- MEDIUM check.py verifies the pack signature (was shape-only).
- MEDIUM docs: LIMITS.md (honest trust model), ANALYSIS stubbed, README current.
- check.py enforces docs-ride-with-bump; forge.py --version, clean pass errors.
- tests/selftest.sh: one-command battery (check + runner + e2e + probes).

## [2.5.0]
- `nolog` pass: strips console.* statements (keep-log lines survive)

## [2.4.0]
- FS:1 support REMOVED: runner v3 refuses unsigned legacy payloads (era archive since removed)
- Hosts are FS:2-only since runner v3; rebuild hosts to carry runner v3

## [2.3.0]
- `--host` mode: userscript hosts (header preserved, pack rejected, single command)

## [2.2.0]
- `--embed` guards: size cap + must-contain check (fail loudly)
- Bootstrap proof: embedded (renamed) runner executes .fs identically to original (42=42)

## [2.1.0]
- `--embed FILE`: inline JS at `/*__FORGE_RUNNER__*/` before passes (host stays installable .js)

## [2.0.1]
- short: regex detection consults pending buffer (fixes `/x/g` flag eaten after `(`)
- short: regex flags limited to known set (dgimsuvy)
- tests/regex.js torture fixture

## [2.0.0]
- FS:2: 3 shuffled segments, per-segment keys, base64, FNV-1a integrity signature
- Runner v2: FS:1+FS:2, verify-before-decrypt, bounds checks, wipe-after-run
- UTF-8 throughout (TextDecoder) — Turkish/emoji content proven working
- CLI `--dev` flag (skip pack, readable output for debugging)
- Bug-hunt battery: tamper/manifest/truncate refused, deterministic builds,
  adversarial probes identical, 68KB real file byte-exact
- Known residual: devtools-open path + mobile Firefox untested (no device here)
- First fully working version: raw JS → `.fs` → forgescript runner → identical behavior
- Passes: strip, short, crypt, pack (ported from proven 0.4.0 line, renamed)
- Runner: `src/runner/forgescript.js` — tag check, light anti-debug gate, wipe-after-run
- Format: `docs/FORMAT.md` (FS:1)
- Verified: 68KB real file, wrong-tag/empty refusal, node runtime identical
