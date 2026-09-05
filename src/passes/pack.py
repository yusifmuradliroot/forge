"""pack pass: emit the .fs data file. ALWAYS LAST.

Output is pure data (FS:1 tag + encrypted blob). No loader inside —
execution belongs to the forgescript runner. Idempotent: repacking returns input.
"""

TAG = "FS:1"


def run(code: str) -> str:
    if code.startswith(TAG + "\n"):
        return code
    blob = "".join("%02x" % (ord(ch) ^ 0x5A) for ch in code)
    return TAG + "\n" + blob + "\n"
