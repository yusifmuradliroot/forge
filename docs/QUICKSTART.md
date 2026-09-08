# QUICKSTART — first build in 60 seconds

Needs: `python3` (3.8+) for the tool, `node` (any live version) to verify.

```bash
python3 tools/forge.py in.js out.fs          # full chain -> signed .fs
python3 tools/forge.py in.js out.js --dev    # readable, no pack (debug)
bash tests/selftest.sh                       # whole battery, must print GREEN
node tests/check_runner.js                   # runner battery alone
python3 tools/forge.py in.js out.fs --audit  # risk report, build on approval
```

Run an `.fs`:
```js
eval(require('fs').readFileSync('src/runner/forgescript.js', 'utf8'));
ForgeScript.run(require('fs').readFileSync('out.fs', 'utf8'));
```

Embed into a host `.js` (userscript): put `/*__FORGE_RUNNER__*/` where the
runner should inline, then build with `--embed src/runner/forgescript.js
--embed-has ForgeScript --host` (pack is rejected in host mode).
Bake a stricter anti-debug gate into the embedded runner with
`--gate 30` (default 100ms; needs --embed).

## What a build does (60-second example)
In: `function greet(name) { var msg = "hello brave world"; return msg + name; }`
Chain: `name`/`msg` shorten, `"hello brave world"` becomes a table call,
statements join with commas. Out (dev): still readable JS, same behavior.
Out (`.fs`): pure data, only the 1 KB runner executes it.

Read next: `docs/FORMAT.md` (file spec), `docs/LIMITS.md` (trust model),
`docs/PASSES.md` (pass contracts).
