# WHEREWEARE — living state (AI: keep this updated)

## Goal
JS protection layer, general purpose and independent. Pipeline v2:
strip → short → crypt → pack (FS:2). Open-source release possible later.

## Done
- Repo wiped and restarted from zero (old 0.4.0 line in git history).
- Infra rebuilt: README, CHANGELOG, LICENSE, AGENTS.md + AI/.
- v1.0.0 WORKED: strip/short/crypt/pack, runner, FORMAT FS:1 spec, e2e verified.
- v2.0.0 FINAL: FS:2 (segments, per-seg keys, base64, FNV signature), runner v2,
  UTF-8 fix, --dev flag. Bug-hunt battery green (2 bugs found+fixed).
  Residual: devtools-open path + mobile Firefox untested.

## User context
- Device: mobile, Firefox-based. Console: NONE → visual-feedback diagnosis only.

## In progress
- (none — v2.0.0 shipped; consumer integrations live outside this repo)

## Next (later, trigger-based — NOT scheduled)
- v3 chunked execution (never full plaintext in memory; needs scope-aware splitter).
  Triggers: v2 observed cracked, threat level rises, or export line fully stable.

## Next (trigger-based — NOT scheduled)
- v3 chunked execution (never full plaintext in memory; needs scope-aware splitter).
  Triggers: v2 observed cracked, threat level rises, or a consumer funds it.

## Open problems
- (none — rebuild)
