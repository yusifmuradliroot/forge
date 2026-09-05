# WHEREWEARE — living state (AI: keep this updated)

## Goal
JS protection layer (general purpose, not gartic-only). Pipeline v1:
strip → short → crypt → pack. First client: Omni export (abyss → grimorium).
Open-source release possible later.

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
- (next: wire into abyss → grimorium export; runner embedding in voyager)

## Next (later, trigger-based — NOT scheduled)
- v3 chunked execution (never full plaintext in memory; needs scope-aware splitter).
  Triggers: v2 observed cracked, threat level rises, or export line fully stable.

## Next
- v1 (LOCKED scope): `strip` → `short` → `crypt`. This alone beats most attackers.
- Then forgescript track in locked build order: format sketch → runner → finalize format → translator.
- v2 (later): `pack` + wire into abyss → grimorium export

## Open problems
- (none — rebuild)
