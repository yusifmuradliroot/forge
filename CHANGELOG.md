# Changelog

## [Unreleased]

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
