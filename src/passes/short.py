"""short pass: rename single-declaration locals to short names.

Conservative by design — a name is renamed ONLY if ALL hold:
- declared exactly once in the file (var/let/const/function/param/catch),
- never used as a property (obj.NAME), object key (NAME:), or after `new`,
- not a known global / reserved word. (GLOBALS also covers cross-file
  contract names like ForgeScript: the runner is embedded in one file and
  called by name from separately-forged files, so renaming it breaks them.)
Everything else is left untouched. Strings, comments, regex, templates are opaque.
"""

from scan import tokenize, build_mask
from seed import explicit_seed, shuffled
from poison import find_poison


import os
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
ForgeScript
Function eval isNaN isFinite parseInt parseFloat encodeURI decodeURI
encodeURIComponent decodeURIComponent escape unescape
""".split())



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


def _is_clean(name, positions, toks):
    """No property/key/new occurrence anywhere (global guard). positions are
    the token indices holding `name` (pre-grouped: O(occurrences), not O(file))."""
    for kk in positions:
        if _prev_other_behind(toks, kk) == ".":
            return False
        if _next_other_ahead(toks, kk) == ":":
            return False
        if _prev_ident(toks, kk) == "new":
            return False
    return True


_GUARD_WORDS = re.compile(r"(?<![\w$])(function|eval|with|arguments)(?![\w$])")


def _func_spans(mask):
    """(start, body_open, end) per `function` construct incl. params.
    Matching runs on the mask (only real brackets visible)."""
    spans = []
    for m in re.finditer(r"(?<![\w$.])function(?![\w$])", mask):
        p = mask.find("(", m.end())
        if p < 0:
            continue
        if re.fullmatch(r"[\s\w$*]*", mask[m.end():p]) is None:
            continue
        d, i = 0, p
        while i < len(mask):
            if mask[i] == "(":
                d += 1
            elif mask[i] == ")":
                d -= 1
                if d == 0:
                    break
            i += 1
        else:
            continue
        q = i + 1
        while q < len(mask) and mask[q] in " \t\n":
            q += 1
        if q >= len(mask) or mask[q] != "{":
            continue
        d, j = 0, q
        while j < len(mask):
            if mask[j] == "{":
                d += 1
            elif mask[j] == "}":
                d -= 1
                if d == 0:
                    break
            j += 1
        else:
            continue
        spans.append((m.start(), q, j + 1))
    return spans


def _scope_shadows(code, mask, toks, decls, param_sites, poisoned, taken, gen):
    """N1 prototype (FORGE_SCOPE=1 only): rename shadowed function params.

    A name declared exactly twice, both as `function` params, gets a fresh
    name inside the smallest function span holding exactly one site — when
    that span holds no nested function/arrow/eval/with/arguments (any of
    which could observe the outer binding). Default builds never run this.
    """
    offs = []
    pos = 0
    for _, text in toks:
        offs.append(pos)
        pos += len(text)
    idents = [(k, t) for k, (kind, t) in enumerate(toks) if kind == "ident"]
    by_name = {}
    for kk, tt in idents:
        by_name.setdefault(tt, []).append(kk)
    spans = sorted(_func_spans(mask), key=lambda s: s[2] - s[0])
    rules = []
    for name, sites in decls.items():
        if len(sites) != 2:
            continue
        if name in RESERVED or name in GLOBALS or name in poisoned:
            continue
        if not all(s in param_sites for s in sites):
            continue
        if not _is_clean(name, by_name.get(name, []), toks):
            continue
        so = sorted(offs[s] for s in sites)
        for (a, q, b) in spans:
            if len([x for x in so if a <= x < b]) != 1:
                continue
            # guards run on the BODY only (the span head trivially holds
            # `function` itself)
            if _GUARD_WORDS.search(mask[q:b]) or "=>" in mask[q:b]:
                continue
            while True:
                cand = next(gen)
                if cand not in taken and cand not in RESERVED and cand not in GLOBALS:
                    break
            taken.add(cand)
            rules.append((name, cand, a, b))
            break
    return rules, offs


def run(code: str) -> str:
    toks = tokenize(code)
    idents = [(k, t) for k, (kind, t) in enumerate(toks) if kind == "ident"]

    decls = {}
    param_sites = set()
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
    def _skip_gap(k):
        while k < len(toks) and (toks[k][0] == "comment" or (
                toks[k][0] == "other" and not toks[k][1].strip())):
            k += 1
        return k

    ti = 0
    while ti < len(toks):
        kind, text = toks[ti]
        if kind == "ident" and text == "function":
            # find '(' after optional `*` and optional name
            tj = _skip_gap(ti + 1)
            if tj < len(toks) and toks[tj][0] == "other" and toks[tj][1].strip() == "*":
                tj = _skip_gap(tj + 1)
            if tj < len(toks) and toks[tj][0] == "ident":
                tj = _skip_gap(tj + 1)
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
                            param_sites.add(kk)
                            break
        ti += 1

    try:
        poisoned = find_poison(code)
    except Exception:
        poisoned = set()
    by_name = {}
    for kk, tt in idents:
        by_name.setdefault(tt, []).append(kk)
    candidates = {}
    for name, sites in decls.items():
        if len(sites) != 1:
            continue
        if name in RESERVED or name in GLOBALS or len(name) < 1:
            continue
        if name in poisoned:
            continue
        if _is_clean(name, by_name.get(name, []), toks):
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

    order = sorted(candidates)
    seed = explicit_seed()
    if seed is not None:
        # Seeded builds shuffle assignment order (same input, different
        # renames per FORGE_SEED). Default path stays sorted (diffable).
        order = shuffled(order, seed)
    mapping = {}
    taken = {t for _, t in idents}
    gen = name_gen()
    for name in order:
        while True:
            cand = next(gen)
            if cand not in taken and cand not in RESERVED and cand not in GLOBALS:
                break
        mapping[name] = cand
        taken.add(cand)

    span_rules, tok_offs = ([], None)
    if os.environ.get("FORGE_SCOPE", ""):
        # N1 prototype: shadowed params renamed inside their own span only.
        span_rules, tok_offs = _scope_shadows(code, build_mask(code), toks,
                                              decls, param_sites, poisoned,
                                              taken, gen)

    out = []
    for ti, (kind, text) in enumerate(toks):
        if kind == "ident":
            if text in mapping:
                out.append(mapping[text])
                continue
            if tok_offs is not None:
                hit = None
                for (nm, nn, a, b) in span_rules:
                    if text == nm and a <= tok_offs[ti] < b:
                        hit = nn
                        break
                if hit is not None:
                    out.append(hit)
                    continue
        out.append(text)
    return "".join(out)
