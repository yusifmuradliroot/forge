# Contributing

## Ground rules

- **Pass contract:** every pass is `run(code: str) -> str` — pure, never
  crashes, never changes behavior. Prove it with a fixture + runtime check
  in `tests/selftest.sh`, not with words.
- **One scanner:** all token work goes through `src/scan.py`. No pass rolls
  its own regex tokenizer.
- **Never-rename:** property/pattern positions and globals stay intact —
  extend `src/poison.py`, don't inline exemptions.
- **Minimalism:** no decoys, no fake content, no dead code, no comments in
  shipped code beyond one-line contracts.
- **English only** in code, comments, commits, issues.
- **Bump `VERSION`** on every behavior change; README + CHANGELOG ride with
  the bump (`tools/check.py` enforces this).
- **Whole battery green:** `bash tests/selftest.sh` must print
  `SELFTEST GREEN` before any push.

## Adding a pass

1. Create `src/passes/<name>.py` with `run(code)`.
2. Register it in the chain (`tools/forge.py`) and document it in
   `docs/PASSES.md`.
3. Add a fixture under `tests/` + a probe in `selftest.sh` that fails
   before your change and passes after.
4. Run the full battery. If any existing probe changes output, your pass
   is wrong until proven otherwise.
