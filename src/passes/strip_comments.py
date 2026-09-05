"""strip_comments pass: remove // and /* */ comments, string-aware."""


def run(code: str) -> str:
    out = []
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        nxt = code[i + 1] if i + 1 < n else ""
        if c in ("'", '"', "`"):
            quote = c
            out.append(c)
            i += 1
            while i < n:
                ch = code[i]
                out.append(ch)
                if ch == "\\":
                    if i + 1 < n:
                        out.append(code[i + 1])
                        i += 2
                        continue
                if ch == quote:
                    i += 1
                    break
                i += 1
        elif c == "/" and nxt == "/":
            while i < n and code[i] != "\n":
                i += 1
        elif c == "/" and nxt == "*":
            i += 2
            while i + 1 < n and not (code[i] == "*" and code[i + 1] == "/"):
                i += 1
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)
