# WHEREWEARE — living state (AI: keep this updated)

## Goal
JS protection layer (general purpose, not gartic-only). Pipeline v1:
strip → short → crypt → pack. First client: Omni export (abyss → grimorium).
Open-source release possible later.

## Done
- Repo wiped and restarted from zero (old 0.4.0 line in git history).
- Infra rebuilt: README, CHANGELOG, LICENSE, AGENTS.md + AI/.
- v1.0.0 WORKS: strip/short/crypt/pack ported from proven code, runner written,
  FORMAT.md spec, e2e verified (raw → .fs → runner → identical), 68KB real file OK.

## User context
- Device: mobile, Firefox-based. Console: NONE → visual-feedback diagnosis only.

## In progress
- (next: wire into abyss → grimorium export; runner embedding in orbit)

## Next
- v1 (LOCKED scope): `strip` → `short` → `crypt`. This alone beats most attackers.
- Then forgescript track in locked build order: format sketch → runner → finalize format → translator.
- v2 (later): `pack` + wire into abyss → grimorium export

## Open problems
- (none — rebuild)
