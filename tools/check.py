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

fails, warns = [], []

SAMPLE = 'const u = "https://x.y/z"; // c\n/* b */ console.log(u);\n'


def main():
    if not (ROOT / "VERSION").is_file():
        fails.append("missing VERSION file")
    passes = sorted(p.stem for p in (ROOT / "src" / "passes").glob("*.py")
                    if not p.name.startswith("_"))
    if not passes:
        fails.append("no passes in src/passes/")
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
            out = mod.run(SAMPLE)
        except Exception as e:
            fails.append(f"pass '{name}': crashed on sample: {e}")
            continue
        if "https://x.y/z" not in out:
            fails.append(f"pass '{name}': corrupted string content in sample")
        if "console.log" not in out:
            fails.append(f"pass '{name}': dropped code in sample")
    fixtures = list((ROOT / "tests").glob("*.js"))
    if not fixtures:
        warns.append("no fixtures in tests/")

    for w in warns:
        print("WARN " + w)
    if fails:
        for f in fails:
            print("FAIL " + f)
        print(f"RESULT: FAIL ({len(fails)} problem(s))")
        return 1
    print(f"RESULT: PASS ({len(passes)} pass(es), {len(fixtures)} fixture(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
