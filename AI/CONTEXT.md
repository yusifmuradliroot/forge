# CONTEXT — infrastructure map (forge, private)

## Role
Standalone mini compiler. No dependency on game repos; Omni pipeline is just the first client.

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
1. mangle identifiers (scope-aware rename) — vs casual readers
2. string encryption (runtime decoder stub) — vs free-AI readers
3. AI-confusion layer (dead code, misleading comments, fake notes) — vs paid-AI + tools
4. custom transform (proprietary pass) — final trump card, needs private source maps
