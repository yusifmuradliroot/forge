# forge design

## Idea
`forge` is a pass pipeline: JS text in → ordered string transforms → JS text out.
No parsing to AST, no dependencies, single python file per pass. Boring on purpose:
every pass is auditable in one screen.

```
in.js ──► strip_comments ──► mangle ──► string_crypt ──► ai_confuse ──► out.js
              (readability)    (names)      (strings)        (noise)
```

Order matters: clean first, rename second, encrypt strings third (so encrypted blobs
don't get renamed), add noise last (so noise itself isn't transformed).

## Guarantees (every pass)
1. Pure function `run(code: str) -> str`. No I/O, no config files, no network.
2. Never crashes on valid JS — worst case returns input unchanged.
3. Never changes runtime behavior — only representation.
4. String/regex/template aware: never touches text inside `'...'`, `"..."`, `` `...` ``.

## Non-goals
- Not a minifier war machine: no AST, no cross-file bundling, no type analysis.
- Heavy obfuscation is deliberately OUT (slow on mobile, kills debugging).
- The final trump card (`custom` proprietary transform) comes last, separately.
