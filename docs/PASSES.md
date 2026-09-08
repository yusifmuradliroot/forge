# PASSES — per-pass contracts (edit code freely, keep these true)

All passes: `run(code: str) -> str`. Pure (no I/O), never crash on valid JS,
never change runtime behavior — only representation. Order:
`nolog → strip → short → num → simp → uni → crypt → pack` (pack forced last, rejected in --host).

Shared machinery: `src/scan.py` (tokenizer + mask — the ONLY scanner anyone
may use), `src/poison.py` (never-rename names, short only),
`src/seed.py` (build variance from FORGE_SEED — the ONLY seed source).

## num — decimal ints to hex
Token-based: only matches inside `other` tokens, so strings/regex/comments/
templates are immune. Skips hex/octal-legacy/floats/exponents/BigInt and
dot-glued digits (`a.5`). Same value, shorter spelling.

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
  catch, incl. `function*` params) that never appear as property, object key,
  shorthand, method, destructured name, after `new`, or in GLOBALS/RESERVED/
  poisoned sets. Cross-file contract names (`ForgeScript`) are GLOBALS.
- Number-adjacent letters are numeric suffixes (`123n`, `1e5`), never idents.
- Regex/division disambiguated with pending-buffer lookbehind.
- With FORGE_SEED set, assignment order shuffles (same input, different
  renames per seed); default order is sorted (diffable builds).

## uni — short strings to \xNN escapes
- Only real `'...'`/`"..."` tokens with pure-ASCII values shorter than 12
  chars (crypt's half starts at 12 — disjoint by length, order irrelevant).
  Same value on the wire, no readable words on disk.
- Same skip-set as crypt: template middles, `__*` markers, directives,
  object-key position, non-ASCII values.

## crypt — encrypt long string literals
- Only real `'...'`/`"..."` tokens, length ≥ 12, ASCII-only. Skips templates
  (incl. middles that merely LOOK like strings), `__*` markers, directives,
  object-key position, short strings.
- XOR base is per-build: historic `0x5A` by default (diffable), derived from
  FORGE_SEED when set. The stub embeds its own key literal, so every old
  `.fs` keeps running and seeded files never mix keys.
- Decoder stub goes AFTER a directive prologue (strict kept) or at top.
- Refuses sources already using `__f` (mask-checked, comments don't count).

## pack — emit FS:2 (ALWAYS LAST)
- Splits UTF-8 bytes in thirds, per-exec-index XOR keys, deterministic
  FNV-seeded shuffle, FNV signature over ciphertext. Refuses empty/tiny input.
- Idempotent: repacking FS:2 returns it unchanged. See FORMAT.md.
