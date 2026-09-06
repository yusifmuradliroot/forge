"""pack pass: emit the .fs data file. ALWAYS LAST.

FS:2 layout (pure data, no loader inside):
  line 1: FS:2
  line 2: manifest JSON {"o":[disk indices in exec order],"s":sig}
  rest:   base64 blobs, one per line, disk (shuffled) order

- Always 3 segments, split by UTF-8 byte thirds (reassembly is byte-exact,
  so split points are irrelevant to correctness).
- Per-exec-index key: kb = 0x5A ^ ((e*31+7) % 256), XOR over UTF-8 bytes.
- Disk order: deterministic shuffle seeded by FNV-1a of the input (same input
  always yields the same .fs — diffable builds).
- sig = fnv1a32hex("FS:2\\n" + ",".join(order) + "\\n" + blobs-in-exec-order).
- Idempotent: repacking an FS:2 file returns it unchanged.
"""

import base64
import json

TAG = "FS:2"
NSEG = 3


def fnv1a(data: bytes) -> int:
    h = 0x811C9DC5
    for b in data:
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def _shuffle(idx, seed):
    a = list(idx)
    s = seed & 0xFFFFFFFF or 1
    for i in range(len(a) - 1, 0, -1):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        j = s % (i + 1)
        a[i], a[j] = a[j], a[i]
    return a


def run(code: str) -> str:
    if code.startswith(TAG + "\n"):
        return code
    if not code.strip():
        # L14: an empty input would emit a manifest claiming 3 blobs with
        # zero blob lines (refused downstream). Abort loudly instead.
        raise ValueError("pack: empty input")
    data = code.encode("utf-8")
    third = (len(data) + NSEG - 1) // NSEG
    segs = [data[i * third:(i + 1) * third] for i in range(NSEG)]
    blobs_exec = []
    for e, seg in enumerate(segs):
        kb = 0x5A ^ ((e * 31 + 7) % 256)
        blobs_exec.append(base64.b64encode(bytes(b ^ kb for b in seg)).decode("ascii"))
    seed = fnv1a(data)
    disk = _shuffle(list(range(NSEG)), seed)
    order = [disk.index(e) for e in range(NSEG)]
    blobs_disk = [""] * NSEG
    for d_pos, exec_idx in enumerate(disk):
        blobs_disk[d_pos] = blobs_exec[exec_idx]
    sig_input = (TAG + "\n" + ",".join(map(str, order)) + "\n"
                 + "".join(blobs_exec)).encode("utf-8")
    sig = "%08x" % fnv1a(sig_input)
    manifest = json.dumps({"o": order, "s": sig})
    return TAG + "\n" + manifest + "\n" + "\n".join(blobs_disk) + "\n"
