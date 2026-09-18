# INSTALL — get forge running

## Requirements

- `python3` 3.8+ (the toolchain; CI tests 3.13)
- `node` any live version (to verify output and run `.fs` files)
- `git`, `bash` (for `tests/selftest.sh`)
- Zero Python/JS dependencies. Nothing to `pip install` / `npm install`.

## Clone

```bash
git clone https://github.com/yusifmuradliroot/forge.git
cd forge
chmod +x forge          # once, Unix only
```

`pyproject.toml` carries package metadata (same version as `VERSION`);
there is nothing to install — you run `./forge` (or `python3 tools/forge.py`)
from the repo root.

## Verify

```bash
python3 tools/check.py        # must print RESULT: PASS
node tests/check_runner.js    # must print RUNNER-BATTERY PASS
bash tests/selftest.sh        # must print SELFTEST GREEN (21 probes)
```

If any step is red, see `docs/FAQ.md` (Troubleshooting) and paste the full
output into your issue (`SUPPORT.md`).

## Windows notes

- Use **Git Bash** (CI runs `bash tests/selftest.sh` on `windows-latest`).
- Line endings are forced to LF (`.gitattributes`); the CLI also normalizes
  CRLF inputs to LF, so Windows builds are byte-identical to Linux.
- `chmod +x forge` is not needed on Windows; call `python3 tools/forge.py`
  directly if `./forge` does not execute.

## Next

- 5-minute tour: `docs/QUICKSTART.md`
- Full flags: `docs/USAGE.md`
- Questions: `docs/FAQ.md`
