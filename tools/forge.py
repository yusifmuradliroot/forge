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
    ap.add_argument("src", nargs="?", help="input JS file")
    ap.add_argument("dst", nargs="?", help="output .fs file")
    ap.add_argument("--passes", default=",".join(DEFAULT),
                    help="comma-separated pass names from src/passes/")
    ap.add_argument("--dev", action="store_true",
                    help="developer mode: skip pack, emit readable processed JS")
    ap.add_argument("--embed", default="",
                    help="inline this JS file at the /*__FORGE_RUNNER__*/ marker first")
    ap.add_argument("--embed-max", type=int, default=8192,
                    help="reject embed source larger than this (bytes)")
    ap.add_argument("--embed-has", default="",
                    help="embed source must contain this string (e.g. ForgeScript)")
    ap.add_argument("--host", action="store_true",
                    help="userscript host mode: preserve ==UserScript== header, "
                         "process body only (pack rejected in this mode)")
    ap.add_argument("--version", action="store_true",
                    help="print forge VERSION and exit")
    args = ap.parse_args()

    if args.version:
        print((ROOT / "VERSION").read_text(encoding="utf-8").strip())
        return 0
    if not args.src or not args.dst:
        ap.error("src and dst are required (unless --version)")

    names = [p.strip() for p in args.passes.split(",") if p.strip()]
    if args.dev:
        names = [p for p in names if p != "pack"]
    if "pack" in names:
        names = [p for p in names if p != "pack"] + ["pack"]

    code = Path(args.src).read_text(encoding="utf-8")
    header = ""
    if args.host:
        lines = code.split("\n")
        try:
            end = next(i for i, l in enumerate(lines) if "==/UserScript==" in l)
        except StopIteration:
            print("host mode needs a ==UserScript== header block, aborting")
            return 1
        header = "\n".join(lines[:end + 1]) + "\n"
        code = "\n".join(lines[end + 1:])
        if "pack" in names:
            print("pack rejected in host mode (output must stay installable .js)")
            return 1
    if args.embed:
        raw_snippet = Path(args.embed).read_text(encoding="utf-8")
        if len(raw_snippet.encode("utf-8")) > args.embed_max:
            print(f"embed source too large ({len(raw_snippet)} chars > {args.embed_max} cap), aborting")
            return 1
        if args.embed_has and args.embed_has not in raw_snippet:
            print(f"embed source missing required {args.embed_has!r}, aborting")
            return 1
        snippet = raw_snippet
        if "/*__FORGE_RUNNER__*/" not in code:
            print("embed marker /*__FORGE_RUNNER__*/ not found, aborting")
            return 1
        code = code.replace("/*__FORGE_RUNNER__*/", snippet, 1)
        print(f"embedded {args.embed} ({len(snippet)} chars, verified)")
    for name in names:
        # L11: unknown pass names used to die with a bare traceback.
        if not name.replace("_", "").isalnum() or name.startswith("_"):
            print(f"bad pass name {name!r} (letters/digits/underscore, no leading _), aborting")
            return 1
        try:
            mod = importlib.import_module(f"passes.{name}")
        except ImportError:
            print(f"unknown pass {name!r} (see src/passes/), aborting")
            return 1
        if not callable(getattr(mod, "run", None)):
            print(f"pass {name!r} has no run(code) function, aborting")
            return 1
        try:
            code = mod.run(code)
        except Exception as e:
            # Passes abort loudly (L6/L14); never write half-processed output.
            print(f"pass {name!r} failed: {e}, aborting (no output written)")
            return 1
        print(f"pass applied: {name} ({len(code)} chars)")
    Path(args.dst).write_text(header + code, encoding="utf-8")
    print(f"wrote {args.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
