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
strip → short → crypt → pack. Clean first, rename second, encrypt third
(encrypted blobs must not be renamed), pack always last.

## Architecture constraint
A layer OVER JavaScript: output runs anywhere JS runs, no installs, no native builds.
