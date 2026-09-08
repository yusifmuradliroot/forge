"""seed.py: the ONE build-variance source for forge.

pack keeps its own proven copy (untouched since 2.9.0 -- zero regression
risk); crypt and short import from here. Default (no FORGE_SEED in the
environment): historic behavior, diffable builds. With FORGE_SEED=N: same
input yields different bytes per seed, still deterministic per seed.
"""

import os


def fnv1a(data: bytes) -> int:
    h = 0x811C9DC5
    for b in data:
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def explicit_seed():
    """fnv1a int of FORGE_SEED, or None when unset/empty (default path)."""
    raw = os.environ.get("FORGE_SEED", "")
    if not raw:
        return None
    return fnv1a(b"forge-seed:" + raw.encode("utf-8"))


def shuffled(items, seed):
    """Deterministic LCG shuffle (same schedule family as pack)."""
    a = list(items)
    s = seed & 0xFFFFFFFF or 1
    for i in range(len(a) - 1, 0, -1):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        j = s % (i + 1)
        a[i], a[j] = a[j], a[i]
    return a


def keep_values():
    """Reserved strings (j-obfuscator `reservedStrings` precedent): exact
    decoded values that uni/crypt must never rewrite, comma-separated in
    FORGE_KEEP. Unset means none; default builds are unaffected."""
    return {v for v in os.environ.get("FORGE_KEEP", "").split(",") if v}
