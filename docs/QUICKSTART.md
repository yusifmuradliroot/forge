# QUICKSTART — first build in 5 minutes

Needs: `python3` (3.8+) for the tool, `node` (any live version) to verify.
Make the command executable once: `chmod +x forge` (Unix; on Windows Git Bash
call `python3 tools/forge.py` directly). Full setup: `docs/INSTALL.md`.

## 1. Build the example

```bash
./forge examples/hello.js hello.fs
```

You will see one line per pass (`nolog`, `strip`, `short`, `num`, `flow`,
`simp`, `uni`, `crypt`, `pack`), then `wrote hello.fs`.
`hello.fs` is pure data — no code, just an `FS:2` tag, a manifest line,
and 3 base64 blobs.

## 2. Run it

```js
node -e "
const fs = require('fs');
eval(fs.readFileSync('src/runner/forgescript.js', 'utf8'));
ForgeScript.run(fs.readFileSync('hello.fs', 'utf8'));
"
```

Prints: `hello brave world, welcome ada`

The only thing that ever executes is the 1 KB runner
(`src/runner/forgescript.js`); your code travels as encrypted bytes.

## 3. See what changed (dev mode)

```bash
./forge examples/hello.js hello.dev.js --dev
```

`--dev` runs every pass except `pack` and emits readable JS:

```js
function a(c) {
  var b = __f(0)+__f(1);
  return b + c;
}
console.log(a("\x61\x64\x61"));
```

Names shortened (`greet`→`a`), the long string moved into a shuffled hex
table (`__f(0)+__f(1)`), the short one escaped (`"ada"`→`"\x61\x64\x61"`).
Same behavior: `node hello.dev.js` prints the same line (needs no runner).

## 4. Guard rails

- `nolog` strips `console.*` by default. The example keeps its log line
  with a `// keep-log` comment — that is the only exemption.
- `./forge in.js out.fs --audit` reports risky constructs
  (`eval`, `debugger`, sinks) and asks approval before building.
- `FORGE_KEEP='exact value'` exempts reserved strings from `uni`/`crypt`
  (comma-separated; unset = nothing exempt).
- `FORGE_SEED=N` makes every build unique (stub names, table order, keys);
  default builds are deterministic and diffable.

## 5. Verify the toolchain

```bash
bash tests/selftest.sh   # whole battery, must print SELFTEST GREEN
```

Embed into a host `.js` (userscript): put `/*__FORGE_RUNNER__*/` where the
runner should inline, then build with `--embed src/runner/forgescript.js
--embed-has ForgeScript --host` (pack is rejected in host mode).
Bake a stricter anti-debug gate into the embedded runner with
`--gate 30` (default 100ms; needs --embed).

Read next: `docs/FORMAT.md` (file spec), `docs/LIMITS.md` (trust model),
`docs/PASSES.md` (pass contracts).
