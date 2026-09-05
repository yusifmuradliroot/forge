# forge

Mini compiler toolkit — general-purpose JS build/protect pipeline.
Private. Pass-based: input → passes → output.

## Usage

```bash
python3 tools/forge.py in.js out.js --passes strip_comments
```

## Layout

```
src/passes/   → transform passes (each: `run(code: str) -> str`)
tools/        → CLI (forge.py)
tests/        → fixtures
docs/         → design, pass catalog
```

## Version
See `VERSION`. Bumped on every behavior change.
