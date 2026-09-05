# WHEREWEARE — living state (AI: keep this updated)

## Goal
General-purpose mini compiler: JS in → protection/build passes → JS out.
First client: Gartic.io Omni pipeline (abyss → grimorium). Must stay usable beyond it.

## Done
- Private repo `forge` created, branch `main`.
- Skeleton: `src/passes/`, `tools/forge.py` CLI, `tests/`, `docs/` (pending), README, VERSION `0.1.0`.
- First pass works: `strip_comments` (string-aware, fixture-verified).
- AI infra: AGENTS.md + AI/{RULES,WHEREWEARE,CONTEXT,LEARNINGS}.
- Infra: topics, CHANGELOG, docs/PASSES.md, tools/check.py (PASS).

## User context
- Device: mobile, Firefox-based. Console: NONE → visual-feedback diagnosis only.

## In progress
- (next AI: fill here)

## Next
- Pass roadmap: mangle identifiers → string encryption → AI-confusion layer → custom transform.
- `docs/` design + pass catalog.
- Wire into abyss → grimorium export when core code exists.

## Open problems
- (none yet)
