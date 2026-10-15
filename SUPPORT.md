# Support — how to get help

## Where
Open a GitHub Issue. For usage questions, use the issue tracker too (do not
DM maintainers) so answers stay searchable.

## Before opening
1. Read `docs/QUICKSTART.md` (5-minute tour), `docs/USAGE.md` (flags),
   `docs/FAQ.md` (incl. Troubleshooting) and `docs/LIMITS.md` (trust model).
2. Reproduce on the latest `main` with the minimal input that still fails.

## Include in every issue
- `forge --version` output
- Exact command + flags (e.g. `./forge in.js out.fs --dev`)
- `python3 --version`, `node --version`, OS + shell (esp. Windows/Git Bash)
- Minimal input file (or `examples/hello.js` + your diff)
- Full terminal output, plus `bash tests/selftest.sh` tail (GREEN/RED + probe)
- For runtime bugs: expected vs actual behavior (`node --check` result helps)

## Response expectations
Maintainers are a small team (often one). Well-specified issues with a
minimal repro get answered first. PRs must keep `bash tests/selftest.sh`
green — see `CONTRIBUTING.md`.
