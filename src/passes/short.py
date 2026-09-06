"""short pass: rename single-declaration locals to short names.

Conservative by design — a name is renamed ONLY if ALL hold:
- declared exactly once in the file (var/let/const/function/param/catch),
- never used as a property (obj.NAME), object key (NAME:), or after `new`,
- not a known global / reserved word.
Everything else is left untouched. Strings, comments, regex, templates are opaque.
"""

import re

RESERVED = set("""
await break case catch class const continue debugger default delete do else enum
export extends false finally for function if implements import in instanceof
interface let new null package private protected public return static super
switch this throw true try typeof var void while with yield undefined NaN Infinity
arguments eval
""".split())

GLOBALS = set("""
window document navigator location history screen console Math JSON Array Object
String Number Boolean RegExp Date Error Promise Symbol Map Set WeakMap WeakSet
Int8Array Uint8Array Uint8ClampedArray Int16Array Uint16Array Int32Array Uint32Array
Float32Array Float64Array ArrayBuffer DataView Blob URL URLSearchParams FormData
XMLHttpRequest WebSocket Worker setTimeout clearTimeout setInterval clearInterval
setImmediate clearImmediate requestAnimationFrame cancelAnimationFrame fetch
localStorage sessionStorage crypto performance alert confirm prompt open close
unsafeWindow GM_getValue GM_setValue GM_xmlhttpRequest GM_info GM
Function eval isNaN isFinite parseInt parseFloat encodeURI decodeURI
encodeURIComponent decodeURIComponent escape unescape
""".split())


def tokenize(code):
    """Yield (kind, text) with kind in ident/str/regex/comment/other."""
    toks = []
    i, n = 0, len(code)
    buf = []
    def flush():
        if buf:
            toks.append(("other", "".join(buf)))
            del buf[:]
    while i < n:
        c = code[i]
        nxt = code[i + 1] if i + 1 < n else ""
        if c in ("'", '"'):
            flush()
            j = i + 1
            while j < n:
                if code[j] == "\\":
                    j += 2
                    continue
                if code[j] == c:
                    j += 1
                    break
                j += 1
            toks.append(("str", code[i:j]))
            i = j
        elif c == "`":
            flush()
            j = i + 1
            seg_start = i
            closed = False
            while j < n:
                if code[j] == "\\":
                    j += 2
                    continue
                if code[j] == "`":
                    toks.append(("str", code[seg_start:j + 1]))
                    j += 1
                    closed = True
                    break
                if code[j] == "$" and j + 1 < n and code[j + 1] == "{":
                    toks.append(("str", code[seg_start:j]))
                    k = j + 2
                    d = 1
                    while k < n and d:
                        if code[k] == "\\":
                            k += 2
                            continue
                        if code[k] in ("'", '"'):
                            q = code[k]
                            k += 1
                            while k < n and code[k] != q:
                                k += 2 if code[k] == "\\" else 1
                            k += 1
                            continue
                        if code[k] == "`":
                            # nested template inside ${}: skip over it silently.
                            # (The recursive tokenize() below re-processes this span;
                            # emitting here would duplicate tokens.)
                            m = k + 1
                            tdepth = 0
                            while m < n:
                                if code[m] == "\\":
                                    m += 2
                                    continue
                                if code[m] == "`" and tdepth == 0:
                                    m += 1
                                    break
                                if code[m] == "$" and m + 1 < n and code[m + 1] == "{":
                                    tdepth += 1
                                    m += 2
                                    continue
                                if code[m] == "}" and tdepth > 0:
                                    tdepth -= 1
                                m += 1
                            k = m
                            continue
                        if code[k] == "{":
                            d += 1
                        elif code[k] == "}":
                            d -= 1
                        k += 1
                    toks.append(("other", "${"))
                    for t in tokenize(code[j + 2:k - 1]):
                        toks.append(t)
                    toks.append(("other", "}"))
                    j = k
                    seg_start = k
                    continue
                j += 1
            if not closed:
                toks.append(("str", code[seg_start:j]))
            i = j
        elif c == "/" and nxt == "/":
            flush()
            j = code.find("\n", i)
            j = n if j == -1 else j
            toks.append(("comment", code[i:j]))
            i = j
        elif c == "/" and nxt == "*":
            flush()
            j = code.find("*/", i + 2)
            j = n if j == -1 else j + 2
            toks.append(("comment", code[i:j]))
            i = j
        elif c == "/" and _regex_allowed(toks, buf):
            flush()
            j = i + 1
            in_class = False
            while j < n:
                if code[j] == "\\":
                    j += 2
                    continue
                if code[j] == "[":
                    in_class = True
                elif code[j] == "]":
                    in_class = False
                elif code[j] == "/" and not in_class:
                    j += 1
                    while j < n and code[j] in "dgimsuvy":
                        j += 1
                    break
                elif code[j] == "\n":
                    break
                j += 1
            toks.append(("regex", code[i:j]))
            i = j
        elif c.isalpha() or c == "_" or c == "$":
            flush()
            j = i + 1
            while j < n and (code[j].isalnum() or code[j] in "_$"):
                j += 1
            toks.append(("ident", code[i:j]))
            i = j
        else:
            buf.append(c)
            i += 1
    flush()
    return toks


KEYWORDS_BEFORE_REGEX = ("return", "typeof", "in", "of", "new", "delete",
                             "void", "throw", "case", "do", "else", "yield", "await")


def _regex_allowed(toks, buf=None):
    # NOTE: the pending buf (unflushed "other" chars) must be consulted FIRST:
    # e.g. in `replace(/x/g)` the "(" sits in buf, not in toks yet.
    if buf:
        s = "".join(buf).rstrip()
        if s:
            ch = s[-1]
            if ch == ")" or ch == "]":
                return False
            if ch.isalnum() or ch in "_$":
                j = len(s) - 1
                while j >= 0 and (s[j].isalnum() or s[j] in "_$"):
                    j -= 1
                return s[j + 1:] in KEYWORDS_BEFORE_REGEX
            return True
    for kind, text in reversed(toks):
        if kind in ("str", "regex", "comment"):
            return False
        if kind == "ident":
            return text in KEYWORDS_BEFORE_REGEX
        if kind == "other":
            s = text.rstrip()
            if not s:
                continue
            ch = s[-1]
            if ch.isalnum() or ch in "_$)]}'\"`":
                return False
            return True
    return True


def _prev_ident(toks, idx):
    for k in range(idx - 1, -1, -1):
        if toks[k][0] == "ident":
            return toks[k][1]
    return None


def _next_other_ahead(toks, idx):
    for k in range(idx + 1, len(toks)):
        if toks[k][0] == "ident":
            return None
        if toks[k][0] == "other":
            s = toks[k][1].lstrip()
            if s:
                return s[0]
    return None


def _prev_other_behind(toks, idx):
    for k in range(idx - 1, -1, -1):
        if toks[k][0] == "ident":
            return None
        if toks[k][0] == "other":
            s = toks[k][1].rstrip()
            if s:
                return s[-1]
    return None


def _split_params(text):
    parts, depth, cur = [], 0, ""
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    names = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if "=" in p:
            p = p.split("=", 1)[0].strip()
        m = re.match(r"^(?:\.\.\.)?([A-Za-z_$][\w$]*)", p)
        if m:
            names.append(m.group(1))
    return names


def run(code: str) -> str:
    toks = tokenize(code)
    idents = [(k, t) for k, (kind, t) in enumerate(toks) if kind == "ident"]

    decls = {}
    i = 0
    while i < len(idents):
        k, name = idents[i]
        if name in ("var", "let", "const"):
            j = i + 1
            while j < len(idents):
                k2, nm = idents[j]
                if nm in RESERVED or nm in GLOBALS:
                    break
                if _prev_other_behind(toks, k2) == "." or _next_other_ahead(toks, k2) == ":":
                    j += 1
                    continue
                decls.setdefault(nm, []).append(k2)
                nxt = _next_other_ahead(toks, k2)
                if nxt == "=":
                    pass
                if nxt == ",":
                    j += 1
                    continue
                break
        elif name == "function":
            if i + 1 < len(idents):
                k2, nm = idents[i + 1]
                if nm not in RESERVED and _prev_other_behind(toks, k2) != ".":
                    decls.setdefault(nm, []).append(k2)
        elif name == "catch":
            if i + 1 < len(idents):
                k2, nm = idents[i + 1]
                if re.fullmatch(r"[A-Za-z_$][\w$]*", nm or ""):
                    decls.setdefault(nm, []).append(k2)
        i += 1

    # params via paren scan on token stream
    ti = 0
    while ti < len(toks):
        kind, text = toks[ti]
        if kind == "ident" and text == "function":
            # find '(' after optional name
            tj = ti + 1
            while tj < len(toks) and toks[tj][0] in ("comment",) :
                tj += 1
            if tj < len(toks) and toks[tj][0] == "ident":
                tj += 1
            depth_text = ""
            if tj < len(toks) and toks[tj][0] == "other" and "(" in toks[tj][1]:
                # collect balanced parens across 'other' tokens (idents inside handled separately)
                par = toks[tj][1][toks[tj][1].index("("):]
                depth = par.count("(") - par.count(")")
                pieces = [par]
                tk = tj + 1
                while depth > 0 and tk < len(toks):
                    t2 = toks[tk][1] if toks[tk][0] in ("other", "ident") else ""
                    depth += t2.count("(") - t2.count(")")
                    pieces.append(t2)
                    tk += 1
                inner = "".join(pieces)
                inner = inner[1:inner.rfind(")")]
                for pn in _split_params(inner):
                    # find the ident token equal to pn inside range [tj, tk)
                    for kk in range(tj, min(tk, len(toks))):
                        if toks[kk][0] == "ident" and toks[kk][1] == pn:
                            # ensure it is a param position (not nested arrow body): accept first occurrence
                            decls.setdefault(pn, []).append(kk)
                            break
        ti += 1

    candidates = {}
    for name, sites in decls.items():
        if len(sites) != 1:
            continue
        if name in RESERVED or name in GLOBALS or len(name) < 1:
            continue
        bad = False
        for kk, tt in idents:
            if tt != name:
                continue
            if _prev_other_behind(toks, kk) == ".":
                bad = True
                break
            if _next_other_ahead(toks, kk) == ":":
                bad = True
                break
            if _prev_ident(toks, kk) == "new":
                bad = True
                break
        if not bad:
            candidates[name] = sites[0]

    # short names a..z, aa..az, ... generated lazily, skipping taken/reserved
    def name_gen():
        n = 0
        while True:
            s = ""
            m = n
            while True:
                s = chr(97 + m % 26) + s
                m = m // 26 - 1
                if m < 0:
                    break
            n += 1
            yield s

    mapping = {}
    taken = {t for _, t in idents}
    gen = name_gen()
    for name in sorted(candidates):
        while True:
            cand = next(gen)
            if cand not in taken and cand not in RESERVED:
                break
        mapping[name] = cand
        taken.add(cand)

    out = []
    for kind, text in toks:
        if kind == "ident" and text in mapping:
            out.append(mapping[text])
        else:
            out.append(text)
    return "".join(out)
