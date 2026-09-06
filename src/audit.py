"""audit.py: report risky constructs in RAW sources before forging.

Raw .js hides things eyes miss (leftover logs, eval, sinks). --audit lists
them with line numbers; the build continues only on approval. keep-log lines
are shown as KEPT (banner/probe must survive on purpose).
"""

import re

from scan import build_mask

_PATTERNS = [
    ("console", re.compile(r"\bconsole\s*\.\s*(log|warn|error|info|debug|table|trace|assert|count|time|timeEnd)\b")),
    ("debugger", re.compile(r"\bdebugger\b")),
    ("eval", re.compile(r"\beval\s*\(")),
    ("Function()", re.compile(r"\bnew\s+Function\s*\(")),
    ("innerHTML", re.compile(r"\binnerHTML\b")),
    ("outerHTML", re.compile(r"\bouterHTML\b")),
    ("document.write", re.compile(r"\bdocument\s*\.\s*write(ln)?\b")),
]


def findings(code):
    """Return [(line, kind, snippet)] for code regions only (mask first)."""
    mask = build_mask(code)
    out = []
    for kind, rx in _PATTERNS:
        for m in rx.finditer(mask):
            pos = m.start()
            line = code.count("\n", 0, pos) + 1
            keep = "keep-log" in code.split("\n")[line - 1]
            snippet = code.split("\n")[line - 1].strip()[:100]
            out.append((line, kind + (" [KEPT keep-log]" if keep else ""), snippet))
    out.sort()
    return out


def report(code):
    found = findings(code)
    if not found:
        return "audit: clean (no console/debugger/eval/sink patterns)"
    lines = ["audit: %d finding(s)" % len(found)]
    for ln, kind, snip in found:
        lines.append("  L%-5d %-22s %s" % (ln, kind, snip))
    return "\n".join(lines)
