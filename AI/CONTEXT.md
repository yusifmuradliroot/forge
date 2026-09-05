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

## Architecture constraint
A layer OVER JavaScript: output runs anywhere JS runs, no installs, no native builds.

## Distribution design (ForgeScript)
- Plugins ship as `.fs` files (written in ForgeScript) on GitHub.
- The ForgeScript runner is EMBEDDED in orbit: voyager → orbit → embedded ForgeScript.
- Orbit fetches `.fs`, routes to the runner, runner executes. No plaintext plugin code on disk.
- Runner and `.fs` language MUST be versioned together (compat matrix: runner vX runs `.fs` vY).
  Language changes require runner + files in lockstep — never bump one side alone.
