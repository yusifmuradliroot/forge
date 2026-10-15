# Security

## Disclosure

Report security issues privately. Do not open public issues for vulnerabilities.

## Threat Model

Forge protects against:
- Casual source code reading
- Free AI-assisted reverse engineering
- Accidental `.fs` corruption

Forge does NOT protect against:
- Determined analysts with the `.fs` and source
- Memory dumping at execution time
- Key extraction if `FORGE_SIGN_KEY` is leaked

## Best Practices

1. Keep raw JS private (never commit it)
2. Use `FORGE_SIGN_KEY` for production builds
3. Rotate signing keys periodically
4. Deliver `.fs` over TLS with pinned URLs
5. Run `--strict` in CI
6. Verify with `tools/check.py` before deployment
