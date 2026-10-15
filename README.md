# forge

![selftest](https://github.com/yusifmuradliroot/forge/actions/workflows/selftest.yml/badge.svg)
[![License: Custom (attribution + takedown)](https://img.shields.io/badge/License-Custom-blue.svg)](LICENSE)

JS protection layer: raw JS in → `.fs` data file out, executed by the forgescript runner.
Minimal by design. Current: 2.12.0 (`FS:2` segmented format, runner v5).

> Trust model (read first): the `.fs` signature proves the file was not
> ACCIDENTALLY damaged. It proves NOTHING about who made it — the format,
> keys and hash are public, so anyone can mint a fully-valid `.fs` for any
> content. Real protection = private raw + TLS + pinned URLs. Never rely on
> the sig for authenticity. See `docs/LIMITS.md`.

## Install

Needs `python3` (3.8+) to build, `node` (any live version) to verify/run.
No dependencies, no build step.

```bash
git clone https://github.com/yusifmuradliroot/forge.git
cd forge
chmod +x forge          # once
./forge examples/hello.js hello.fs
```

Full guide: `docs/INSTALL.md`. 5-minute tour: `docs/QUICKSTART.md`.
CLI flags: `docs/USAGE.md`. Questions: `docs/FAQ.md`.

## Pipeline

```
in.js ──► nolog ──► strip ──► short ──► num ──► flow ──► simp ──► uni ──► crypt ──► pack ──► out.fs ──► forgescript runner
```

nolog strips `console.*` statements (`keep-log` lines survive; `void console.*`
goes as a whole). Passes run in the given order, except pack is always forced
last. One shared scanner (`src/scan.py`) serves strip/short/nolog;
property/pattern-position names are never renamed (`src/poison.py`, including
`export` bindings). Live `${}` strings are encrypted; template TEXT middles
stay verbatim. CRLF inputs are normalized to LF (Windows-safe).

## Usage

```bash
./forge in.js out.fs          # full chain
./forge in.js out.js --dev    # developer mode: readable, no pack
./forge host.js out.js --passes nolog,strip,short,crypt --embed runner.js --embed-has ForgeScript --host
./forge in.js out.fs --audit  # report risks, build on approval
python3 tools/check.py        # integrity checker (incl. sig verify)
node tests/check_runner.js    # runner battery (multibyte + refusals)
bash tests/selftest.sh        # whole battery, must print SELFTEST GREEN
```

Run an `.fs` file (node example; browser/VM: load runner once, call `run`):
```js
eval(require('fs').readFileSync('src/runner/forgescript.js','utf8'));
ForgeScript.run(require('fs').readFileSync('out.fs','utf8'));
```

## Support

- Bug reports / questions: GitHub Issues (`SUPPORT.md` shows what to include).
- Security issues: see `SECURITY.md` (do not open a public issue).
- Contributing: `CONTRIBUTING.md` (pass contract, battery-green rule).

## Layout

```
src/          → scan.py (shared scanner), poison.py (never-rename names), seed.py (variance), audit.py (risk report)
src/passes/   → nolog, strip, short, num, flow, simp, uni, crypt, pack — each run(code: str) -> str
src/runner/   → forgescript.js — the runner (plain JS, runs ONLY FS:2 .fs)
tools/        → forge.py (translator CLI), check.py (integrity checker)
tests/        → fixtures + selftest.sh (full battery) + check_runner.js (runner battery)
docs/         → INSTALL.md, QUICKSTART.md, USAGE.md, FAQ.md, FORMAT.md (.fs spec), PASSES.md, LIMITS.md
examples/     → hello.js (minimal buildable example)
```

## Version
See `VERSION` (2.12.0). Changelog in `CHANGELOG.md`. `pyproject.toml` carries the same version.
