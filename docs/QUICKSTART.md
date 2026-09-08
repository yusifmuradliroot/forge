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

Read next: `docs/FORMAT.md` (file spec), `docs/LIMITS.md` (trust model),
`docs/PASSES.md` (pass contracts).
