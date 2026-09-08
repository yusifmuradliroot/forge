# PASSES — per-pass contracts (edit code freely, keep these true)

All passes: `run(code: str) -> str`. Pure (no I/O), never crash on valid JS,
never change runtime behavior — only representation. Order:
`nolog → strip → short → num → flow → simp → uni → crypt → pack` (pack forced last, rejected in --host).

Shared machinery: `src/scan.py` (tokenizer + mask — the ONLY scanner anyone
may use), `src/poison.py` (never-rename names, short only),
`src/seed.py` (build variance from FORGE_SEED — the ONLY seed source;
also `FORGE_KEEP`: comma-separated reserved string values uni/crypt skip).

## num — decimal ints to hex
Token-based: only matches inside `other` tokens, so strings/regex/comments/
templates are immune. Skips hex/octal-legacy/floats/exponents/BigInt and
dot-glued digits (`a.5`). Same value, shorter spelling.

## flow — provably-safe control-flow micro-transforms
- Comma-join of consecutive plain expression statements (`a(); b();` ->
  `a(), b();`). Skips anything with braces, statement-only keywords,
  directives (quote-start), regex-start statements and labels.
- Negation-flip (`if (!C) {A} else {B}` -> `if (C) {B} else {A}`) in
  statement position with braced bodies; `else if` chains untouched.
- `while (!0|true|1) {body}` -> `for (;;) {body}` (`do..while` unaffected).
- Mask-based analysis, original-text emission; confusion means skip.
  Fixpoint, max 3 rounds.

## simp — safe micro-simplifications
`true`→`!0`/`false`→`!1` (value positions only), safe-int folding, simple
string concat, literal dead branches (char-exact spans; `else if` chains and
methods literally named if/while are kept). Fixpoint, max 5 rounds.

## nolog — drop console.* statements
- In: any valid JS. Out: same minus statement-position `console.*` calls.
- Keeps: `keep-log` lines, expression uses (`x = f()`, ternary, `void`? no —
  `void` IS stripped), property access (`o.console`), template/comment/regex
  contents, `${}` inner code follows the same rules.
- Replaces removals with `;` (dangling `if (c)` bodies stay valid).
- Runs FIRST (needs comments for keep-log).

## strip — drop comments
- Removes `//` + `/* */` only. Regex/str/template-aware (a `//` inside
  `/\//` must not eat code). Byte-identical output for comment-free input.

## short — rename single-declaration locals
- Renames ONLY names declared exactly once (var/let/const/function/param/
  catch, incl. named + generator + anonymous params) that never appear as
  property, object key, shorthand, method, destructured name, after `new`,
  or in GLOBALS/RESERVED/poisoned sets. Cross-file contract names
  (`ForgeScript`) are GLOBALS.
- Number-adjacent letters are numeric suffixes (`123n`, `1e5`), never idents.
- Regex/division disambiguated with pending-buffer lookbehind.
- With FORGE_SEED set, assignment order shuffles (same input, different
  renames per seed); default order is sorted (diffable builds).
- FORGE_SCOPE=1 enables the N1 prototype: shadowed function params renamed
  inside their own span only (no nested function/arrow/eval/with/arguments).
  Experimental: verify output, default off.

## uni — short strings to \xNN escapes
- Only real `'...'`/`"..."` tokens with pure-ASCII values shorter than 12
  chars (crypt's half starts at 12 — disjoint by length, order irrelevant).
  Same value on the wire, no readable words on disk.
- Same skip-set as crypt: template middles, `__*` markers, directives,
  object-key position, non-ASCII values.

## crypt — encrypt long string literals into a shuffled table
- Only real `'...'`/`"..."` tokens, length ≥ 12, ASCII-only. Skips templates
  (incl. middles that merely LOOK like strings), `__*` markers, directives,
  object-key position, short strings.
- Output is ONE hex table + index-call decoder (`var __t=[..];var
  __f=function(i){..};` + `__f(3)+__f(0)` chains) after a directive prologue.
- Table order shuffles per FORGE_SEED (default: encounter order, diffable).
  Stub/table names, XOR key, chunk length and hex case derive from the seed
  (defaults: `__t`/`__f`, `0x5A`, 16, lowercase). The stub embeds its own key
  literal, so old `.fs` files keep running and seeded files never mix keys.
- Refuses sources already using the stub/table names (loud abort).

## pack — emit FS:2 (ALWAYS LAST)
- Splits UTF-8 bytes in thirds, per-exec-index XOR keys, deterministic
  FNV-seeded shuffle, FNV signature over ciphertext. Refuses empty/tiny input.
- Idempotent: repacking FS:2 returns it unchanged. See FORMAT.md.
