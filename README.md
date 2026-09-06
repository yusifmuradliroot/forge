# forge

JS protection layer: raw JS in → `.fs` data file out, executed by the forgescript runner.
Private. Minimal by design. Current: v2 (`FS:2` segmented format + signatures).

## Pipeline

```
in.js ──► strip ──► short ──► crypt ──► pack ──► out.fs ──► forgescript runner
```

## Usage

```bash
python3 tools/forge.py in.js out.fs          # full chain
python3 tools/forge.py in.js out.js --dev    # developer mode: readable, no pack
python3 tools/forge.py host.js out.js --passes strip,short,crypt --embed runner.js
python3 tools/check.py                       # integrity checker
```

Run an `.fs` file (node example; browser/VM: load runner once, call `run`):
```js
eval(require('fs').readFileSync('src/runner/forgescript.js','utf8'));
ForgeScript.run(require('fs').readFileSync('out.fs','utf8'));
```

## Layout

```
src/passes/   → strip, short, crypt, pack — each run(code: str) -> str
src/runner/   → forgescript.js — the runner (plain JS, runs ONLY .fs)
tools/        → forge.py (translator CLI), check.py (integrity checker)
tests/        → fixtures (e2e.js = end-to-end sample)
docs/         → FORMAT.md (.fs spec), ANALYSIS.md (deep review + v2 backlog)
```

## Version
See `VERSION`. Changelog in `CHANGELOG.md`.
