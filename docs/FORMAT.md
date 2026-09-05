# .fs format — FS:2 (current) and FS:1 (legacy, read-only)

A `.fs` file is PURE DATA. No loader, no code outside the payload.

## FS:2

```
FS:2
{"o":[disk indices in exec order],"s":sig}
<base64 blob per line, disk (shuffled) order, always 3 segments>
```

- Segments: stage output as UTF-8 bytes, split in thirds (reassembly is byte-exact,
  split points irrelevant). Disk order is a deterministic shuffle (FNV-seeded) —
  same input always yields the same file (diffable builds).
- Per-exec-index key: `kb = 0x5A ^ ((e*31+7) % 256)`, XOR over bytes, then base64.
- `sig = fnv1a32hex("FS:2\\n" + order.join(",") + "\\n" + blobs-in-exec-order)`.
  Runner verifies BEFORE decrypting; mismatch → refuse, run nothing.
- Runner flow: tag → anti-debug gate → parse manifest → bounds-check indices →
  verify sig → decode in manifest order → TextDecoder → execute → wipe refs.
- Unknown tag, bad JSON, missing/short/long blobs, bad indices, bad base64,
  bad UTF-8, bad sig → refuse (null). No exceptions escape except payload errors.

## FS:1 (legacy)
Single XOR-hex blob after the tag. Runner still reads it. Never emitted anymore.

## Reserved
`FS:3` = chunked execution (never full plaintext in memory — needs a scope-aware
splitter, i.e. a real compiler step). Not designed yet.
