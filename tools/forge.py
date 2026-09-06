#!/usr/bin/env python3
"""forge CLI: raw JS -> .fs (or processed .js). Usage:
python3 tools/forge.py in.js out.fs [--passes strip,short,crypt,pack]
python3 tools/forge.py host.js out.js --passes strip,short,crypt --embed runner.js
Default chain is the locked v1 pipeline. pack is always forced last.
--embed FILE inlines FILE at the /*__FORGE_RUNNER__*/ marker BEFORE passes run,
so the first .js files holding forgescript ship clean and hard to read.
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
    ap.add_argument("--embed", default="",
                    help="inline this JS file at the /*__FORGE_RUNNER__*/ marker first")
    args = ap.parse_args()

    names = [p.strip() for p in args.passes.split(",") if p.strip()]
    if args.dev:
        names = [p for p in names if p != "pack"]
    if "pack" in names:
        names = [p for p in names if p != "pack"] + ["pack"]

    code = Path(args.src).read_text(encoding="utf-8")
    if args.embed:
        snippet = Path(args.embed).read_text(encoding="utf-8")
        if "/*__FORGE_RUNNER__*/" not in code:
            print("embed marker /*__FORGE_RUNNER__*/ not found, aborting")
            return 1
        code = code.replace("/*__FORGE_RUNNER__*/", snippet, 1)
        print(f"embedded {args.embed} ({len(snippet)} chars)")
    for name in names:
        mod = importlib.import_module(f"passes.{name}")
        code = mod.run(code)
        print(f"pass applied: {name} ({len(code)} chars)")
    Path(args.dst).write_text(code, encoding="utf-8")
    print(f"wrote {args.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
