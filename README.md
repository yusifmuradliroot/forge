# forge

![selftest](https://github.com/yusifmuradliroot/forge/actions/workflows/selftest.yml/badge.svg)
[![License: Custom (attribution + takedown)](https://img.shields.io/badge/License-Custom-blue.svg)](LICENSE)

**Hardened JS protection layer: raw JS in → `.fs` data file out, executed by the forgescript runner.**

Minimal by design. Current: **2.13.0** (`FS:2` segmented format, runner v5, hardened).

> **Trust model (read first):** The `.fs` signature proves the file was not ACCIDENTALLY damaged. With `FORGE_SIGN_KEY` set, it becomes an HMAC-SHA256 authenticity check — anyone without the key cannot mint a valid `.fs`. Without the key, FNV-1a is accident-check only (public, unkeyed). See `docs/LIMITS.md`.

## Install

Needs `python3` (3.8+) to build, `node` (any live version) to verify/run.  
No dependencies, no build step.

```bash
git clone https://github.com/yusifmuradliroot/forge.git
cd forge
chmod +x forge
./forge examples/hello.js hello.fs
```

Full guide: `docs/INSTALL.md`. 5-minute tour: `docs/QUICKSTART.md`.  
CLI flags: `docs/USAGE.md`. Questions: `docs/FAQ.md`.

## Pipeline

```
in.js ──► nolog ──► strip ──► short ──► num ──► flow ──► simp ──► uni ──► crypt ──► pack ──► out.fs ──► forgescript runner
```

`nolog` strips `console.*` statements (`keep-log` lines survive; `void console.*` goes as a whole). Passes run in the given order, except `pack` is always forced last. One shared scanner (`src/scan.py`) serves strip/short/nolog; property/pattern-position names are never renamed (`src/poison.py`, including `export` bindings and import specifiers). Live `${}` strings are encrypted; template TEXT middles stay verbatim. CRLF inputs are normalized to LF (Windows-safe).

## Usage

```bash
./forge in.js out.fs                    # full chain, diffable build
./forge in.js out.js --dev              # developer mode: readable, no pack
./forge in.js out.fs --strict           # refuse risky constructs (eval/with/export/etc.)
./forge in.js out.fs --strict --yes     # strict but force build anyway
./forge in.js out.fs --audit            # report risks, ask before building
./forge host.js out.js --passes nolog,strip,short,crypt --embed runner.js --embed-has ForgeScript --host
FORGE_SIGN_KEY=secret ./forge in.js out.fs   # HMAC-SHA256 signed .fs
FORGE_DEBUG=1 ./forge in.js out.fs       # show rejection reasons
python3 tools/check.py                   # integrity checker (incl. sig verify)
node tests/check_runner.js               # runner battery (multibyte + refusals)
bash tests/selftest.sh                   # whole battery, must print SELFTEST GREEN
```

Run an `.fs` file:

```js
eval(require('fs').readFileSync('src/runner/forgescript.js', 'utf8'));
ForgeScript.run(require('fs').readFileSync('out.fs', 'utf8'));
```

## Security Modes

| Mode | Env / Flag | Protection |
|------|-----------|------------|
| Default | none | FNV-1a accident-check, `--strict` opt-in |
| Signed | `FORGE_SIGN_KEY=...` | HMAC-SHA256 authenticity (`alg: "hmac"`) |
| Strict | `--strict` | Build refused on `eval`/`with`/`export`/sinks |
| Debug | `FORGE_DEBUG=1` | Runner rejection reasons printed |

## Support

- Bug reports / questions: GitHub Issues (`SUPPORT.md` shows what to include).
- Security issues: see `SECURITY.md` (do not open a public issue).
- Contributing: `CONTRIBUTING.md` (pass contract, battery-green rule).

## Layout

```
src/          → scan.py, poison.py, seed.py, audit.py
src/passes/   → nolog, strip, short, num, flow, simp, uni, crypt, pack
src/runner/   → forgescript.js — the runner (plain JS, runs ONLY FS:2 .fs)
tools/        → forge.py (translator CLI), check.py (integrity checker)
tests/        → fixtures + selftest.sh + check_runner.js
docs/         → INSTALL, QUICKSTART, USAGE, FAQ, FORMAT, PASSES, LIMITS, SUPPORT, SECURITY
examples/     → hello.js (minimal buildable example)
```

## Version

See `VERSION` (2.13.0). Changelog in `CHANGELOG.md`. `pyproject.toml` carries the same version.
