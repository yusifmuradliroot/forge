# WHEREWEARE — living state (AI: keep this updated)

## Goal
JS protection layer (general purpose, not gartic-only). Pipeline v1:
strip → short → crypt → pack. First client: Omni export (abyss → grimorium).
Open-source release possible later.

## Done
- Repo wiped and restarted from zero (old 0.4.0 line in git history).
- Infra rebuilt: README, VERSION `0.1.0`, CHANGELOG, LICENSE, AGENTS.md + AI/.

## User context
- Device: mobile, Firefox-based. Console: NONE → visual-feedback diagnosis only.

## In progress
- (next: forge core passes, one by one with approval)

## Next
- `strip` pass (comments/notes removal, string-aware)
- `short` pass (minimal renames, single-declaration locals)
- `crypt` pass (string encryption, `__*`/directive/key safe)
- `pack` pass (whole-file pack + mini loader + tag)
- Wire into abyss → grimorium export

## Open problems
- (none — rebuild)
