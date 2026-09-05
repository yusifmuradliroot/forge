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
    runner = ROOT / "src" / "runner" / "forgescript.js"
    if not runner.is_file():
        fails.append("missing src/runner/forgescript.js")
    else:
        src = runner.read_text(encoding="utf-8")
        for keep in ("ForgeScript", "FS:1", "Function"):
            if keep not in src:
                fails.append(f"runner missing {keep!r}")
        if "://" in src or "/*" in src:
            fails.append("runner must be note-free")
    passes = sorted(p.stem for p in (ROOT / "src" / "passes").glob("*.py")
                    if not p.name.startswith("_"))
    for want in ("strip", "short", "crypt", "pack"):
        if want not in passes:
            fails.append(f"missing v1 pass: {want}")
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
    if fails:
        for f in fails:
            print("FAIL " + f)
        print(f"RESULT: FAIL ({len(fails)} problem(s))")
        return 1
    print(f"RESULT: PASS ({len(passes)} pass(es), runner OK)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
