# CONTEXT — infrastructure map (forge, private)

## Role
JS protection layer. Raw JS in, working-but-hard-to-read JS out.
Independent tool — answers to no other repo. Consumers pin a VERSION and adapt.

## Layout
```
src/scan.py + src/poison.py → shared scanner + never-rename names
src/passes/<name>.py  → nolog, strip, short, crypt, pack — each run(code: str) -> str
tools/forge.py        → CLI: .fs chain, --dev, --embed (guards), --host (userscript)
tests/                → fixtures per pass + real-file verification
docs/                 → FORMAT.md (.fs spec), ANALYSIS.md (deep review)
VERSION               → single version for the whole tool
```

## Pipeline order (v2.8.0)
nolog → strip → short → crypt → pack. Logs first (needs comments for keep-log),
clean second, rename third, encrypt fourth (blobs must not be renamed), pack last.
Host mode (--host): header preserved, embed first, pack rejected.

## Embedding pattern (for consumers)
Host loads `src/runner/forgescript.js` once, feeds it `.fs` payloads via
`ForgeScript.run(text)`. Runner core is DOM-free: browser, userscript manager,
node — anywhere JS runs. Runner refuses unknown tags and tampered payloads.
Runner and language version together: runner vX runs `.fs` vY (see FORMAT.md).

## Architecture constraint
A layer OVER JavaScript: output runs anywhere JS runs, no installs, no native builds.

## Terms (user-defined, do not rename)
- **forge** — Python app: cleans raw JS and translates it to `.fs`.
- **forgescript** — the language AND its JS-written runner. Runner traits: plain UNENCRYPTED JS
  (only stage-1 passes: stripped, short names — by forge itself), small, minimal, fast, stable.
  Runs ONLY `.fs` code. Light anti-debug embedded (e.g. halt when devtools opens).
  Rationale: the runner hides nothing itself; secrecy lives in the `.fs` payloads it reads.
- **forgescript (language)** — JS-based, every JS element replaced with a hard-to-read but
  lightweight variant. Purpose: make raw JS hard to read.
- **.fs** — file type the runner executes and understands.

## Payload contract
- `.fs` is PURE DATA (never carries its own loader): tag line + encrypted payload.
- Loaders holding markers inside blobs must unpack-first or tag-check before scanning.
- Format: FS:2 only since 2.4.0 (segments, keys, signature). FS:1 removed (era archive since removed).
  Reserved: FS:3 chunked execution (needs a scope-aware splitter).
