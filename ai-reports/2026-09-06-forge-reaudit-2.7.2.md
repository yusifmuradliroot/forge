# forge full re-audit — parts, deepest level
Date: 2026-09-06 | forge 2.7.2 (runner v4) | auditor: Muse Spark | v1

Method: every file re-read (post-2.7.x code, not the v2.5.0 snapshot);
every suspicion executed as a probe. Findings marked PROVEN (transcript),
REVIEWED (read-clean), or NOTE (judgment call). Prior audit
(ai-reports/2026-09-06-deep-audit-v2.5.0.md) stays valid except where noted.

---

## PART A — SECURITY VULNERABILITIES

### A1. crypt encrypts template-middle chunks (PROVEN, HIGH — silent corruption)
A template chunk that starts AND ends with a quote
(`` `${a}" quoted text "${b}` `` → middle chunk `" quoted text "`) is a `str`
token the tokenizer cannot distinguish from a real string literal. crypt
encrypts it into `__f("...")` INSIDE the template → renders literal garbage.
Proof: `` const x = `${a}" quoted text "${b}` `` → `` `${a}__f("7a…")${b}` ``.
Fix: track template context while walking toks (a chunk is real-string only
outside backtick spans); skip everything between.

### A2. crypt glue breaks missing-semicolon directives (PROVEN, HIGH)
`"use strict"\nvar s = "<long>"` → `"use strict"var __f=...` (SYNTAX ERROR,
node-verified). The glue only skips `;`/`\n` AFTER the directive, but the stub
lands on the directive's own line. Fix: `glue = ";"` unless `result[cut]`
is already `;` (a duplicate `;;` after a newline is harmless).

### A3. Signature still zero-authenticity (REVIEWED, standing from C2)
Re-verified unchanged: public format + constant keys + FNV ⇒ anyone mints
valid files. No new exposure, but every new consumer must read LIMITS.md first.

### A4. Generator destructured params escape poison (PROVEN narrow, MEDIUM-LOW)
`function* g({a}) {}` — poison never sees the pattern (only `function` +
paren after optional NAME; `*` breaks the walk). Outcome today: missed
minification only (param scan misses too → zero decl sites → untouched).
Corrupts ONLY in the narrow shape `const a = …; function* g({a}){…a…}` called
with an external `{a:…}` (silent wrong value, no crash). Fix: allow `*` in
the function-head walk.

---

## PART B — POSSIBLE BUGS (all probed)

### B1. L6 false-aborts on `__f` inside comments (PROVEN, LOW-MEDIUM)
`// calls __f() at runtime` + any long string → `ValueError`, build refused.
The check regexes raw code instead of identifiers. Fix: scan the mask
(`build_mask` is already imported nowhere in crypt — import it) or token idents.
Safe direction (refusal, not corruption), but blocks legit builds.

### B2. pack emits unusable files for 1–2 byte inputs (PROVEN, LOW)
`pack.run('x')` → manifest claims 3 blobs, 1 blob line exists → runner
refuses. Silent at build (exit 0). Fix: `ValueError` when `len(data) < 3`
(same as the L14 empty abort).

### B3. short generator gap (PROVEN, LOW — minification loss, see A4)
Same root as A4. No invalid output observed; names just stay long.

### B4. nolog `void console.log(x);` survives (PROVEN, trivial)
Statement-position `void` isn't in the starter set. Safe direction (a log
survives = silence gap, not breakage). One-word fix.

### B5. `--passes ""` writes raw JS under an `.fs` name (PROVEN, trivial)
Empty list → no passes → input copied verbatim to `out.fs` (exit 0, no tag).
Runner refuses it downstream, but the artifact lies about its format.
Fix: refuse empty pass list.

### B6. Duplicate crypt aborts LOUDLY (REVIEWED, acceptable)
Second crypt run sees its own `__f(` stub → L6 ValueError. Loud, safe,
correct-ish. Document "passes run once" instead of changing code.

### B7. short `taken` vs GLOBALS (REVIEWED, safe by construction)
`name_gen` yields `[a-z]+`; GLOBALS contains no such short name in the first
5000 (probed). Safe today; add the one-line guard anyway (future-proof).

---

## PART C — STABILITY WEAKNESSES

- C1. No template-boundary awareness anywhere except short's tokenizer
  (crypt A1 is the live wound; audit/nolog inherit safety only via masking).
- C2. nolog `_line_of` is O(n) per strip → O(n·m) on log-heavy files
  (measured: 500 logs = 0.02 s — fine today, note the shape).
- C3. poison nested-brace walk is O(depth·span); fine <100 KB, no guardrail.
- C4. Runner `atob` on huge blobs, NTP jumps vs the 100 ms gate, `o.o`
  duplicates — all fail-closed, all acceptable. Noted, no action.
- C5. `debugger` + silent refusal remains the only blind debugger by design
  (LIMITS §5). Accept.

---

## PART D — MALICIOUS-USE PROTECTION (forge as a tool)

- D1. No telemetry, no network, no dynamic import outside `passes.*` —
  verified by grep (only name-lists match). Nothing to exfiltrate with. Good.
- D2. Primary control is repo privacy (unchanged). LICENSE §3 ("do not
  disrupt/harm") covers misuse thinly; RECOMMEND one explicit line, e.g.
  "no malware, no obfuscation services for third parties" (owner call —
  license change, not code).
- D3. `--passes` traversal confined (`passes.<name>`, dots rejected). Good.
- D4. Passes abort loudly, never write half-output (L6/L14 + CLI catch). Good.

## PART E — CLIENT-SIDE PROTECTION SECURITY

- E1. Unchanged since C2/LIMITS: obscurity of source, never of method.
  Constant per-position XOR keys compound it (one known-plaintext pair cribs
  every file's stream layout — manifest even labels the order).
- E2. `run()` executes with host privileges; a swapped `.fs` is full
  compromise — mitigated ONLY by TLS + pinned URLs + no write access.
  Restated because new consumers keep assuming otherwise.
- E3. Wipe-refs (`c="";t=""`) is theater (caller's string lives till GC).
  Harmless; honest-doc it or drop it (drop = smaller runner; keep = zero risk).

---

## PART F — GLOBAL USABILITY

- F1. No QUICKSTART (install python3/node, first build in 60 s). Biggest
  usability gap for anyone new.
- F2. No `docs/PASSES.md` (per-pass input→output contract future edits must
  keep — the exact knowledge that would have prevented the 2.7.x bug cluster).
- F3. No CI; `selftest.sh` is bash-only (Windows out). Recommend: keep the
  shell script + mirror the gates in `check.py` where cheap (already done
  for sig/docs rules).
- F4. Python/node version floors undocumented (`f-string` ⇒ 3.6+;
  `atob`/`TextDecoder`/spread ⇒ any live node). One line in README.
- F5. `--embed` silently ignores 2nd+ markers (strip deletes the leftover
  comment, so harmless) — warn instead.
- F6. `--yes` without `--audit` is a silent no-op; `--embed-max` message says
  chars, compares bytes. Trivia, one-line fixes.

## PART G — IN-REPO SYNC & HIERARCHY

- G1. STALE (fix with next bump per rule 15/17): `tools/forge.py` docstring
  ("locked v1 pipeline", pre-nolog usage), `AI/WHEREWEARE.md:5` pipeline
  line (no nolog), `AI/CONTEXT.md` "order (v2.6.0)" heading.
- G2. Layout is clean (`src/` libs + `passes/` + `tools/` + `tests/` +
  `docs/` + `ai-reports/`). Single-layout imports hold (no dual dance left).
- G3. `nolog` is NOT in DEFAULT (deliberate: stripping logs changes behavior;
  callers opt in). Keep + document the choice (this line is that document;
  move to PASSES.md when written).
- G4. `scan.py`/`poison.py`/`audit.py` have no direct unit tests; covered only
  via passes. Acceptable (selftest probes the behaviors), note the gap.

## PART H — DEAD CODE / FILES

- H1. `short.py`: `_regex_allowed`, `KEYWORDS_BEFORE_REGEX`, `build_mask`
  imported, zero uses in module → REMOVE (rule 2, zero-dead-code).
- H2. `nolog._mask`: `off` variable written, never read → REMOVE.
- H3. `poison.py`: verify `_check_word_term`-class leftovers (one known
  removed; re-grep at fix time).
- H4. `crypt`: `import re as _re` inside `run()` → move to top (cosmetic).
- H5. No dead files (archive already purged; `__pycache__` untracked+ignored;
  every tests/* file is referenced by selftest except `nolog.js` — wire it
  in or drop it: currently `tests/nolog.js` is built by NOTHING. Recommend
  adding it to selftest (behavior-compare) or deleting.
- H6. `docs/ANALYSIS.md` stub: keep (history pointer), do not expand.

## PART I — REMOVE / OPTIMIZE / ADD

**REMOVE:** H1 imports, H2 variable, E3-wipe theater (optional), stale doc
lines (G1), `tests/nolog.js` if unwired (H5 decision).
**OPTIMIZE:** A1 template-context tracking, A2 unconditional `;` glue,
A4 `*` in function-head walk, B1 mask-based `__f` check, B2/B5 loud aborts,
B4 `void` starter, B7 GLOBALS guard, F5/F6 one-liners.
**ADD:** audit patterns `setTimeout/setInterval`-string, bare `Function(`,
`insertAdjacentHTML` (all three PROVEN missed today:
`setTimeout("do evil",100)` → clean, `Function("return 1")` → clean,
`insertAdjacentHTML` → clean); `docs/PASSES.md`; QUICKSTART; version floors;
LICENSE one-liner (owner call); `tests/nolog.js` wired or deleted.
