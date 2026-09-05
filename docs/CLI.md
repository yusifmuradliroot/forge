# forge CLI reference

```
python3 tools/forge.py SRC DST --passes P1[,P2,...]
```

| Argument | Meaning |
|---|---|
| `SRC` | input JS file (utf-8) |
| `DST` | output JS file (overwritten) |
| `--passes` | comma-separated pass names from `src/passes/` (default: `strip_comments`) |

Stdout reports each applied pass with the running char count, then the output path.
Exit code is 0 on success; a traceback means a pass violated its contract (report it).
