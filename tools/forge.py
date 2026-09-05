#!/usr/bin/env python3
"""forge CLI: run passes over a JS file. Usage:
python3 tools/forge.py in.js out.js --passes strip_comments[,next_pass]
"""
import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def main():
    ap = argparse.ArgumentParser(description="forge mini compiler")
    ap.add_argument("src", help="input JS file")
    ap.add_argument("dst", help="output JS file")
    ap.add_argument("--passes", default="strip_comments",
                    help="comma-separated pass names from src/passes/")
    args = ap.parse_args()

    code = Path(args.src).read_text(encoding="utf-8")
    for name in [p.strip() for p in args.passes.split(",") if p.strip()]:
        mod = importlib.import_module(f"passes.{name}")
        code = mod.run(code)
        print(f"pass applied: {name} ({len(code)} chars)")
    Path(args.dst).write_text(code, encoding="utf-8")
    print(f"wrote {args.dst}")


if __name__ == "__main__":
    main()
