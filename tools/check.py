#!/usr/bin/env python3
"""forge integrity checker. One run, clear verdict.
Usage: python3 tools/check.py
Exit 0 = PASS, 1 = FAIL. Fix what it reports (max 2 rounds), then ask the user.
"""
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

fails = []


def main():
    if not (ROOT / "VERSION").is_file():
        fails.append("missing VERSION file")
    else:
        # M4: release-checklist rule -- every bump ships README + CHANGELOG.
        ver = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for doc in ("README.md", "CHANGELOG.md"):
            try:
                if ver not in (ROOT / doc).read_text(encoding="utf-8"):
                    fails.append(f"{doc} does not mention VERSION {ver} (docs ride with the bump)")
            except Exception as e:
                fails.append(f"{doc} unreadable: {e}")
    runner = ROOT / "src" / "runner" / "forgescript.js"
    if not runner.is_file():
        fails.append("missing src/runner/forgescript.js")
    else:
        src = runner.read_text(encoding="utf-8")
        for keep in ("ForgeScript", "FS:2", "Function", "TextDecoder"):
            if keep not in src:
                fails.append(f"runner missing {keep!r}")
        if "FS:1" in src:
            fails.append("runner still accepts FS:1 (removed in 2.4.0)")
        if "://" in src or "/*" in src:
            fails.append("runner must be note-free")
    passes = sorted(p.stem for p in (ROOT / "src" / "passes").glob("*.py")
                    if not p.name.startswith("_"))
    for want in ("strip", "short", "crypt", "pack"):
        if want not in passes:
            fails.append(f"missing v1 pass: {want}")
    try:
        from passes.pack import fnv1a
        if "%08x" % fnv1a(b"foobar") != "bf9cf968":
            fails.append("pack fnv1a vector mismatch (want bf9cf968)")
    except Exception as e:
        fails.append(f"pack fnv1a import failed: {e}")
    sample = 'const greeting = "hello packed world"; // c\nconsole.log(greeting);\n'
    for name in passes:
        try:
            mod = importlib.import_module(f"passes.{name}")
        except Exception as e:
            fails.append(f"pass '{name}': import failed: {e}")
            continue
        if not callable(getattr(mod, "run", None)):
            fails.append(f"pass '{name}': missing run(code) function")
            continue
        try:
            out = mod.run(sample)
        except Exception as e:
            fails.append(f"pass '{name}': crashed on sample: {e}")
            continue
        if name == "pack":
            import json as _json
            lines = out.split("\n")
            if not lines or lines[0] != "FS:2":
                fails.append("pack: missing FS:2 tag")
            else:
                try:
                    m = _json.loads(lines[1])
                    blobs = [b for b in lines[2:] if b]
                    if len(blobs) != 3 or sorted(m.get("o", [])) != [0, 1, 2] or not m.get("s"):
                        fails.append("pack: bad manifest (want 3 blobs, order perm of 0..2, sig)")
                    else:
                        # M2: verify the signature itself (shape-only checks let
                        # sig regressions ship green -- the inverse-order saga).
                        # Salted files (2.9+): unrotate disk blobs first.
                        ordered = [blobs[i] for i in m["o"]]
                        if m.get("k"):
                            try:
                                salt = bytes.fromhex(m["k"])
                                fixed = []
                                for e, b in enumerate(ordered):
                                    r = salt[e % len(salt)] % (len(b) or 1)
                                    fixed.append(b[-r:] + b[:-r] if r else b)
                                ordered = fixed
                            except Exception as e:
                                fails.append(f"pack: bad salt: {e}")
                                return
                        want = "%08x" % fnv1a(("FS:2\n" + ",".join(map(str, m["o"]))
                                                    + "\n" + "".join(ordered)).encode())
                        if want != m["s"]:
                            fails.append("pack: signature does not verify")
                except Exception as e:
                    fails.append(f"pack: manifest invalid: {e}")
    if fails:
        for f in fails:
            print("FAIL " + f)
        print(f"RESULT: FAIL ({len(fails)} problem(s))")
        return 1
    print(f"RESULT: PASS ({len(passes)} pass(es), runner OK)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
