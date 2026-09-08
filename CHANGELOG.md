# Changelog

## [Unreleased]

## [2.8.0] — re-audit fixes (ai-reports/2026-09-06-forge-reaudit-2.7.2.md)
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

## [2.6.0] — deep-audit fixes (see ai-reports/2026-09-06-deep-audit-v2.5.0.md)
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
- Voyager gate already FS:2-only; rebuild hosts to carry runner v3

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
