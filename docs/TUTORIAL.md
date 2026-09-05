# forge tutorial (5 minutes)

## 1. Run a single pass
```bash
python3 tools/forge.py tests/basic.js /tmp/out.js --passes strip_comments
```
Output: same code, comments gone, strings intact.

## 2. Chain passes
```bash
python3 tools/forge.py in.js out.js --passes strip_comments,mangle,string_crypt
```
Passes run left to right. Recommended order is the one above (see `DESIGN.md`).

## 3. Write your own pass
Create `src/passes/shout.py`:
```python
def run(code: str) -> str:
    return code.upper()  # don't ship this :)
```
Run it:
```bash
python3 tools/forge.py tests/basic.js /tmp/out.js --passes shout
```
No registration needed — the CLI loads `src/passes/<name>.py` by name.

## 4. Verify
```bash
python3 tools/check.py
```
Checks every pass imports, exposes `run()`, and survives a torture sample
(strings with URLs, fake comments, template literals).
