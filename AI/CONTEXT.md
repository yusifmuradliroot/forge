# CONTEXT — infrastructure map (forge, private)

## Role
JS protection layer. Raw JS in, working-but-hard-to-read JS out.
First client: abyss → grimorium export. Usable beyond it.

## Layout
```
src/passes/<name>.py  → strip, short, crypt, pack — each run(code: str) -> str
tools/forge.py        → CLI: forge.py in.js out.js --passes strip,short,crypt,pack
tests/                → fixtures per pass + real-file verification
docs/                 → design docs (pending)
VERSION               → single version for the whole tool
```

## Pipeline order
v1: strip → short → crypt. Clean first, rename second, encrypt third
(encrypted blobs must not be renamed). `pack` deferred to v2.

## Build order (locked)
1. `.fs` format sketch (skeleton target for the runner — half page, not full spec)
2. forgescript runner (minimal, fast, secure; light anti-debug embedded;
   environment-agnostic core, pluggable host API for browser/Violentmonkey/node)
3. Finalize `.fs` format against the runner
4. forge translator (raw JS → `.fs`)
Runner core MUST stay DOM-free. Full-tamper anti-debug is out (cat-and-mouse).

## Architecture constraint
A layer OVER JavaScript: output runs anywhere JS runs, no installs, no native builds.

## Terms (user-defined, do not rename)
- **forge** — Python app: cleans raw JS and translates it to `.fs`.
- **forgescript** — the language AND its JS-written runner. Runner traits: plain JS, no notes,
  encrypted variables + encrypted data, small, minimal, secure. Runs ONLY `.fs` code.
- **forgescript (language)** — JS-based, every JS element replaced with a hard-to-read but
  lightweight variant. Purpose: make raw JS hard to read.
- **.fs** — file type the runner executes and understands.

## Distribution design
- Plugins ship as `.fs` files on GitHub.
- The forgescript runner is EMBEDDED in orbit: voyager → orbit → embedded runner.
- Orbit fetches `.fs`, orders the runner to execute it. ALL execution logic lives in the
  runner — `.fs` is PURE DATA (encrypted payload + tag), never carries its own loader.
  (An in-file mini loader is rejected: duplicated per file, harder to update, pointless
  when the runner is already there.)
- Runner and language MUST be versioned together (compat matrix: runner vX runs `.fs` vY).
  Language changes require runner + files in lockstep — never bump one side alone.
