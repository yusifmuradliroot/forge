# forge

![selftest](https://github.com/yusifmuradliroot/forge/actions/workflows/selftest.yml/badge.svg)

JS protection layer: raw JS in → `.fs` data file out, executed by the forgescript runner.
Private. Minimal by design. Current: 2.11.2 "golden gate era" (`FS:2` segmented format, runner v5).

> Trust model (read first): the `.fs` signature proves the file was not
> ACCIDENTALLY damaged. It proves NOTHING about who made it — the format,
> keys and hash are public, so anyone can mint a fully-valid `.fs` for any
> content. Real protection = private raw + TLS + pinned URLs. Never rely on
> the sig for authenticity. See `docs/LIMITS.md`.

## Pipeline

```
in.js ──► nolog ──► strip ──► short ──► num ──► flow ──► simp ──► uni ──► crypt ──► pack ──► out.fs ──► forgescript runner
```

nolog strips `console.*` statements (`keep-log` lines survive). Passes run in
the given order, except pack is always forced last. One shared scanner
(`src/scan.py`) serves strip/short/nolog; property/pattern-position names are
never renamed (`src/poison.py`).

## Usage

```bash
./forge in.js out.fs          # full chain (needs: chmod +x forge, once)
./forge in.js out.js --dev    # developer mode: readable, no pack
./forge host.js out.js --passes nolog,strip,short,crypt --embed runner.js --embed-has ForgeScript --host
./forge in.js out.fs --audit  # report risks, build on approval
python3 tools/check.py        # integrity checker (incl. sig verify)
node tests/check_runner.js    # runner battery (multibyte + refusals)
```

Run an `.fs` file (node example; browser/VM: load runner once, call `run`):
```js
eval(require('fs').readFileSync('src/runner/forgescript.js','utf8'));
ForgeScript.run(require('fs').readFileSync('out.fs','utf8'));
```

## First time
See `docs/QUICKSTART.md` (needs python3 3.8+, node any live version).

## Layout

```
src/          → scan.py (shared scanner), poison.py (never-rename names)
src/passes/   → nolog, strip, short, num, flow, simp, uni, crypt, pack — each run(code: str) -> str
src/runner/   → forgescript.js — the runner (plain JS, runs ONLY FS:2 .fs)
tools/        → forge.py (translator CLI), check.py (integrity checker)
tests/        → fixtures + check_runner.js (runner battery)
docs/         → FORMAT.md (.fs spec), LIMITS.md (honest limits), ANALYSIS.md (v1 history)
```

## Version
See `VERSION`. Changelog in `CHANGELOG.md`.
