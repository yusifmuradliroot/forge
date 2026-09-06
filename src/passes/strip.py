"""strip pass: remove // and /* */ comments via the shared scanner.
Regex/str/template-aware (H1: a regex like /\\// no longer eats trailing code).
Output for comment-free inputs is byte-identical to input."""

try:
    from scan import tokenize
except ImportError:
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from scan import tokenize




def run(code: str) -> str:
    return "".join(text for kind, text in tokenize(code) if kind != "comment")
