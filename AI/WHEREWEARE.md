# WHEREWEARE — living state (AI: keep this updated)

## Goal
Secure programming language + interpreter + security layers. General purpose, not gartic-only.
First client: Gartic.io Omni pipeline (abyss → grimorium). Open-source release possible later —
keep code original and dependency-free so relicensing stays possible.

## Done
- Private repo `forge` created, branch `main`.
- v0.2.0: 4 passes (strip_comments, mangle, string_crypt, ai_confuse), full chain verified on
  real 68KB file (node --check OK, runtime output identical).
- Full docs: DESIGN, TUTORIAL, CLI, FAQ, PASSES catalog. checker PASS (4 passes, 3 fixtures).
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
