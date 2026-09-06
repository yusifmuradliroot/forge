"""nolog pass: remove console.* call statements, comment-aware.
Lines whose trailing comment contains 'keep-log' survive
(e.g. the startup banner). Expressions (x = console.log(...),
cond ? console.log(...) : y) are NEVER touched.
Runs FIRST, before strip (it honors comments strip would delete)."""


def run(code: str) -> str:
    out = []
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        nxt = code[i + 1] if i + 1 < n else ""
        # copy comments through untouched
        if c == "/" and nxt == "/":
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append(code[i:j])
            i = j
            continue
        if c == "/" and nxt == "*":
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(code[i:j])
            i = j
            continue
        if c in ("'", '"', "`"):
            j = _str_end(code, i)
            out.append(code[i:j])
            i = j
            continue
        if code.startswith("console.", i) and _stmt_start(code, i):
            j, semi = _call_end(code, i)
            if j > i and (semi or _next_ok(code, j)):
                # same-line trailing comment may carry keep-log
                k = j
                while k < n and code[k] in " \t":
                    k += 1
                keep = False
                if code.startswith("//", k):
                    eol = code.find("\n", k)
                    eol = n if eol < 0 else eol
                    keep = "keep-log" in code[k:eol]
                if not keep:
                    i = j
                    continue
                out.append(code[i:j])
                i = j
                continue
        out.append(c)
        i += 1
    return "".join(out)


def _str_end(code, i):
    q = code[i]
    n = len(code)
    k = i + 1
    while k < n:
        ch = code[k]
        if ch == "\\":
            k += 2
            continue
        if ch == q:
            return k + 1
        if q != "`" and ch == "\n":
            return k
        k += 1
    return n


def _prev_word(code, i):
    k = i - 1
    while k >= 0 and code[k] in " \t\n":
        k -= 1
    if k >= 0 and code[k] == ")":
        depth = 1
        k -= 1
        while k >= 0 and depth:
            if code[k] == ")":
                depth += 1
            elif code[k] == "(":
                depth -= 1
            k -= 1
        while k >= 0 and code[k] in " \t\n":
            k -= 1
    e = k + 1
    while k >= 0 and (code[k].isalnum() or code[k] in "_$"):
        k -= 1
    return code[k + 1:e]


def _stmt_start(code, i):
    k = i - 1
    while k >= 0 and code[k] in " \t":
        k -= 1
    if k < 0 or code[k] in ";\n{}":
        return True
    if code[k] == ")":
        return _prev_word(code, i) in ("if", "while", "for", "with")
    if code[k].isalnum() or code[k] in "_$":
        return _prev_word(code, i) in ("else", "do")
    return False


def _call_end(code, i):
    n = len(code)
    j = i + len("console.")
    while j < n and (code[j].isalnum() or code[j] in "_$"):
        j += 1
    while j < n and code[j] in " \t\n":
        j += 1
    if j >= n or code[j] != "(":
        return -1, False
    depth = 0
    k = j
    while k < n:
        ch = code[k]
        if ch in ("'", '"', "`"):
            k = _str_end(code, k)
            continue
        if ch == "/" and k + 1 < n and code[k + 1] == "/":
            eol = code.find("\n", k)
            k = n if eol < 0 else eol
            continue
        if ch == "/" and k + 1 < n and code[k + 1] == "*":
            end = code.find("*/", k + 2)
            k = n if end < 0 else end + 2
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                k += 1
                while k < n and code[k] in " \t":
                    k += 1
                semi = k < n and code[k] == ";"
                if semi:
                    k += 1
                return k, semi
        k += 1
    return -1, False


def _next_ok(code, j):
    # guard ternary: `? console.log(x) : y` keeps the call
    k = j
    n = len(code)
    while k < n and code[k] in " \t\n":
        k += 1
    return k >= n or code[k] in ";}"
