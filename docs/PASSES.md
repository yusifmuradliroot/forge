# Pass catalog

Every pass: `run(code: str) -> str`. Pure transform, never crashes on valid JS,
never changes runtime behavior.

| Pass | Status | Target | Notes |
|---|---|---|---|
| `strip_comments` | done | all | string-aware (`' " \``), fixture `tests/basic.js` |
| `mangle` | done | casual readers | single-declaration locals only; shadow/property/key/regex/template safe; fixture `tests/mangle.js` |
| `string_crypt` | done | free-AI readers | `__f` XOR-hex stub; skips short/`__*`/directives/object keys/templates; fixture `tests/string_crypt.js`, node-verified |
| `ai_confuse` | done | paid-AI + tools | fake banner + 3 collision-checked decoys, append-only |
| `custom` | planned (last) | pros | proprietary transform, needs private source maps |

## Adding a pass
1. Create `src/passes/<name>.py` with `run(code)`.
2. Add a fixture under `tests/` proving strings/regex/URLs survive.
3. Register nothing — CLI loads by name. Run `tools/check.py`.
4. Bump `VERSION`, note in CHANGELOG.
