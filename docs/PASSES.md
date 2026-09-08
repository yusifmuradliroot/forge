# PASSES — per-pass contracts (edit code freely, keep these true)

All passes: `run(code: str) -> str`. Pure (no I/O), never crash on valid JS,
never change runtime behavior — only representation. Order:
`nolog → strip → short → crypt → pack` (pack forced last, rejected in --host).

Shared machinery: `src/scan.py` (tokenizer + mask — the ONLY scanner anyone
may use), `src/poison.py` (never-rename names, short only).

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

## crypt — encrypt long string literals
- Only real `'...'`/`"..."` tokens, length ≥ 12, ASCII-only. Skips templates
  (incl. middles that merely LOOK like strings), `__*` markers, directives,
  object-key position, short strings.
- Decoder stub goes AFTER a directive prologue (strict kept) or at top.
- Refuses sources already using `__f` (mask-checked, comments don't count).

## pack — emit FS:2 (ALWAYS LAST)
- Splits UTF-8 bytes in thirds, per-exec-index XOR keys, deterministic
  FNV-seeded shuffle, FNV signature over ciphertext. Refuses empty/tiny input.
- Idempotent: repacking FS:2 returns it unchanged. See FORMAT.md.
