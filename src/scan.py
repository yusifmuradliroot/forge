"""scan.py: the single shared JS scanner (strings, templates+${}, regex, comments).

All passes MUST scan through this module — three divergent reimplementations
of the same scan caused the strip/nolog/short bug family (see ai-reports).
Kinds: ident/str/regex/comment/other. Template ${} bodies are emitted as
inner tokens (recursed), so passes see template expressions as code.
"""

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
        elif (c.isalpha() or c == "_" or c == "$") and not (
                i > 0 and code[i - 1].isalnum()):
            # H4: a letter directly after digits is a numeric suffix
            # (123n, 1e5, 0xFF) -- never an identifier. Emit as opaque.
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



def build_mask(code):
    """Blank strings/regex/comments (keep newlines). Template literal chunks
    are strings (blanked); ${} bodies stay live code. Returned mask has the
    same length as code, so positions transfer 1:1. Only REAL code brackets
    remain visible -> balanced matching on the mask is sound."""
    out = []
    for kind, text in tokenize(code):
        if kind in ("str", "regex", "comment"):
            out.append("".join("\n" if ch == "\n" else " " for ch in text))
        else:
            out.append(text)
    return "".join(out)


def sig_text(toks, idx, direction):
    """Nearest significant token text in direction (-1/1), skipping comments.
    Shared by crypt + uni (single implementation, never one per pass)."""
    i = idx + direction
    while 0 <= i < len(toks):
        kind, text = toks[i]
        if kind == "comment":
            i += direction
            continue
        return text
    return ""


def template_inner_spans(toks):
    """Token-index ranges living INSIDE template literals (opening backtick
    chunk through closing one). A str token that starts like a real string
    may be a template middle -- only ranges outside spans are encryptable.
    Shared by crypt + uni (single implementation, never one per pass)."""
    spans = []
    depth = 0
    start = None
    for idx, (kind, text) in enumerate(toks):
        if kind != "str":
            continue
        if not depth and text[:1] == "`" and not (len(text) > 1 and text[-1:] == "`"):
            depth = 1
            start = idx
        elif depth and text[-1:] == "`":
            depth = 0
            spans.append((start, idx))
    return spans
