"""strip pass: remove // and /* */ comments via the shared scanner.
Regex/str/template-aware (H1: a regex like /\\// no longer eats trailing code).
Output for comment-free inputs is byte-identical to input."""

from scan import tokenize




def run(code: str) -> str:
    return "".join(text for kind, text in tokenize(code) if kind != "comment")
