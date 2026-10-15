#!/usr/bin/env python3
"""forge integrity checker. One run, clear verdict.
Usage: python3 tools/check.py
Exit 0 = PASS, 1 = FAIL. Fix what it reports and re-run until green.
"""
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

fails = []


def main():
    if set(sys.argv[1:]) & {"-h", "--help"}:
        print(__doc__.strip())
        return 0
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
        try:
            pyproj = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
            if ver not in pyproj:
                fails.append(f"pyproject.toml does not mention VERSION {ver} (version rides with the bump)")
        except Exception as e:
            fails.append(f"pyproject.toml unreadable: {e}")
    # Public hygiene: the custom license (attribution + takedown) must ship,
    # and internal memory must never ship.
    try:
        lic = (ROOT / "LICENSE").read_text(encoding="utf-8")
        if "NO PUBLIC USE" in lic:
            fails.append("LICENSE still forbids public use (see section 1)")
        for keep in ("ATTRIBUTION", "TAKEDOWN ON DEMAND", "yusifmuradliroot/forge"):
            if keep not in lic:
                fails.append(f"LICENSE missing {keep!r} (attribution + takedown required)")
    except Exception as e:
        fails.append(f"LICENSE unreadable: {e}")
    for private in ("AGENTS.md", "AI", "ai-reports"):
        if (ROOT / private).exists():
            fails.append(f"{private} must not ship in the public repo (internal memory)")
    if not (ROOT / ".gitattributes").is_file():
        fails.append("missing .gitattributes (Windows CRLF breaks FS:2)")
    else:
        ga = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        if "eol=lf" not in ga:
            fails.append(".gitattributes must force eol=lf")
    # Regression vectors for the 2.12.0 fixes (must stay green).
    try:
        from passes import nolog as _nolog
        if _nolog.run("void console.log(1);").strip() != ";":
            fails.append("nolog: void console leaves invalid code (want ';')")
    except Exception as e:
        fails.append(f"nolog void vector failed: {e}")
    try:
        from passes import crypt as _crypt
        inner = _crypt.run("var a=`x${y+\"this is a very long string value\"}w`;")
        if "__f(" not in inner:
            fails.append("crypt: live ${} string not encrypted")
        middle = _crypt.run("var t=`a${x}\"b\"${y}c`;")
        if "\"b\"" not in middle:
            fails.append("crypt: template middle corrupted")
    except Exception as e:
        fails.append(f"crypt template vector failed: {e}")
    try:
        from poison import find_poison as _poison
        if "f" not in _poison("export function f(a){return a+1}"):
            fails.append("poison: exported function name not protected")
    except Exception as e:
        fails.append(f"poison export vector failed: {e}")
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
    try:
        from seed import fnv1a as seed_fnv, explicit_seed, shuffled
        if "%08x" % seed_fnv(b"foobar") != "bf9cf968":
            fails.append("seed fnv1a vector mismatch (want bf9cf968)")
        if explicit_seed() is not None:
            fails.append("seed explicit_seed() must be None without FORGE_SEED")
        if shuffled([1, 2, 3], 1) == [1, 2, 3] and shuffled([1, 2, 3, 4, 5], 1) == [1, 2, 3, 4, 5]:
            fails.append("seed shuffled() looks like a no-op")
    except Exception as e:
        fails.append(f"seed import failed: {e}")
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
