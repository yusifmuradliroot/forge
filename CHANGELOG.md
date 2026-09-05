# Changelog

## [Unreleased]

## [1.0.0]
- First fully working version: raw JS → `.fs` → forgescript runner → identical behavior
- Passes: strip, short, crypt, pack (ported from proven 0.4.0 line, renamed)
- Runner: `src/runner/forgescript.js` — tag check, light anti-debug gate, wipe-after-run
- Format: `docs/FORMAT.md` (FS:1)
- Verified: 68KB real file, wrong-tag/empty refusal, node runtime identical
