# CONTEXT — infrastructure map (forge, private)

## Role
Secure programming language + interpreter + security layers. NOT gartic-only — general purpose.
Omni pipeline is just the first client. Open-source release is possible later.

## Open-source hygiene (mandatory from day one)
Keep the relicense option open: zero copied code, zero dependencies, original
implementation everywhere. Today's custom license must never become a blocker.

## Layout
```
src/passes/<name>.py  → one transform each: run(code: str) -> str
tools/forge.py        → CLI: forge.py in.js out.js --passes a,b,c
tests/                → fixtures (input samples; output eyeballed or diffed)
docs/                 → design + pass catalog (pending)
VERSION               → single version for the whole tool
```

## Pass contract
- Pure string transform. Never crash on valid JS. Never change runtime behavior.
- String/regex-aware where needed (see `strip_comments` as reference implementation).

## Roadmap
Phase A — pass pipeline (0.3.0):
1. mangle identifiers — vs casual readers ✅
2. string encryption — vs free-AI readers ✅
3. proprietary pack format + mini loader — vs paid-AI + tools (spec: `docs/IR.md`, pending)
Phase B — secure language layer (later):
4. custom language running as a layer over JS — code ships in our form, our runtime executes it
5. security layers on top (verify, integrity checks, anti-tamper at runtime)

Minimalism (hard): output stays small — strip notes, short renames, zero decoys/fake content.
(`ai_confuse` was removed in 0.3.0 for violating this.)

## Architecture constraint
A layer OVER JavaScript, never beside it: compiles to JS and/or interprets via a
JS-hosted runtime. Runs anywhere JS runs (browser, Violentmonkey included).
No native builds, no new runtime to install — JS is the only foundation.
