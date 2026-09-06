"""crypt pass: encrypt long string literals, decode at runtime.

Token-based (shared scanner): ONLY real '...'/"..." string tokens are
touched. Regex content, comments and template chunks are never scanned --
a regex like /42\\["(10|34)",.../ used to be shredded because its quotes
looked like string bounds (silent output corruption).
Skipped: template literals (may hold ${expr}), short strings (markers, keys),
__-prefixed (loader markers), directives, object-key position.
A tiny decoder stub is appended after a directive prologue (strict kept).
Source already using __f aborts loudly.
"""

import re as _re

MIN_LEN = 12
STUB = ("var __f=function(s){var o='',i=0;for(;i<s.length;i+=2)"
        "{o+=String.fromCharCode(parseInt(s.substr(i,2),16)^0x5A);}return o;};")

try:
    from scan import tokenize
except ImportError:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from scan import tokenize


def _xor_hex(s):
    return "".join("%02x" % (ord(ch) ^ 0x5A) for ch in s)


def _sig_text(toks, idx, direction):
    """Nearest significant token text in direction (-1/1), skipping comments."""
    i = idx + direction
    while 0 <= i < len(toks):
        kind, text = toks[i]
        if kind == "comment":
            i += direction
            continue
        return text
    return ""


def run(code: str) -> str:
    toks = tokenize(code)
    out = []
    changed = False
    for idx, (kind, text) in enumerate(toks):
        if kind == "str" and text[:1] in ("'", '"') and len(text) >= 2 and text[-1:] == text[:1]:
            body = text[1:-1]
            try:
                value = body.encode().decode("unicode_escape")
            except Exception:
                value = None
            if value is None:
                out.append(text)
                continue
            if value.startswith("__"):
                out.append(text)  # loader markers (mustContain) — never touch
                continue
            if value in ("use strict", "use asm"):
                out.append(text)  # directives lose meaning when encrypted
                continue
            prev_t = _sig_text(toks, idx, -1).rstrip()
            next_t = _sig_text(toks, idx, 1).lstrip()
            if next_t.startswith(":") and prev_t.endswith(("{", ",")):
                out.append(text)  # object key position — a call is invalid there
                continue
            if len(value) >= MIN_LEN and all(ord(ch) < 128 for ch in value):
                out.append('__f("' + _xor_hex(value) + '")')
                changed = True
                continue
            out.append(text)
        else:
            out.append(text)
    result = "".join(out)
    if changed:
        if "__f" in set(_re.findall(r"[A-Za-z_$][\w$]*", code)):
            raise ValueError("crypt: source already uses __f; rename it first")
        m = _re.match(
            r"((?:[ \t\r\n;]*(?:\"(?:use strict|use asm)\"|'(?:use strict|use asm)')[ \t]*;?)*)",
            result)
        cut = m.end(1)
        glue = ";" if cut and (cut >= len(result) or result[cut] not in ";\n") else ""
        result = result[:cut] + glue + STUB + result[cut:]
    return result
