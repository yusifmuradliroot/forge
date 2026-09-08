# Usability — forge as a developer tool (would people use it?)
Date: 2026-09-06 | forge 2.8.0 | v1 (heuristic + virtual walkthrough)

Scope: forge ONLY (the protector tool: CLI, passes, runner, docs).
Audience: a JS developer protecting a userscript/bot (today: exactly 1 user).

## Verdict
Usable by its author, hostile to a newcomer. Three gates: no guided first
run, error messages assume internals knowledge, Windows/CI paths absent.

## 1. First run (virtual walkthrough)
1. Clone → README → QUICKSTART exists (new, good): python3/node floors stated.
2. `bash tests/selftest.sh` → GREEN in seconds. Excellent first signal.
3. `forge.py in.js out.fs` → works, prints per-pass char counts. Good feedback.
4. `--audit` on first real file → risk list + prompt. Genuinely useful moment.
Friction: MEDIUM-LOW. Missing: a 5-line example input/output pair in QUICKSTART
(show, don't tell), expected timings ("<1 s under 100 KB").

## 2. Daily use (single consumer today)
- Deterministic builds (byte-identical) → diffable, trustworthy. Excellent.
- `--dev` readable output for debugging transforms. Good.
- `--embed/--host` + guards make host shipping one command. Good.
- `--audit/--yes` fits manual release flow. Good.
- Failure UX: loud aborts with reasons (L6/L14/unknown pass), no half-outputs.
  Good. Gap: `--passes ""` writes raw JS under `.fs` name silently (see re-audit
  B5 — fix queued, not yet implemented).

## 3. Error messages (do they teach?)
- Pass crash → `pass 'x' failed: <err>, aborting (no output written)`. Good.
- Unknown pass → points at `src/passes/`. Good.
- L6/__f, empty/tiny input → specific. Good.
- check.py FAIL lines name the rule. Good.
- Missing: "what to do next" hints (e.g. "rename __f in <file>:<line>").
  Cheap, high value for strangers.

## 4. Trust & adoption blockers (would STRANGERS use it?)
- No: single consumer, private repo, no license for reuse clarity (custom
  source-available, fine for us, unclear for others), no CI badge/proof,
  Windows untested, no changelog-per-pass mapping for upgrades.
- The tool is genuinely good at its job (fast, deterministic, verified);
  nothing structural blocks wider use except evidence + packaging.

## 5. Real-world risks (what breaks first in other hands?)
1. Non-ASCII inputs past the battery (only TR/emoji/CJK covered).
2. Exotic-but-valid JS (generators covered now; decorators, `using`, import
   attributes NOT covered — tokenizer treats `decorator` lines as idents;
   output stays valid but unminified there; unprobed).
3. 500 KB+ inputs (linear to 1 MB measured; beyond unmeasured).
4. Users duplicating passes (`crypt,crypt` aborts LOUD — safe but surprising;
   document "run once").

## Priority fixes (in order)
1. B5 empty-pass-list refusal + `--passes ""` guard (silent lie today).
2. QUICKSTART example pair + timings.
3. check.py/selftest on Windows path (or document bash-only).
4. Decorator/import-attribute probes in battery.
5. CI (even a 10-line workflow running selftest) — the day a second human
   touches this, not before.
