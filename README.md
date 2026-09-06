# forge

JS protection layer: raw JS in → `.fs` data file out, executed by the forgescript runner.
Private. Minimal by design. Current: 2.7.1 (`FS:2` segmented format, runner v4).

> Trust model (read first): the `.fs` signature proves the file was not
> ACCIDENTALLY damaged. It proves NOTHING about who made it — the format,
> keys and hash are public, so anyone can mint a fully-valid `.fs` for any
> content. Real protection = private raw + TLS + pinned URLs. Never rely on
> the sig for authenticity. See `docs/LIMITS.md`.

## Pipeline

```
in.js ──► nolog ──► strip ──► short ──► crypt ──► pack ──► out.fs ──► forgescript runner
```

nolog strips `console.*` statements (`keep-log` lines survive). Passes run in
the given order, except pack is always forced last. One shared scanner
(`src/scan.py`) serves strip/short/nolog; property/pattern-position names are
never renamed (`src/poison.py`).

## Usage

```bash
python3 tools/forge.py in.js out.fs          # full chain
python3 tools/forge.py in.js out.js --dev    # developer mode: readable, no pack
python3 tools/forge.py host.js out.js --passes nolog,strip,short,crypt --embed runner.js --embed-has ForgeScript --host
python3 tools/check.py                       # integrity checker (incl. sig verify)
python3 tools/forge.py in.js out.fs --audit  # report risks, build on approval
node tests/check_runner.js                   # runner battery (multibyte + refusals)
```

Run an `.fs` file (node example; browser/VM: load runner once, call `run`):
```js
eval(require('fs').readFileSync('src/runner/forgescript.js','utf8'));
ForgeScript.run(require('fs').readFileSync('out.fs','utf8'));
```

## Layout

```
src/          → scan.py (shared scanner), poison.py (never-rename names)
src/passes/   → nolog, strip, short, crypt, pack — each run(code: str) -> str
src/runner/   → forgescript.js — the runner (plain JS, runs ONLY FS:2 .fs)
tools/        → forge.py (translator CLI), check.py (integrity checker)
tests/        → fixtures + check_runner.js (runner battery)
docs/         → FORMAT.md (.fs spec), LIMITS.md (honest limits), ANALYSIS.md (v1 history)
```

## Version
See `VERSION`. Changelog in `CHANGELOG.md`.
