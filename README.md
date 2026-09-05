# forge

JS protection layer: raw JS in → clean → shorten → encrypt → pack → working JS out.
Private. Minimal by design.

## Pipeline (v1)

```
in.js ──► strip ──► short ──► crypt ──► pack ──► out.js
```

## Layout

```
src/passes/   → one transform each: run(code: str) -> str
tools/        → CLI
tests/        → fixtures
docs/         → design docs
```

## Version
See `VERSION`.
