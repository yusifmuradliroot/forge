# forge deep audit — every file, every pass, adversarially probed
Date: 2026-09-06 | forge v2.5.0 (runner v3) | auditor: Muse Spark | v1

Method: full read of all 5 passes, runner, CLI, checker, docs, fixtures —
then adversarial probes EXECUTED against each (not just read). Every finding
below carries a proof transcript. Severity = worst realistic impact on shipped `.fs`.

Scope note: forge is a general-purpose JS protector (nothing gartic-specific —
correct, keep it that way). Its trust boundary is: private raw in, signed `.fs`
out, public runner executes. Findings are ordered by severity.

---

## CRITICAL

### C1 — Runner decodes segments separately: silent UTF-8 corruption, valid signature
`src/runner/forgescript.js`, `b()`: each segment is `TextDecoder().decode()`d
INDEPENDENTLY, then joined as strings. Any multibyte char split across a segment
boundary decodes as 2x U+FFFD. The signature covers CIPHERTEXT, so it still
verifies — corruption is invisible to every checker. The v2 battery claim
("Turkish/emoji proven") is wrong for shuffled orders; the minimal fixture only
passed because splits landed on ASCII.

Proof:
```
src: const selam = "merhaba dünya, bu uzun bir Türkçe cümledir"; ...
dec: ... "merhaba dünya, bu uzun bir T��rkçe cümledir" ...
node==python plen: 126 vs 122 (C3 BC became EF BF BD EF BF BD)
manifest o=[1,2,0] (shuffled); identity-order files are unaffected
```

Fix (format-compatible, old files keep working): collect segment bytes,
concat, ONE `TextDecoder().decode()` at the end. Runner v4 + rebuild hosts
(runner is embedded). `.fs` bytes need no change. Add a shuffled multibyte
fixture to the battery (Turkish + emoji, all 6 orders).

### C2 — FS:2 "signature" gives zero authenticity (demonstrated forgery)
The format, key schedule (`0x5A ^ ((e*31+7) % 256)` — CONSTANT across all files
ever forged), shuffle (FNV-seeded, deterministic) and FNV itself are all public
in this repo. FNV is not a MAC. Anyone can mint a fully-valid `.fs` for
ARBITRARY content. Demonstrated:

```
$ pack.run('console.log("PWNED by attacker-crafted fs");') -> evil.fs
runner-accepted-forged-file: true | output: ["PWNED by attacker-crafted fs"]
```

So "tampered .fs never runs" is FALSE against a deliberate attacker; the sig is
integrity-vs-accident only. Real protection today = TLS + pinned URLs + no
write access — never the sig. compounding: per-file keys don't exist, so one
known-plaintext pair cribs every file's stream positions.

Fix options (owner call): (a) document honestly (sig = accident check) and stop
relying on it; (b) HMAC with the key OUTSIDE the repo — breaks the public-runner
model, needs key distribution; (c) per-file salt in manifest (raises cost, still
not auth). Minimum: (a) NOW — docs currently oversell it.

---

## HIGH (silent output corruption, all reproduced)

### H1 — strip.py eats code after regexes with escaped slashes / `/*`
strip is regex-BLIND (unlike short). `var re = /\//; var x = 1;` forges to
`var re = /\` (truncated — downstream SyntaxError at best, dropped statements
at worst). Same for `/\/*/` (block-comment opener inside regex).
Shipped files dodged this by luck (no such regexes), not by safety.

Fix: make strip regex-aware. Structural recommendation (covers H1 + L1 + L2):
extract ONE shared scanner (`scan.py`: strings incl. `${}`, regex incl. classes,
comments) used by strip/short/nolog. Three divergent reimplementations of the
same scan is the root cause of this whole family.

### H2 — short.py renames destructured binding names
`const {beta} = obj` -> `const {b} = obj`: reads property `b`. Silent wrong
behavior. Proof transcript confirmed.
Fix: when a var/let/const declarator contains `{`/`[` before `=`, skip the whole
declaration (conservative; binding-pattern renames are never worth the risk).

### H3 — short.py renames object shorthand `{alpha}` -> `{a}`
Reads property `a`. Same family: method shorthand, getters, class methods with
a colliding declared name. Proof confirmed (`foo({alpha})` -> `foo({a})`).
Fix: brace-depth tracking in the bad-use check (an ident in key/shorthand
position poisons the name). `{[k]: v}` computed keys and `{...s}` spreads are
safe (value semantics) and must stay renamable — the fix must distinguish them.

### H4 — short.py renames BigInt suffix: `123n` -> `123b` (SyntaxError)
The ident scanner accepts a letter immediately after digits. `123...890n`
becomes `123...890b` — forged file fails `node --check`.
Fix: in `tokenize`, if an ident-start char is IMMEDIATELY preceded (no gap) by
a digit, emit as `other`, not `ident`.

---

## MEDIUM

### M1 — crypt STUB prepended before file-top `"use strict"` (semantics change)
`result = STUB + result` unconditionally. A file starting with `"use strict";`
loses strict mode (this-coercion, silent bad assignment, arguments mapping).
Function-level directives (our shipped shape) are unaffected — again luck.
Proof confirmed (`directive-first: False` once a long string triggers the stub).
Fix: append the stub at END (`var` hoists; prefix with `;` against ASI hazards).

### M2 — check.py never verifies the pack signature (shape-only)
It asserts tag + 3 blobs + perm shape + `s` truthy — a sig regression ships
green. We already lived the sibling of this: the inverse-order false-FAIL that
only self-inverse manifests survived. Fix: recompute FNV over manifest order
in the checker (5 lines; use the REAL runner `b()` as oracle in CI instead).

### M3 — docs/ANALYSIS.md stale (logic confusion)
Still v1.0.0: says pack emits `FS:1`, lists FS:2/sig/keys/dev-mode as FUTURE —
all shipped. A reader gets a false model of the tool. Fix: rewrite or stamp
SUPERSEDED pointing at FORMAT.md + CHANGELOG.

### M4 — README stale ("Current: v2", no nolog/host/2.5.0)
Repeat of the 2026-09-05 release-checklist lesson. Fix with the next bump, same
commit (rule already exists — enforce via check.py? e.g. assert VERSION string
appears in README + CHANGELOG).

---

## LOW

- L1: nolog strips `console.*` inside MULTILINE regex when followed by `;`
  (`/ab\nconsole.log(x);\ncd/` corrupted). Needs regex-awareness (see shared-scanner rec).
- L2: nolog `keep-log` honored only as trailing `//`; block/leading markers missed.
- L3: short renames same-named method/getter/class-method (H3 family, rarer).
- L4: `export function f` gets renamed (breaks imports; bundles unaffected — document).
- L5: `eval("x")` / `with` + renamed locals break (inherent to mangling — document).
- L6: pre-existing global `__f` + crypt output collide (assert/rename to `__f2`/uuid-ish).
- L7: `import x from "<long>"` would encrypt the module specifier (bundles have none — document).
- L8: runner API is `this`-dependent (`const {run}=ForgeScript` throws; bind or document).
- L9: runner "wipe refs" (`c="";t=""`) is theater — caller's string lives until GC. Honest-doc.
- L10: runner refuses SILENTLY (we debugged blind for a day because of it). By design —
  but ship a `--dev`-style diagnosing runner? No: keep silent, note the cost.
- L11: forge.py traceback on bad `--passes` names (wrap import), no `--version`,
  embed-max message says chars, compares bytes.
- L12: check.py note-free test (`://`) false-positives on any future URL string.
- L13: no CI — fixtures never auto-run (regression risk; the Turkish claim rotted silently).
- L14: `pack('')` emits a manifest claiming 3 blobs with zero blob lines (refused
  downstream, but should abort loudly at build).
- L15: minification is conservative by design (cross-scope same-name never renamed;
  arrow params never recorded) — ratio cost, not correctness. Fine, keep.

## Explicitly verified SAFE (do not "fix")
- Determinism: double build byte-identical.
- FNV test vector (`bf9cf968`) green.
- Regex-vs-division in short: correct in ALL reachable cases (buf-first + keyword
  list); the `}`-lookbehind asymmetry is unreachable-harmful (buf always carries it).
- Optional chaining `o?.x` accidentally safe (`?.` ends with `.`).
- Ternary/if-else bodies in nolog (placeholder `;` fix holds; torture green).
- Nested-template console in nolog (ternary guard holds).
- `?.`/`,`/`;`/`(`/`{` before regex all correct.
- No compression = no zip-bomb surface (1.4x max).
- `--passes` confined to `passes.*` (no module-escape exec).
- Idempotent pack (FS:2 input returned as-is).
- Minimal Turkish round-trips byte-exact (identity order) — the C1 fix generalizes it.

## Recommended order
1. C1 runner one-shot decode (runner v4; format unchanged; rebuild hosts; add
   shuffled-multibyte battery).
2. C2 honest-docs now; HMAC/salt as a separate owner decision.
3. Shared `scan.py` (kills H1/L1/L2 structurally) + H2/H3/H4 fixes + fixtures.
4. M2 checker verifies sig via real runner; M4 README rule enforced.
5. M1 stub-append; M3 ANALYSIS rewrite; CI (even `python -m pytest`-less shell loop).
