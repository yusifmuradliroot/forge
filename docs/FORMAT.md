# .fs format v1 (FS:1) — sketch, authoritative for the runner

A `.fs` file is PURE DATA. No loader, no code outside the payload.

```
FS:1
<hex>
```

- Line 1: tag `FS:1` — format id + language version. Plaintext by design.
- Rest: the stage-1 processed JS (stripped → shortened → string-encrypted),
  XOR `0x5A`, hex-encoded, newlines stripped.
- Runner flow: read tag → pick decoder for `1` → XOR-decode in memory →
  execute → wipe references. Unknown tag → refuse (return null, run nothing).
- Reserved: `FS:2` = segmented format (segments + map, never full plaintext).
  Runners must reject tags they don't implement.

/decisions locked during build: single blob v1 (chunked execution is v2)./
