# WHEREWEARE — living state (AI: keep this updated)

## Goal
JS protection layer, general purpose and independent. Pipeline v2:
strip → short → crypt → pack (FS:2). Open-source release possible later.

## Done
- v2.6.0: deep-audit fixes — runner v4 (multibyte), poison (short), scan-shared
  strip/nolog, crypt strict-safe, sig-verifying checker, LIMITS.md, selftest.sh.
- v2.5.0: `nolog` pass (console.* stripped, keep-log survives) for silent public builds.
- v2.4.0: FS:1 REMOVED (runner v3, FS:2-only). FS:1-era runner archived at `archive/fs1-era/`.
- v2.3.0: full pipeline (strip, short, crypt, pack FS:2 signed) + runner v2.
  --dev mode, --embed (guards + bootstrap proof), --host (userscript mode).
  Regex/division tokenizer fix + torture fixture. Bug-hunt battery green.
  Residual: devtools-open path + mobile Firefox untested.
- Consumers: omni voyager (host-built) + omni.fs + plugin .fs files, all verified.

## User context
- Device: mobile, Firefox-based. Console: AVAILABLE for now (past logs received).

## In progress
- (none — v2.3.0 shipped; consumer integrations live outside this repo)

## Next (trigger-based — NOT scheduled)
- v3 chunked execution (never full plaintext in memory; needs scope-aware splitter).
  Triggers: v2 observed cracked, threat level rises, or a consumer funds it.

## Open problems
- (none open)
