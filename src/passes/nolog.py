"""nolog pass: remove console.* call statements, string-aware.
Lines containing 'keep-log' survive (e.g. the startup banner).
Runs after strip (comments gone), before short (identifiers intact)."""


def run(code: str) -> str:
    out = []
    i, n = 0, len(code)
    while i < n:
        if code.startswith("console.", i) and _is_stmt(code, i):
            j = _call_end(code, i)
            if j > i:
                stmt = code[i:j]
                if "keep-log" not in stmt:
                    i = j
                    continue
                out.append(stmt)
                i = j
                continue
        out.append(code[i])
        i += 1
    return "".join(out)


def _is_stmt(code, i):
    k = i - 1
    while k >= 0 and code[k] in " \t":
        k -= 1
    return k < 0 or code[k] in ";\n{}"


def _call_end(code, i):
    n = len(code)
    j = i + len("console.")
    while j < n and (code[j].isalnum() or code[j] in "_$"):
        j += 1
    while j < n and code[j] in " \t":
        j += 1
    if j >= n or code[j] != "(":
        return -1
    depth = 0
    instr = None
    k = j
    while k < n:
        ch = code[k]
        if instr:
            if ch == "\\":
                k += 2
                continue
            if ch == instr:
                instr = None
        else:
            if ch in ("'", '"', "`"):
                instr = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    k += 1
                    while k < n and code[k] in " \t":
                        k += 1
                    if k < n and code[k] == ";":
                        k += 1
                    return k
        k += 1
    return -1
