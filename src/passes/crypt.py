"""crypt pass: encrypt long string literals, decode at runtime.

Only plain '...' and "..." literals with length >= MIN_LEN are touched.
Skipped: template literals (may hold ${expr}), short strings (markers, keys),
strings that look like code or URLs for safety? No — URLs are fine to encrypt,
they decode identically at runtime. Identifiers are never touched, so loader
markers (mustContain) always survive.
A tiny decoder stub is prepended once.
"""

MIN_LEN = 12
STUB = ("var __f=function(s){var o='',i=0;for(;i<s.length;i+=2)"
        "{o+=String.fromCharCode(parseInt(s.substr(i,2),16)^0x5A);}return o;};")


def _xor_hex(s):
    return "".join("%02x" % (ord(ch) ^ 0x5A) for ch in s)


def _prev_sig(code, i):
    i -= 1
    while i >= 0 and code[i] in " \t\r\n":
        i -= 1
    return code[i] if i >= 0 else ""


def _next_sig(code, j, n):
    while j < n and code[j] in " \t\r\n":
        j += 1
    return code[j] if j < n else ""


def run(code: str) -> str:
    out = []
    i, n = 0, len(code)
    changed = False
    while i < n:
        c = code[i]
        if c in ("'", '"'):
            j = i + 1
            raw = []
            while j < n:
                if code[j] == "\\" and j + 1 < n:
                    raw.append(code[j:j + 2])
                    j += 2
                    continue
                if code[j] == c:
                    break
                raw.append(code[j])
                j += 1
            if j >= n:
                out.append(code[i:])
                break
            body = "".join(raw)
            try:
                value = body.encode().decode("unicode_escape")
            except Exception:
                out.append(code[i:j + 1])
                i = j + 1
                continue
            if value.startswith("__"):
                # loader markers (mustContain) — never touch
                out.append(code[i:j + 1])
            elif value in ("use strict", "use asm"):
                # directives lose meaning when encrypted
                out.append(code[i:j + 1])
            elif (_next_sig(code, j + 1, n) == ":"
                    and _prev_sig(code, i) in ("{", ",")):
                # object key position {"k": v} — a call expr is invalid there
                out.append(code[i:j + 1])
            elif len(value) >= MIN_LEN and all(ord(ch) < 128 for ch in value):
                out.append("__f(\"" + _xor_hex(value) + "\")")
                changed = True
            else:
                out.append(code[i:j + 1])
            i = j + 1
        else:
            out.append(c)
            i += 1
    result = "".join(out)
    if changed and "__f=function" not in result:
        result = STUB + result
    return result
