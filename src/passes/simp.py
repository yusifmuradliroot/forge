"""simp pass: safe micro-simplifications on the token stream.

- true -> !0, false -> !1 (value positions only; o.true / {true:} kept).
  `undefined` deliberately untouched (shadowable; proving otherwise needs
  scope analysis this tool refuses to fake).
- Constant folding for pure literal binary ops: ints (+ - *) within the safe
  integer range (bigger would round differently than JS doubles), and simple
  string concatenation ("a"+"b", no escapes inside). Division/modulo skipped.
- Dead branches on literal conditions: if(true){A}->A, if(false){A}else{B}->B,
  if(false){A} dropped, while(false){...} dropped. Braced branches only.
Runs to fixpoint (max 5 rounds) so nesting collapses too.
"""

import bisect

from scan import tokenize

_MAX_SAFE = 9007199254740991


def _offsets(toks):
    """Char offset of each token start (tokens tile the input exactly)."""
    offs = []
    pos = 0
    for _, text in toks:
        offs.append(pos)
        pos += len(text)
    return offs


def _sig(toks, idx, direction):
    i = idx + direction
    while 0 <= i < len(toks):
        if toks[i][0] != "comment":
            return toks[i][1]
        i += direction
    return ""


def _is_code_pos(toks, idx):
    prev = _sig(toks, idx, -1).rstrip()
    nxt = _sig(toks, idx, 1).lstrip()
    if prev.endswith("."):
        return False
    if nxt.startswith(":"):
        return False
    return True


def run(code: str) -> str:
    import re
    # Pass 1: true/false (token-local, no structure needed).
    toks = tokenize(code)
    out = []
    for idx, (kind, text) in enumerate(toks):
        if kind == "ident" and text in ("true", "false") and _is_code_pos(toks, idx):
            out.append("!0" if text == "true" else "!1")
        else:
            out.append(text)
    code = "".join(out)
    # Pass 2+3: structural folds to fixpoint (bounded).
    for _ in range(5):
        new = _fold_once(code)
        if new == code:
            break
        code = new
    return code


_NUMOP = None


def _fold_once(code):
    import re
    toks = tokenize(code)
    n = len(toks)

    def is_other(t, s=None):
        return t[0] == "other" and (s is None or s in t[1])

    # Collect edits as (char_start, char_end, replacement).
    offs = _offsets(toks)
    edits = []
    i = 0
    while i < n:
        kind, text = toks[i]
        # --- number op number inside ONE other-token (no idents/strings span it) ---
        if kind == "other":
            m = re.search(r"(?<![\w$.])(-?\d+)\s*([+*\-])\s*(-?\d+)(?![\w$.])", text)
            if m:
                folded = None
                try:
                    a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
                    if abs(a) <= _MAX_SAFE and abs(b) <= _MAX_SAFE:
                        r = a + b if op == "+" else (a - b if op == "-" else a * b)
                        if abs(r) <= _MAX_SAFE:
                            folded = text[:m.start()] + str(r) + text[m.end():]
                except ValueError:
                    folded = None
                if folded is not None:
                    edits.append((offs[i], offs[i] + len(text), folded))
                    i += 1
                    continue
        # --- "lit" + "lit" across str/other/str ---
        if kind == "str" and len(text) >= 2 and text[0] in ("'", '"') and text[-1:] == text[0]:
            j = i + 1
            while j < n and toks[j][0] == "comment":
                j += 1
            if j < n and toks[j][0] == "other" and toks[j][1].strip() == "+":
                k = j + 1
                while k < n and toks[k][0] == "comment":
                    k += 1
                if k < n and toks[k][0] == "str":
                    t2 = toks[k][1]
                    if len(t2) >= 2 and t2[0] == text[0] and t2[-1:] == text[0]:
                        b1, b2 = text[1:-1], t2[1:-1]
                        if "\\" not in b1 and "\\" not in b2:
                            edits.append((offs[i], offs[k] + len(t2), text[0] + b1 + b2 + text[0]))
                            i = k + 1
                            continue
        # --- dead branches: if/while with literal cond, braced bodies ---
        if kind == "ident" and text in ("if", "while"):
            res = _dead_branch(toks, i)
            if res:
                edits.append(res)
                # skip past consumed region (recompute index from char offset)
                ce = res[1]
                while i < n and offs[i] < ce:
                    i += 1
                continue
        i += 1
    if not edits:
        return code
    # apply non-overlapping left-to-right
    out = []
    pos = 0
    for a, b, rep in sorted(edits):
        if a < pos:
            continue
        out.append(code[pos:a])
        out.append(rep)
        pos = b
    out.append(code[pos:])
    return "".join(out)


def _prev_word_at(chars, i):
    while i >= 0 and chars[i] in " \t\n":
        i -= 1
    e = i + 1
    while i >= 0 and (chars[i].isalnum() or chars[i] in "_$"):
        i -= 1
    return chars[i + 1:e]


def _span_at(toks, offs, pos):
    """Balance-match the group opening exactly at char offset pos.
    Returns (inner_text, end_char_excl) or None. Strings/regex/comments are
    opaque (token-aware), so brackets inside them never count."""
    import bisect
    n = len(toks)
    chars = "".join(t[1] for t in toks)
    N = len(chars)
    if pos >= N or chars[pos] not in "([{":
        return None
    depth = 0
    started = False
    parts = []
    j = max(0, min(bisect.bisect_right(offs, pos) - 1, n - 1))
    k = pos - offs[j]
    while j < n:
        kind, text = toks[j]
        if kind in ("str", "regex", "comment"):
            if started:
                parts.append(text)
            j += 1
            k = 0
            continue
        while k < len(text):
            ch = text[k]
            if not started:
                if ch in " \t\n":
                    k += 1
                    continue
                if ch not in "([{":
                    return None
                started = True
                depth = 1
                k += 1
                continue
            if ch in "([{":
                depth += 1
                parts.append(ch)
            elif ch in ")]}":
                depth -= 1
                if depth == 0:
                    return ("".join(parts), offs[j] + k + 1)
                parts.append(ch)
            else:
                parts.append(ch)
            k += 1
        j += 1
        k = 0
    return None


def _dead_branch(toks, i):
    """toks[i] is ident if/while. Returns (char_start, char_end, replacement)
    or None. Only unambiguous STATEMENT positions: the keyword must follow
    start-of-input, ';', '{', '}' or ':' (blocks, cases, sequence starts).
    Anything else (notably `else if` chains and `{if(){}}` object/class
    methods literally named if/while -- legal but essentially never written)
    is left alone."""
    word = toks[i][1]
    n = len(toks)
    offs = _offsets(toks)
    chars = "".join(t[1] for t in toks)
    N = len(chars)

    def skip(p):
        while p < N:
            if chars[p] in " \t\n":
                p += 1
                continue
            ti = max(0, min(bisect.bisect_right(offs, p) - 1, n - 1))
            if toks[ti][0] == "comment" and p == offs[ti]:
                p += len(toks[ti][1])
                continue
            break
        return p

    # statement-position gate
    q = offs[i] - 1
    while q >= 0 and chars[q] in " \t\n":
        q -= 1
    if not (q < 0 or chars[q] in ";{ }:"):
        # covers: else-if chains, method names, property access, calls
        return None
    if q >= 0 and chars[q] == "{":
        # `{ if(..){..} }` is a block, but looks identical to an object
        # holding a method literally named if/while (legal, ~never written).
        # Decide by what precedes the brace: statement/block slots are blocks,
        # value slots are objects (skip), `case`/`default` bodies are blocks.
        qq = q - 1
        while qq >= 0 and chars[qq] in " \t\n":
            qq -= 1
        is_block = True
        if qq < 0 or chars[qq] in ";}{)":
            is_block = True
        elif chars[qq] == ":":
            w = _prev_word_at(chars, qq - 1)
            is_block = w in ("case", "default")
        elif chars[qq] == ">" and qq > 0 and chars[qq - 1] == "=":
            is_block = True  # => body (concise object needs parens)
        else:
            ww = _prev_word_at(chars, qq)
            is_block = ww in ("else", "do", "try", "finally", "return")
        if not is_block:
            return None
    p = skip(offs[i] + len(word))
    if p >= N or chars[p] != "(":
        return None
    sp = _span_at(toks, offs, p)
    if not sp:
        return None
    cond, cend = sp
    cond_v = cond.strip()
    q = skip(cend)
    if q >= N or chars[q] != "{":
        return None
    bsp = _span_at(toks, offs, q)
    if not bsp:
        return None
    body, bend = bsp
    cstart = offs[i]
    if word == "while":
        if cond_v in ("false", "!1"):
            return (cstart, bend, "")
        return None
    # optional else (exact ident at exact pos -- `else if` handled by gate)
    e = skip(bend)
    ei = max(0, min(bisect.bisect_right(offs, e) - 1, n - 1))
    has_else = (toks[ei][0] == "ident" and toks[ei][1] == "else" and e == offs[ei])
    if cond_v in ("true", "!0"):
        if not has_else:
            return (cstart, bend, "{" + body + "}")
        f = skip(e + 4)
        if f >= N or chars[f] != "{":
            return None
        fsp = _span_at(toks, offs, f)
        if not fsp:
            return None
        _, fend = fsp
        return (cstart, fend, "{" + body + "}")
    if cond_v in ("false", "!1"):
        if not has_else:
            return (cstart, bend, "")
        f = skip(e + 4)
        if f >= N or chars[f] != "{":
            return None
        fsp = _span_at(toks, offs, f)
        if not fsp:
            return None
        ebody, fend = fsp
        return (cstart, fend, "{" + ebody + "}")
    return None
