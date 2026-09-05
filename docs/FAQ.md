# forge FAQ

**Is the output still readable?**
`strip_comments` + `mangle` output is readable-with-effort by design. Full
unreadability is not the goal (see `DESIGN.md` non-goals).

**Will passes break my code?**
They must not — that's the pass contract. If output misbehaves, bisect with
single `--passes` runs to find the culprit, then report with the fixture.

**Why no AST / dependencies?**
Zero-dependency single-file passes stay auditable and run anywhere python3 runs.

**Does encrypted output still pass `mustContain` checks?**
`string_crypt` skips short strings and never touches identifiers, so loader
markers (which are identifiers) always survive. Verify with `tools/check.py`.

**Mobile performance?**
Passes run at build time, not on device. Only `string_crypt`'s decoder stub runs
on device (one tiny function, negligible cost).
