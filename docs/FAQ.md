# FAQ — questions people actually ask

## What does forge do?
Raw JS in, working-but-hard-to-read JS out. Long strings move into a shuffled
hex table, short strings become `\xNN` escapes, locals shorten, numbers go
hex, safe control-flow/forms simplify — then everything packs into an
encrypted `.fs` data file that only the 1 KB `forgescript` runner executes.

## What does it protect against?
The curious and automated readers: casual copy-paste, free-AI skims, drive-by
inspection. It does NOT stop a funded analyst with the `.fs` and this repo
(the method is public; the content is what's hidden). See `docs/LIMITS.md`.

## Does the signature prove who made the file?
No. It proves the file was not ACCIDENTALLY damaged (truncation, bad edit,
our own regression). Anyone can mint a fully-valid `.fs` for any content.
Real authenticity = private raw + TLS + pinned URLs. Never rely on the sig.

## How do I keep a console.log line?
Add `keep-log` on the same line (comment): `console.log(x); // keep-log`.
Everything else `console.*` in statement position is stripped by default.

## Why is my output silent?
`nolog` strips `console.*` by default. Either add `// keep-log` or check
with `--dev` output. This bites every hello-world — it is by design.

## Can I forge code with eval / with?
No. Keep both out of forged sources (`--audit` flags them). Renaming locals
around `eval("name")` / `with (obj)` breaks lookups. `FORGE_SCOPE=1` is even
stricter (experimental).

## What about export / import?
`export` names are kept verbatim so importers match; `--audit` lists every
`export` for review. Forge targets bundles — bundle (or eliminate imports)
before forging. Import specifiers would otherwise be escaped/encrypted.

## Template literals?
Live `${}` strings ARE protected (encrypted/escaped). Template TEXT itself
(the parts between backticks outside `${}`) stays verbatim — a decoder call
there would be a syntax error. Middle `"b"` in `` `a${x}"b"${y}c` `` is kept.

## Deterministic builds? Unique builds?
Default (no env) = deterministic and diffable. `FORGE_SEED=N` = same input,
different bytes per seed (stub identity, table order, keys, short order),
still deterministic per seed. Old `.fs` files keep running (stubs carry keys).

## How big / how fast?
Expect roughly +30-40% bytes on small files (table + stub amortize on larger
ones) and single-digit-ms runner overhead (one array alloc). Measure on your
file with `--dev` + `time`.

## Which JS is supported?
Modern plain JS bundles. Node 20 runs the battery; output targets Firefox +
Violentmonkey (also node/browsers). Mobile Firefox at scale is untested —
verify per release on your target.

## Windows?
Yes — Git Bash, LF enforced (`.gitattributes`), CRLF inputs normalized.
Builds are byte-identical to Linux. See `docs/INSTALL.md`.

## Troubleshooting
- `SELFTEST RED`: paste the failing probe line + full log (see `SUPPORT.md`).
- Runner returns `null`: tampered `.fs`, unknown tag, bad manifest/sig, or
  the anti-debug gate tripped. Diagnose via `--dev` output + battery, never
  by staring at `null` (silence is the point).
- `pack: empty input` / `too short`: inputs need ≥3 bytes of UTF-8.
- `crypt: source already uses __t/__f`: rename your identifiers first.
- `pack rejected in host mode`: hosts must stay installable `.js` — drop pack.
- `--gate needs --embed`: the threshold lives in the embedded runner copy.
- `void ;` SyntaxError: fixed in 2.12.0 — update forge.
