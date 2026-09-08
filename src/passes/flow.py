"""flow pass: provably-safe control-flow micro-transforms (F1).

Textual rewrites only, zero runtime cost, no scope questions:
- comma-join: consecutive plain expression statements (`a(); b();`) become
  one comma expression (`a(), b();`). Only segments with no braces (no
  objects/blocks/functions), not starting with a statement-only keyword,
  quote (directives stay separate statements) or a label (`x:`).
- negation-flip: `if (!C) {A} else {B}` -> `if (C) {B} else {A}` (braced
  bodies, statement position, `else if` chains untouched).
- while-true: `while (!0|true|1) {body}` -> `for (;;) {body}`.
Analysis runs on the scan mask (same length as code, strings/regex/comments
blanked); emission slices the ORIGINAL text. Any confusion -> skip (never
crash, never guess).
"""

import re

try:
    from scan import tokenize, build_mask
except ImportError:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from scan import tokenize, build_mask

_STMT_ONLY = re.compile(
    r"^(var|let|const|function|if|for|while|switch|return|throw|class|"
    r"import|export|debugger|do|try|with|case|default|break|continue|"
    r"else|catch|finally)\b")
_LABEL = re.compile(r"^[$A-Za-z_][\w$]*\s*:")


def _segments(mask):
    """Split mask into top-level (depth-0, newline-blind) `;`-terminated
    segments. Returns [(start, semi_pos)] with semi_pos the `;` index."""
    segs = []
    depth = 0
    start = 0
    for i, ch in enumerate(mask):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth:
                depth -= 1
        elif ch == ";" and depth == 0:
            segs.append((start, i))
            start = i + 1
    return segs


def _joinable(seg):
    t = seg.strip()
    if not t or "{" in t or "}" in t:
        return False
    if t[:1] in ("'", '"', "`"):
        return False  # directives stay separate statements
    if t.startswith("/"):
        return False  # keep regex/division statements untouched
    if _STMT_ONLY.match(t):
        return False
    if _LABEL.match(t):
        return False  # `x: ...` would be a syntax error after a comma
    return True


def _comma_join(code, mask):
    out = []
    pos = 0
    carry = None
    carry_start = 0
    last_semi = -1
    for start, semi in _segments(mask):
        seg_code = code[start:semi]
        if _joinable(mask[start:semi]):
            if carry is None:
                carry_start = start
            carry = seg_code if carry is None else carry + "," + seg_code
            last_semi = semi
        else:
            if carry is not None:
                out.append(code[pos:carry_start] + carry + ";")
                pos = last_semi + 1
                carry = None
            out.append(code[pos:semi + 1])
            pos = semi + 1
    if carry is not None:
        out.append(code[pos:carry_start] + carry + ";")
        pos = last_semi + 1
    out.append(code[pos:])
    return "".join(out)


def _match(mask, i, depth=0):
    """Match the bracket group opening at mask[i]. Returns end index excl."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    opener = mask[i]
    closer = pairs[opener]
    d = 0
    while i < len(mask):
        ch = mask[i]
        if ch == opener:
            d += 1
        elif ch == closer:
            d -= 1
            if d == 0:
                return i + 1
        i += 1
    return -1


def _skip_ws(mask, p):
    while p < len(mask) and mask[p] in " \t\n":
        p += 1
    return p


def _negation_flip(code, mask):
    out = []
    pos = 0
    for m in re.finditer(r"(?<![\w$.])(if|while)(?![\w$])", mask):
        kw = m.group(1)
        # statement-position gate (mirrors simp: start, ';', '{', '}', ':')
        q = m.start() - 1
        while q >= 0 and mask[q] in " \t\n":
            q -= 1
        if not (q < 0 or mask[q] in ";{}:"):
            continue
        p = _skip_ws(mask, m.end())
        if p >= len(mask) or mask[p] != "(":
            continue
        ce = _match(mask, p)
        if ce < 0:
            continue
        cond = mask[p + 1:ce - 1]
        q2 = _skip_ws(mask, ce)
        if q2 >= len(mask) or mask[q2] != "{":
            continue
        be = _match(mask, q2)
        if be < 0:
            continue
        if kw == "while":
            if cond.strip() in ("!0", "true", "1"):
                out.append(code[pos:m.start()])
                out.append("for(;;)" + code[q2:be])
                pos = be
            continue
        # if: needs `!C` cond + braced else (exact `else`, no `else if`)
        stripped = cond.strip()
        if not stripped.startswith("!"):
            continue
        e = _skip_ws(mask, be)
        if code[e:e + 4] != "else" or (e + 4 < len(mask) and (mask[e + 4].isalnum() or mask[e + 4] in "_$")):
            continue
        if e > 0 and (mask[e - 1].isalnum() or mask[e - 1] in "_$"):
            continue
        f = _skip_ws(mask, e + 4)
        if f >= len(mask) or mask[f] != "{":
            continue  # `else if` chains and unbraced elses stay
        fe = _match(mask, f)
        if fe < 0:
            continue
        inner = code[p + 1:ce - 1].strip()[1:].strip()
        if not inner:
            continue
        out.append(code[pos:m.start()])
        out.append("if(" + inner + ")" + code[f:fe] + "else" + code[q2:be])
        pos = fe
    out.append(code[pos:])
    return "".join(out)


def run(code: str) -> str:
    mask = build_mask(code)
    code = _comma_join(code, mask)
    for _ in range(3):  # flip strips one `!` per round; converges fast
        mask = build_mask(code)
        new = _negation_flip(code, mask)
        if new == code:
            break
        code = new
    return code
