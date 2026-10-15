# USAGE — CLI reference

All commands run from the repo root. `./forge` is a thin wrapper for
`python3 tools/forge.py` (identical behavior).

## Build

```bash
./forge in.js out.fs
```

Runs the default chain
`nolog,strip,short,num,flow,simp,uni,crypt,pack` and writes `out.fs`
(pure data: `FS:2` tag + manifest + 3 base64 blobs). `pack` is always forced
last. Prints one line per pass plus `wrote out.fs`. Exit non-zero on any
failure, and nothing is written on abort.

## Developer mode

```bash
./forge in.js out.js --dev
```

Skips `pack`, emits readable processed JS (same behavior, no runner needed).
Use it to diff what each pass changed and to debug before packing.

## Audit gate

```bash
./forge in.js out.fs --audit
./forge in.js out.fs --audit --yes   # print report, skip prompt
```

Reports risky constructs in the RAW source with line numbers (`console`,
`debugger`, `eval`, `Function()`, timer-strings, sinks, plus `export` and
`with` which affect renaming) and asks approval before building.
`keep-log` lines are marked `KEPT`.

## Custom passes

```bash
./forge in.js out.js --passes nolog,strip,short,crypt --dev
```

Comma-separated names from `src/passes/`. Unknown names abort loudly.
`pack` is rejected in `--host` mode.

## Embed + host (userscript) mode

Put `/*__FORGE_RUNNER__*/` in the host where the runner should inline:

```bash
./forge host.js out.js --passes nolog,strip,short,crypt \
  --embed src/runner/forgescript.js --embed-has ForgeScript --host
```

- `--embed FILE`: inline FILE at the marker BEFORE passes run.
- `--embed-max BYTES` (default 8192): reject larger embed sources.
- `--embed-has STR`: embed source must contain STR (e.g. `ForgeScript`).
- `--host`: preserve the `==UserScript==` header, process the body only.
- `--gate MS` (needs `--embed`, default 100, 0..10000): bake a stricter
  runner anti-debug threshold into the embedded copy only.

## Run an .fs file

Node:

```js
eval(require('fs').readFileSync('src/runner/forgescript.js','utf8'));
ForgeScript.run(require('fs').readFileSync('out.fs','utf8'));
```

Browser / userscript manager: load `src/runner/forgescript.js` once, then
call `ForgeScript.run(fsText)`. Returns the payload result, or `null` when
the tag/manifest/signature/gate check refuses (silence is by design).

## Environment

- `FORGE_SEED=N`: unique builds per seed (stub names, table order, keys,
  short order). Unset = deterministic, diffable builds.
- `FORGE_KEEP='a,b'`: comma-separated exact string values `uni`/`crypt`
  never rewrite. Unset = nothing exempt.
- `FORGE_SCOPE=1`: experimental shadowed-param rename (verify output).

## Misc

```bash
./forge --version            # print VERSION
python3 tools/check.py       # integrity checker (exit 0 = PASS)
python3 tools/check.py --help
```

Input files may use LF or CRLF (normalized to LF). Output files are LF.
