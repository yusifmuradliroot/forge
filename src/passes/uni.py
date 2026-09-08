"""uni pass: short strings -> \\xNN escapes (same value, no readable words).

crypt encrypts values >= 12 chars; everything shorter stayed plaintext
(intent words like "join", keys, URLs). uni closes that half: pure-ASCII
short values become hex escapes. Same skip-set as crypt (markers,
directives, object-key position, template middles) and disjoint from crypt
by length, so pass order between the two is irrelevant.
"""

from scan import tokenize, template_inner_spans, sig_text


def run(code: str) -> str:
    toks = tokenize(code)
    in_tpl = set()
    for a, b in template_inner_spans(toks):
        for k in range(a, b + 1):
            in_tpl.add(k)
    out = []
    for idx, (kind, text) in enumerate(toks):
        if idx in in_tpl:
            out.append(text)
            continue
        if kind == "str" and text[:1] in ("'", '"') and len(text) >= 2 and text[-1:] == text[:1]:
            body = text[1:-1]
            if "\\" in body:
                try:
                    value = body.encode().decode("unicode_escape")
                except Exception:
                    out.append(text)
                    continue
            else:
                value = body
            if not value or len(value) >= 12:
                out.append(text)  # empty stays byte-identical; long is crypt's
                continue
            if value.startswith("__"):
                out.append(text)  # loader markers (mustContain) -- never touch
                continue
            if value in ("use strict", "use asm"):
                out.append(text)  # directives lose meaning when rewritten
                continue
            if not all(ord(ch) < 128 for ch in value):
                out.append(text)  # non-ASCII: unicode_escape round-trip unsafe
                continue
            prev_t = sig_text(toks, idx, -1).rstrip()
            next_t = sig_text(toks, idx, 1).lstrip()
            if next_t.startswith(":") and prev_t.endswith(("{", ",")):
                out.append(text)  # object key position -- keep readable
                continue
            q = text[:1]
            out.append(q + "".join("\\x%02x" % ord(ch) for ch in value) + q)
        else:
            out.append(text)
    return "".join(out)
