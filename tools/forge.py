#!/usr/bin/env python3
"""forge CLI: raw JS -> .fs. Usage:
python3 tools/forge.py in.js out.fs [--passes strip,short,crypt,pack]
Default chain is the locked v1 pipeline. pack is always forced last.
"""
import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

DEFAULT = ["strip", "short", "crypt", "pack"]


def main():
    ap = argparse.ArgumentParser(description="forge: raw JS -> .fs")
    ap.add_argument("src", help="input JS file")
    ap.add_argument("dst", help="output .fs file")
    ap.add_argument("--passes", default=",".join(DEFAULT),
                    help="comma-separated pass names from src/passes/")
    ap.add_argument("--dev", action="store_true",
                    help="developer mode: skip pack, emit readable processed JS")
    args = ap.parse_args()

    names = [p.strip() for p in args.passes.split(",") if p.strip()]
    if args.dev:
        names = [p for p in names if p != "pack"]
    if "pack" in names:
        names = [p for p in names if p != "pack"] + ["pack"]

    code = Path(args.src).read_text(encoding="utf-8")
    for name in names:
        mod = importlib.import_module(f"passes.{name}")
        code = mod.run(code)
        print(f"pass applied: {name} ({len(code)} chars)")
    Path(args.dst).write_text(code, encoding="utf-8")
    print(f"wrote {args.dst}")


if __name__ == "__main__":
    main()
