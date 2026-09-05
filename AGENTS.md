# AGENTS.md — AI entry point

You are working in **forge** (PRIVATE mini compiler toolkit, branch `main`).
General-purpose JS build/protect pipeline: input → passes → output.

## Mandatory at session start
Read these files IN ORDER before doing anything:
1. `AI/WHEREWEARE.md` — where we left off, current goal, next steps
2. `AI/RULES.md` — hard rules, obey without exception
3. `AI/CONTEXT.md` — how the infrastructure fits together
4. `AI/LEARNINGS.md` — past decisions, mistakes, repo-specific knowledge

## Mandatory during work
- Update `AI/WHEREWEARE.md` CONTINUOUSLY as you work — after every agreed step, BEFORE
  committing/pushing. If this session died right now, the next AI must continue from files alone.
- Append to `AI/LEARNINGS.md`: what you did, WHY, mistakes, lessons. Write for the NEXT AI.
  Full AI annotation allowed here (private repo) — in code too.
- Communicate with the user in **Turkish**, in short bite-sized steps. One decision at a time.

## Key facts
- Toolchain runs on the dev machine (python3). EMITTED JS must run on Firefox + Violentmonkey.
- Passes are independent transforms in `src/passes/` with signature `run(code: str) -> str`.
- Bump `VERSION` on every behavior change.
