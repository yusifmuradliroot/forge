"""nolog pass: remove console.* call statements via the shared scanner.
Strings/regex/comments/template-chunks are masked (L1: regex content immune);
${} expressions stay live code. Lines carrying keep-log (leading or trailing,
line or block comments) survive. Stripped calls leave ';' (dangling-if safe).
Expressions (x = console.log(..), ternary) are never touched.
Runs FIRST, before strip (it honors comments strip would delete)."""

from scan import tokenize




def _mask(code):
    """Return (mask, comments): mask has str/regex/comment chars blanked
    (newlines kept); comments is a list of (line, text)."""
    out = []
    comments = []
    line = 1
    for kind, text in tokenize(code):
        if kind in ("str", "regex", "comment"):
            if kind == "comment":
                comments.append((line, text))
            out.append("".join("\n" if ch == "\n" else " " for ch in text))
        else:
            out.append(text)
        line += text.count("\n")
    return "".join(out), comments


def _line_of(code, pos):
    return code.count("\n", 0, pos) + 1


def _prev_word(mask, i):
    k = i - 1
    while k >= 0 and mask[k] in " \t\n":
        k -= 1
    if k >= 0 and mask[k] == ")":
        depth = 1
        k -= 1
        while k >= 0 and depth:
            if mask[k] == ")":
                depth += 1
            elif mask[k] == "(":
                depth -= 1
            k -= 1
        while k >= 0 and mask[k] in " \t\n":
            k -= 1
    e = k + 1
    while k >= 0 and (mask[k].isalnum() or mask[k] in "_$"):
        k -= 1
    return mask[k + 1:e]


def _stmt_start(mask, i):
    k = i - 1
    while k >= 0 and mask[k] in " \t":
        k -= 1
    if k < 0 or mask[k] in ";\n{}":
        return True
    if mask[k] == ")":
        return _prev_word(mask, i) in ("if", "while", "for", "with")
    if mask[k].isalnum() or mask[k] in "_$":
        return _prev_word(mask, i) in ("else", "do", "void")
    return False


def _call_end(mask, i):
    n = len(mask)
    j = i + len("console.")
    while j < n and (mask[j].isalnum() or mask[j] in "_$"):
        j += 1
    while j < n and mask[j] in " \t\n":
        j += 1
    if j >= n or mask[j] != "(":
        return -1, False
    depth = 0
    k = j
    while k < n:
        ch = mask[k]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                k += 1
                while k < n and mask[k] in " \t":
                    k += 1
                semi = k < n and mask[k] == ";"
                if semi:
                    k += 1
                return k, semi
        k += 1
    return -1, False


def _void_start(mask, i):
    """Index of a `void` keyword directly preceding console at i (spaces/tabs
    only between), else -1. `void console.log(x);` must go as a whole --
    leaving `void ;` behind is a SyntaxError."""
    k = i - 1
    while k >= 0 and mask[k] in " \t":
        k -= 1
    e = k + 1
    while k >= 0 and (mask[k].isalnum() or mask[k] in "_$"):
        k -= 1
    if mask[k + 1:e] == "void":
        q = k
        while q >= 0 and mask[q] in " \t\n":
            q -= 1
        prev = mask[q] if q >= 0 else ";"
        if q < 0 or prev in ";\n{}" or prev == ")":
            return k + 1
    return -1


def run(code: str) -> str:
    mask, comments = _mask(code)
    keep_lines = {ln for ln, tx in comments if "keep-log" in tx}
    out = []
    i, n = 0, len(code)
    while i < n:
        if mask.startswith("console.", i) and _stmt_start(mask, i):
            j, semi = _call_end(mask, i)
            if j > i and (semi or _next_ok(mask, j)):
                if _line_of(code, j) not in keep_lines and _line_of(code, i) not in keep_lines:
                    vs = _void_start(mask, i)
                    if vs >= 0:
                        del out[len(out) - (i - vs):]
                    out.append(";")
                    i = j
                    continue
                out.append(code[i:j])
                i = j
                continue
        out.append(code[i])
        i += 1
    return "".join(out)


def _next_ok(mask, j):
    # guard ternary: `? console.log(x) : y` keeps the call
    k = j
    n = len(mask)
    while k < n and mask[k] in " \t\n":
        k += 1
    return k >= n or mask[k] in ";}"
