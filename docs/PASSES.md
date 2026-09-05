# Pass catalog

Every pass: `run(code: str) -> str`. Pure transform, never crashes on valid JS,
never changes runtime behavior.

| Pass | Status | Target | Notes |
|---|---|---|---|
| `strip_comments` | done | all | string-aware (`' " \``), fixture `tests/basic.js` |
| `mangle` | planned | casual readers | scope-aware identifier rename |
| `string_crypt` | planned | free-AI readers | encrypt strings, runtime decoder stub |
| `ai_confuse` | planned | paid-AI + tools | dead code, misleading comments, fake notes |
| `custom` | planned (last) | pros | proprietary transform, needs private source maps |

## Adding a pass
1. Create `src/passes/<name>.py` with `run(code)`.
2. Add a fixture under `tests/` proving strings/regex/URLs survive.
3. Register nothing — CLI loads by name. Run `tools/check.py`.
4. Bump `VERSION`, note in CHANGELOG.
