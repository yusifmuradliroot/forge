"""num pass: decimal integer literals -> hex (200 -> 0xc8).

Token-based (shared scanner): only matches inside 'other' tokens, so strings,
regex, comments and templates are immune. Skips anything that isn't a plain
base-10 integer: existing hex/octal/binary, floats, exponents, BigInt suffix,
and digits glued to identifiers or dots (a.5, 5.toString stays intact).
Semantics-preserving by construction (same numeric value, different spelling).
"""

import re

from scan import tokenize

_NUM = re.compile(r"(?<![\w$.])(0|[1-9][0-9]*)(?![\w$.])")


def _convert_other(text):
    def rep(m):
        word = m.group(1)
        # A dot or letter glued on either side in the ORIGINAL (not just the
        # match edges, which the lookarounds already guard) -- keep it simple:
        # the regex guards handle it. Convert, preserving magnitude.
        return hex(int(word))
    return _NUM.sub(rep, text)


def run(code: str) -> str:
    out = []
    for kind, text in tokenize(code):
        if kind == "other":
            out.append(_convert_other(text))
        else:
            out.append(text)
    return "".join(out)
