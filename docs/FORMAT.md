# .fs format — FS:2 (only)

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
  HONESTY NOTE: accident-check, NOT authenticity (FNV is public and unkeyed —
  anyone can mint valid files). See LIMITS.md.
- Runner flow (v4): tag → anti-debug gate → parse manifest → bounds-check
  indices → verify sig → decode per segment → CONCAT bytes → ONE TextDecoder
  (v4 fix: per-segment decode corrupted split multibyte chars) → execute.
- Unknown tag, bad JSON, missing/short/long blobs, bad indices, bad base64,
  bad UTF-8, bad sig → refuse (null). No exceptions escape except payload errors.

## FS:1 (removed in forge 2.4.0)
Single XOR-hex blob after the tag. Runner REFUSES it since runner v3.
Never emitted since 2.0.

## Reserved
`FS:3` = chunked execution (never full plaintext in memory — needs a scope-aware
splitter, i.e. a real compiler step). Not designed yet.
