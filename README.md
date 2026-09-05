# forge

JS protection layer: raw JS in → `.fs` data file out, executed by the forgescript runner.
Private. Minimal by design.

## Pipeline (v1)

```
in.js ──► strip ──► short ──► crypt ──► pack ──► out.fs ──► forgescript runner
```

## Usage

```bash
python3 tools/forge.py in.js out.fs
node -e "eval(require('fs').readFileSync('src/runner/forgescript.js','utf8')); ForgeScript.run(require('fs').readFileSync('out.fs','utf8'));"
```

## Layout

```
src/passes/   → strip, short, crypt, pack — each run(code: str) -> str
src/runner/   → forgescript.js — the runner (plain JS, runs ONLY .fs)
tools/        → forge.py (translator CLI), check.py (integrity checker)
tests/        → fixtures (e2e.js = end-to-end sample)
docs/         → FORMAT.md (.fs spec)
```

## Version
See `VERSION`.
