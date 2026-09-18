# Security policy

## Scope
`forge` is an obfuscation/build tool, not a security boundary. Read
`docs/LIMITS.md` first: the `.fs` signature is accident-check (FNV-1a,
unkeyed), the runner is readable by design, and plaintext exists in memory
at execution time.

## What to report privately
- A pass that silently changes runtime behavior (with minimal repro).
- A crafted input that crashes the toolchain with data loss.
- Anything that executes attacker input during BUILD (passes never `eval`).

Out of scope: recovering content from `.fs` with repo access (by design),
the `debugger` gate being bypassable (documented as light), and CRLF/tag
refusals returning `null` (silence is the point).

## How to report
Use GitHub **Private vulnerability reporting** (Security tab). Do not open a
public issue for unpatched behavior-changing bugs. Include `VERSION`, repro
files, `node --check` output, and `bash tests/selftest.sh` tail.

## Response
Reports are triaged as soon as possible. Behavior-changing bugs get a VERSION
bump + regression probe + CHANGELOG entry before release.
