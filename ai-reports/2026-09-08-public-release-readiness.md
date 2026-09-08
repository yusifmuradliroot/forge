# forge Public Release Readiness Report
**Date:** 2026-09-08 | **Version:** 2.11.1 | **Status: NOT READY**

---

## Executive Summary

forge works. 17/17 selftest green, all 9 passes functional, runner v5 proven,
CI passes on Linux + Windows. But the **packaging is half-built** — the tool
works, the distribution doesn't. A stranger cloning this repo cannot figure out
how to use it without hand-holding.

---

## BLOCKERS (must fix before any public share)

### 1. LICENSE is incompatible with public release
**File:** `LICENSE` (all 27 lines)

Current license says:
- "NO PUBLIC USE"
- "NO PUBLIC DISTRIBUTION"
- "TAKEDOWN ON DEMAND"
- "Additional terms may be added at any time"

This is a private/source-available license. If the goal is public use,
replace with MIT, Apache 2.0, or ISC. If source-available is intended,
keep it but remove the contradictions ("no public use" + "distribution
allowed" = confusion).

### 2. Internal files must not ship
**Files:** `AGENTS.md`, `AI/` (4 files), `ai-reports/` (9 files)

These contain:
- Private consumer names (omni, voyager, abyss, grimorium)
- Turkish-language communication instructions for AI
- Internal development state and strategy
- Detailed vulnerability analysis with internal auditor references
- ELO scoring and roadmap

**Action:** Remove entirely, or move to `.forge-internal/` and add to
`.gitignore`. If `LIMITS.md` references `ai-reports/`, update the
reference.

### 3. No installation path
There is no `setup.py`, `pyproject.toml`, or any way to install forge
as a command. Users must know to run `python3 tools/forge.py` from
the repo root. This is fine for internal use, hostile for public.

**Options:**
- A) `pyproject.toml` + `pip install -e .` → `forge` command available
- B) Wrapper script at repo root: `./forge` that calls `python3 tools/forge.py`
- C) Both

---

## HIGH PRIORITY (stale/wrong content)

### 4. README says "runner v4" — it's v5
**File:** `README.md:4`

Actual runner code: `var ForgeScript={version:5,...`
README claims: `runner v4`

### 5. docs/FORMAT.md says "Runner flow (v4)"
**File:** `docs/FORMAT.md:21,23`

Same issue. Runner is v5 since v2.9.0.

### 6. No real tutorial or examples
README has terminal commands but no "here's what happens when you run this"
 walkthrough. A new user sees:
```bash
python3 tools/forge.py in.js out.fs
```
But doesn't know what `in.js` should contain, what `out.fs` looks like,
or how to run the output.

**Needs:** A 5-minute quickstart with a minimal JS file, the forge
command, the output, and running it with the runner.

---

## MEDIUM PRIORITY (cleanup)

### 7. selftest.sh leaves temp files
Creates `/tmp/st_*` files but never cleans up. Minor, but sloppy.

### 8. No CI badge in README
CI exists (`.github/workflows/selftest.yml`) but no badge in README.
Signals "this project isn't serious" to visitors.

### 9. No CONTRIBUTING.md
No guide for external contributors. If the project is public, people
will open issues and PRs without knowing the rules.

### 10. Redundant imports in simp.py
`import re` appears inside `run()` (line 51) and `_fold_once()` (line 74)
in addition to module level. Works but messy.

### 11. check.py has no --help
Running `python3 tools/check.py --help` triggers the actual check
instead of showing help. By design, but confusing.

---

## LOW PRIORITY (polish)

### 12. No Python unit tests
All tests are integration (shell + node). No pytest/unittest. For a
public tool, unit tests help contributors understand expected behavior.

### 13. No dedicated num.py or audit.py test fixtures
Tested through the chain only, not in isolation.

### 14. CI pins Python 3.13
README says 3.8+. Not contradictory (CI tests latest, README states
minimum), but could confuse. Add a note: "CI tests on 3.13; 3.8+ is
the minimum."

---

## What's Already Good

| Area | Status |
|---|---|
| Core functionality | All 9 passes work, runner v5 proven |
| Selftest | 17/17 GREEN, covers all passes + edge cases |
| CI | Linux + Windows, runs on push/PR |
| CLI help | Complete, all flags documented |
| docs/FORMAT.md | Accurate FS:2 spec (except runner version label) |
| docs/LIMITS.md | Honest, well-written trust model |
| docs/PASSES.md | Accurate pass documentation |
| No hardcoded paths | All relative, cross-platform safe |
| Python 3.8+ claim | Accurate (only f-strings used) |
| Zero dependencies | By design, no bloat |
| License text | Clear (if private intent is chosen) |

---

## Recommended Release Plan

### Phase 1: Clean (1-2 hours)
1. Replace LICENSE with MIT or ISC
2. Remove `AGENTS.md`, `AI/`, `ai-reports/` from repo
3. Fix runner version in README + FORMAT.md
4. Add `pyproject.toml` for `pip install -e .`
5. Clean selftest.sh temp files
6. Add CI badge to README
7. Write a 5-minute QUICKSTART with minimal example

### Phase 2: Polish (optional)
8. Add CONTRIBUTING.md
9. Fix simp.py redundant imports
10. Add --help to check.py
11. Add pytest unit tests for individual passes

### Phase 3: Publish
12. Tag v2.11.1 on GitHub
13. Write a release post (what it does, why it's different, 3 examples)

---

## Verdict

**forge is a working tool with bad packaging.** The code is solid, the
documentation exists but is stale and incomplete, and the distribution
model (clone + python3 tools/forge.py) is hostile to new users. Phase 1
above takes ~2 hours and makes it genuinely usable by strangers.
