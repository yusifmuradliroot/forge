"""poison.py: names short.py must NEVER rename (property/pattern positions).

 Conservative by design: over-poisoning only costs bytes, under-poisoning
 corrupts. Operates on the scan mask (strings/regex/comments blanked), so all
 visible brackets are real and balanced matching is sound.
"""

import re

_IDENT_RE = re.compile(r"[A-Za-z_$][\w$]*")
_PAIRS = {"(": ")", "[": "]", "{": "}"}
_CLOSE = {")": "(", "]": "[", "}": "{"}


def _skip_balanced(mask, i):
    """i at an opener; return index just past its match (or len)."""
    depth = 0
    n = len(mask)
    while i < n:
        ch = mask[i]
        if ch in _PAIRS:
            depth += 1
        elif ch in _CLOSE:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def _match_backward(mask, i):
    """i at a closer; return index of its opener (or -1)."""
    depth = 0
    while i >= 0:
        ch = mask[i]
        if ch in _CLOSE:
            depth += 1
        elif ch in _PAIRS:
            depth -= 1
            if depth == 0:
                return i
        i -= 1
    return -1


def _poison_span(mask, a, b, poison):
    for m in _IDENT_RE.finditer(mask, a, b):
        poison.add(m.group(0))


def _prev_sig(mask, i):
    while i >= 0 and mask[i] in " \t\n":
        i -= 1
    return mask[i] if i >= 0 else ""


def _prev_word(mask, i):
    k = i
    while k >= 0 and mask[k] in " \t\n":
        k -= 1
    e = k + 1
    while k >= 0 and (mask[k].isalnum() or mask[k] in "_$"):
        k -= 1
    return mask[k + 1:e]


def _is_decl_keyword(mask, i, word):
    """True if word at i is a real declaration keyword (not property/key)."""
    prev = _prev_sig(mask, i - 1)
    if prev in (".",):
        return False
    if prev and (prev.isalnum() or prev in "_$"):
        return False
    j = i + len(word)
    if j < len(mask) and (mask[j].isalnum() or mask[j] in "_$"):
        return False
    return True


def _parse_declarators(mask, i, poison, terms, for_head=False):
    """i at first char after var/let/const. Walk declarators; poison
    binding-pattern idents. `terms`: extra words that end the list (of/in).
    for_head: also stop (without consuming) at ';' and ')'."""
    n = len(mask)
    while i < n:
        while i < n and mask[i] in " \t\n":
            i += 1
        if i >= n:
            return i
        if mask[i] == ";":
            return i if for_head else i + 1
        if for_head and mask[i] == ")":
            return i
        # terminator words (of/in) at depth 0
        w = _IDENT_RE.match(mask, i)
        if w and w.group(0) in terms:
            return i
        # pattern position?
        if mask[i] in "{[":
            j = _skip_balanced(mask, i)
            _poison_span(mask, i, j, poison)
            i = j
            while i < n and mask[i] in " \t\n":
                i += 1
            if i < n and mask[i] == "=":
                i = _skip_initializer(mask, i + 1)
            elif i < n and mask[i] == ",":
                i += 1
                continue
            return i
        # plain name: skip it
        if w:
            i = w.end()
        else:
            i += 1
        while i < n and mask[i] in " \t\n":
            i += 1
        if i < n and mask[i] == "=":
            i = _skip_initializer(mask, i + 1)
        while i < n and mask[i] in " \t\n":
            i += 1
        if i < n and mask[i] == ",":
            i += 1
            continue
        return i
    return i


def _skip_initializer(mask, i):
    """Skip one comma-terminated expression: balanced brackets + function
    bodies are real on the mask, so depth tracking suffices. Stops after the
    top-level ',' or ';' (consumes it) or at of/in/close."""
    n = len(mask)
    depth = 0
    while i < n:
        ch = mask[i]
        if ch in _PAIRS:
            # arrow body or block? still balanced -> generic depth is fine
            depth += 1
        elif ch in _CLOSE:
            if depth == 0:
                return i
            depth -= 1
        elif depth == 0 and ch in ",;":
            return i + 1
        i += 1
    return i


def find_poison(code):
    """Full poison pass over source. Returns a set of names."""
    from scan import build_mask  # local import: dual package layouts
    mask = build_mask(code)
    poison = set()
    n = len(mask)
    i = 0
    while i < n:
        ch = mask[i]
        if ch.isalpha() or ch in "_$":
            m = _IDENT_RE.match(mask, i)
            word = m.group(0)
            if word in ("var", "let", "const") and _is_decl_keyword(mask, i, word):
                i = _parse_declarators(mask, m.end(), poison, ())
                continue
            if word == "for" and _prev_sig(mask, i - 1) not in (".",) and not _prev_sig(mask, i - 1).isalnum():
                j = m.end()
                while j < n and mask[j] in " \t\n":
                    j += 1
                if j < n and mask[j] == "(":
                    # for-head: var-decl or plain; only decls matter
                    k = j + 1
                    while k < n and mask[k] in " \t\n":
                        k += 1
                    w2 = _IDENT_RE.match(mask, k)
                    if w2 and w2.group(0) in ("var", "let", "const"):
                        i = _parse_declarators(mask, w2.end(), poison,
                                               ("of", "in"), for_head=True)
                        continue
                    i = j + 1
                    continue
            if word == "export" and _is_decl_keyword(mask, i, word):
                j = m.end()
                while j < n and mask[j] in " \t\n":
                    j += 1
                w2 = _IDENT_RE.match(mask, j)
                if w2 and w2.group(0) == "default":
                    j = w2.end()
                    while j < n and mask[j] in " \t\n":
                        j += 1
                    w3 = _IDENT_RE.match(mask, j)
                    if w3 and w3.group(0) in ("function", "class"):
                        j = w3.end()
                        while j < n and mask[j] in " \t\n":
                            j += 1
                        w4 = _IDENT_RE.match(mask, j)
                        if w4:
                            poison.add(w4.group(0))
                            i = w4.end()
                            continue
                    i = j
                    continue
                if w2 and w2.group(0) in ("function", "class"):
                    j = w2.end()
                    while j < n and mask[j] in " \t\n":
                        j += 1
                    if j < n and mask[j] == "*":
                        j += 1
                        while j < n and mask[j] in " \t\n":
                            j += 1
                    w3 = _IDENT_RE.match(mask, j)
                    if w3:
                        poison.add(w3.group(0))
                        i = w3.end()
                        continue
                    i = j
                    continue
                if w2 and w2.group(0) in ("var", "let", "const"):
                    e = _parse_declarators(mask, w2.end(), set(), ())
                    _poison_span(mask, w2.end(), e, poison)
                    i = e
                    continue
                if j < n and mask[j] == "{":
                    e = _skip_balanced(mask, j)
                    _poison_span(mask, j, e, poison)
                    i = e
                    continue
            if word == "catch":
                j = m.end()
                while j < n and mask[j] in " \t\n":
                    j += 1
                if j < n and mask[j] == "(":
                    k = j + 1
                    while k < n and mask[k] in " \t\n":
                        k += 1
                    if k < n and mask[k] in "{[":
                        e = _skip_balanced(mask, k)
                        _poison_span(mask, k, e, poison)
                        i = e
                        continue
                    i = j + 1
                    continue
            if word == "function":
                j = m.end()
                while j < n and mask[j] in " \t\n":
                    j += 1
                if j < n and mask[j] == "*":
                    j += 1
                    while j < n and mask[j] in " \t\n":
                        j += 1
                if j < n and mask[j] not in "(;," and (mask[j].isalpha() or mask[j] in "_$"):
                    w2 = _IDENT_RE.match(mask, j)
                    if w2:
                        j = w2.end()
                while j < n and mask[j] in " \t\n":
                    j += 1
                if j < n and mask[j] == "(":
                    e = _skip_balanced(mask, j)
                    _poison_params(mask, j, e, poison)
                    i = e
                    continue
            i = m.end()
            continue
        if ch == ")" :
            # possible arrow params: ') =>'
            j = i + 1
            while j < n and mask[j] in " \t\n":
                j += 1
            if mask[j:j + 2] == "=>":
                o = _match_backward(mask, i)
                if o >= 0:
                    _poison_params(mask, o, i + 1, poison)
            i += 1
            continue
        i += 1
    # object key/shorthand/method positions (H3)
    _poison_object_keys(mask, poison)
    return poison


def _poison_params(mask, a, b, poison):
    """Poison {...}/[...] spans inside a param list (a,b) (open..close+1)."""
    i = a
    while i < b:
        if mask[i] in "{[":
            j = _skip_balanced(mask, i)
            _poison_span(mask, i, j, poison)
            i = j
        else:
            i += 1


_BLOCK_WORDS = {"if", "for", "while", "with", "catch", "else", "do", "try",
                "finally", "function"}


def _classify_brace(mask, i):
    """Classify '{' at i (never a '${'): 'obj' or 'block'. Ambiguous -> 'obj'
    (safe direction: over-poisoning only costs bytes)."""
    c = _prev_sig(mask, i - 1)
    if c in "=([,:?!~+-*/%&|^":
        return "obj"
    if c == ")":
        return "block"
    if c == "}":
        return "block"
    if c == "{":
        return "block"
    if c == ">":
        # '=>' block body (arrow concise object needs parens, handled above)
        return "block"
    if c.isalnum() or c in "_$":
        w = _prev_word(mask, i - 1)
        if w in _BLOCK_WORDS or w in ("return", "typeof", "new", "delete",
                                      "void", "throw", "case", "yield",
                                      "await", "default", "in", "of",
                                      "instanceof"):
            # 'return {' / 'case 1: {'-ish: return-object is common and safe;
            # keyword bodies (else/do/try) are blocks.
            if w in ("else", "do", "try", "finally"):
                return "block"
            return "obj"
        return "obj"
    return "obj"


def _poison_object_keys(mask, poison):
    """Inside obj-classified {} spans, poison key/shorthand/method idents."""
    n = len(mask)
    i = 0
    while i < n:
        if mask[i] == "{" and not (i > 0 and mask[i - 1] == "$"):
            if _classify_brace(mask, i) == "obj":
                j = _skip_balanced(mask, i)
                _poison_keys_in_span(mask, i, j, poison)
                i = j
                continue
        i += 1


def _poison_keys_in_span(mask, a, b, poison):
    i = a + 1
    while i < b:
        ch = mask[i]
        if ch.isalpha() or ch in "_$":
            m = _IDENT_RE.match(mask, i)
            word = m.group(0)
            # find next significant char
            j = m.end()
            while j < b and mask[j] in " \t\n":
                j += 1
            nxt = mask[j] if j < b else ""
            # find prev significant char
            k = i - 1
            while k > a and mask[k] in " \t\n":
                k -= 1
            prv = mask[k] if k > a else ""
            prev_word = ""
            if prv.isalnum() or prv in "_$":
                e = k + 1
                while k > a and (mask[k].isalnum() or mask[k] in "_$"):
                    k -= 1
                prev_word = mask[k + 1:e]
            if nxt == ":" and prv in "{,":
                poison.add(word)  # {key: ..} / {.., key: ..}
            elif prv in "{," and nxt in "},":
                poison.add(word)  # shorthand {key} / {key, ..}
            elif prv in "{," and nxt == "(":
                poison.add(word)  # method {m( .. )}
            elif prv in "{," and nxt == "=":
                poison.add(word)  # class field {x = 1}: the NAME must not change
            elif prv == "*" and nxt == "(":
                poison.add(word)  # generator method {*g( .. )}
            elif prev_word in ("async", "get", "set", "static") and nxt == "(":
                poison.add(word)  # async m() / get x() / static m()
            # recurse into nested value spans? nested braces handled by outer
            # loop independently; skip balanced groups to stay linear-ish
            i = m.end()
            continue
        if ch in "{[":
            i = _skip_balanced(mask, i)
            continue
        i += 1
