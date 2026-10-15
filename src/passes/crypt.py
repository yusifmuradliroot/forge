"""crypt pass: encrypt long string literals into a shuffled table (S1+S2).

Token-based (shared scanner): ONLY real '...'/"..." string tokens are
touched. Regex content, comments and template chunks are never scanned.
Skipped: template literals (may hold ${expr}), short strings (uni's half),
__-prefixed (loader markers), directives, object-key position.

Output shape: ONE hex table + index-call decoder appended after a directive
prologue (strict kept). Table entry order shuffles per FORGE_SEED (default:
encounter order, diffable). Stub/table names, XOR key, chunk length and hex
case all derive from the seed (defaults: __t/__f, 0x5A, 16, lowercase).
Each file's stub carries its own key literal, so old .fs files keep running
and seeded files never mix keys. A source already using the stub/table
names aborts loudly.
"""

import re as _re

MIN_LEN = 12
STUB_TPL = ("var {t}=[{e}];var {f}=function(i){{var s={t}[i],o='',j=0;"
            "for(;j<s.length;j+=2)o+=String.fromCharCode(parseInt(s.substr(j,2),16)^0x{k});"
            "return o;}};")

try:
    from scan import tokenize, template_inner_spans as _template_spans, sig_text as _sig_text
    from seed import explicit_seed, shuffled, keep_values
except ImportError:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from scan import tokenize, template_inner_spans as _template_spans, sig_text as _sig_text
    from seed import explicit_seed, shuffled, keep_values


def _params():
    """(key, chunk_len, table_name, fn_name, upper_fn). Defaults preserve
    the historic shape (diffable builds); seeds vary everything."""
    seed = explicit_seed()
    if seed is None:
        return 0x5A, 16, "__t", "__f", lambda h, k: h
    tag = "%04x" % (seed % 65536)

    def upper(h, k):
        return h.upper() if (seed >> (k % 24)) & 1 else h

    return seed % 255 + 1, 8 + seed % 17, "__t" + tag, "__f" + tag, upper


def _xor_hex(s, key):
    return "".join("%02x" % (ord(ch) ^ key) for ch in s)


def _is_tpl_middle(toks, idx):
    """True if a real-looking quoted token is template literal TEXT between
    `}` and `${` (e.g. `a${x}"b"${y}c`). Such middles must stay verbatim --
    an `__f()` call there is a syntax error. Live `${}` code (prev `+`/`${`
    etc.) returns False and stays encryptable."""
    prev_t = _sig_text(toks, idx, -1).rstrip()
    next_t = _sig_text(toks, idx, 1).lstrip()
    return prev_t.endswith("}") and next_t.startswith("${")


def run(code: str) -> str:
    toks = tokenize(code)
    key, chunk_len, table_name, fn_name, upper = _params()
    in_tpl = set()
    for a, b in _template_spans(toks):
        for k in range(a, b + 1):
            in_tpl.add(k)
    entries = []  # hex chunks, encounter order
    targets = {}  # token idx -> encounter entry indices
    keep = keep_values()
    for idx, (kind, text) in enumerate(toks):
        if idx in in_tpl:
            if not (kind == "str" and text[:1] in ("'", '"')
                    and len(text) >= 2 and text[-1:] == text[:1]):
                continue
            if _is_tpl_middle(toks, idx):
                continue
        if kind == "str" and text[:1] in ("'", '"') and len(text) >= 2 and text[-1:] == text[:1]:
            body = text[1:-1]
            try:
                value = body.encode().decode("unicode_escape")
            except Exception:
                continue
            if value.startswith("__"):
                continue  # loader markers (mustContain) — never touch
            if value in keep:
                continue  # FORGE_KEEP reserved strings — never touch
            if value in ("use strict", "use asm"):
                continue  # directives lose meaning when encrypted
            prev_t = _sig_text(toks, idx, -1).rstrip()
            next_t = _sig_text(toks, idx, 1).lstrip()
            if next_t.startswith(":") and prev_t.endswith(("{", ",")):
                continue  # object key position — a call is invalid there
            if len(value) >= MIN_LEN and all(ord(ch) < 128 for ch in value):
                # splitStrings: long literals become table entries; the call
                # shape stays a plain `+` chain (cheap, AST-free).
                idxs = []
                for off in range(0, len(value), chunk_len):
                    idxs.append(len(entries))
                    entries.append(upper(_xor_hex(value[off:off + chunk_len], key),
                                         len(entries)))
                targets[idx] = idxs
    if not targets:
        return code
    live = set()
    for k2, t2 in toks:
        if k2 == "ident":
            live.add(t2)
    if table_name in live or fn_name in live:
        raise ValueError("crypt: source already uses %s/%s; rename first"
                         % (table_name, fn_name))
    seed = explicit_seed()
    order = shuffled(list(range(len(entries))), seed) if seed is not None \
        else list(range(len(entries)))
    pos = {e: p for p, e in enumerate(order)}
    table = ",".join('"' + entries[e] + '"' for e in order)
    stub = STUB_TPL.format(t=table_name, e=table, f=fn_name,
                           k="%02x" % key)
    # Pass 2: emit calls with final (shuffled) positions straight into the
    # token stream, so no text-level remapping ever touches string contents.
    out = []
    for idx, (kind, text) in enumerate(toks):
        if idx in targets:
            out.append("+".join("%s(%d)" % (fn_name, pos[e])
                                for e in targets[idx]))
        else:
            out.append(text)
    result = "".join(out)
    m = _re.match(
        r"((?:[ \t\r\n;]*(?:\"(?:use strict|use asm)\"|'(?:use strict|use asm)')[ \t]*;?)*)",
        result)
    cut = m.end(1)
    glue = "" if cut and result[cut:cut + 1] == ";" else ";"
    result = result[:cut] + glue + stub + result[cut:]
    return result
