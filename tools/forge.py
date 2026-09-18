#!/usr/bin/env python3
"""forge CLI: raw JS -> .fs (or processed .js). Usage:
python3 tools/forge.py in.js out.fs [--passes nolog,strip,short,num,flow,simp,uni,crypt,pack]
python3 tools/forge.py host.js out.js --passes nolog,strip,short,crypt --embed runner.js --embed-has ForgeScript --host
python3 tools/forge.py in.js out.fs --audit [--yes]
Default chain is nolog,strip,short,num,flow,simp,uni,crypt,pack. pack is always forced last
(and rejected in --host mode, where output must stay installable .js).
--embed FILE inlines FILE at the /*__FORGE_RUNNER__*/ marker BEFORE passes run,
so hosts ship with the runner processed inline. Passes run exactly once each;
crypt refuses sources that already use its stub/table names, pack refuses empty/tiny inputs.
--gate MS (with --embed only) bakes a stricter runner anti-debug threshold
into the embedded copy (default 100ms, 0..10000); the marker must match exactly once.
"""
import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

DEFAULT = ["nolog", "strip", "short", "num", "flow", "simp", "uni", "crypt", "pack"]


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
    ap.add_argument("--audit", action="store_true",
                    help="report risky constructs (console/debugger/eval/sinks) "
                         "in the raw source and ask approval before building")
    ap.add_argument("--yes", action="store_true",
                    help="with --audit: print the report but skip the prompt (no-op otherwise)")
    ap.add_argument("--gate", type=int, default=100,
                    help="runner anti-debug threshold ms for --embed builds "
                         "(default 100, 0..10000; needs --embed)")
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
    # Normalize CRLF (Windows checkout) to LF: the FS:2 tag, the runner tag
    # check and all mask offsets assume "\n". Output is always LF (see
    # .gitattributes); behavior on LF inputs is byte-identical to before.
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    if args.audit:
        # Audit the RAW input (line numbers match the file you review).
        from audit import report as audit_report
        print(audit_report(code))
        if not args.yes:
            try:
                ans = input("forge audit: build anyway? [y/N] ").strip().lower()
            except EOFError:
                ans = ""
            if ans not in ("y", "yes"):
                print("aborted by audit (no output written)")
                return 1
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
        raw_snippet = Path(args.embed).read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
        if len(raw_snippet.encode("utf-8")) > args.embed_max:
            print(f"embed source too large ({len(raw_snippet.encode('utf-8'))} bytes > {args.embed_max} cap), aborting")
            return 1
        if args.embed_has and args.embed_has not in raw_snippet:
            print(f"embed source missing required {args.embed_has!r}, aborting")
            return 1
        snippet = raw_snippet
        if "/*__FORGE_RUNNER__*/" not in code:
            print("embed marker /*__FORGE_RUNNER__*/ not found, aborting")
            return 1
        if code.count("/*__FORGE_RUNNER__*/") > 1:
            print("warning: multiple embed markers, only the first is replaced")
        code = code.replace("/*__FORGE_RUNNER__*/", snippet, 1)
        print(f"embedded {args.embed} ({len(snippet.encode('utf-8'))} bytes, verified)")
    if args.gate != 100:
        if not args.embed:
            print("--gate needs --embed (the threshold lives in the runner), aborting")
            return 1
        if not 0 <= args.gate <= 10000:
            print("--gate must be 0..10000 ms, aborting")
            return 1
        marker = "Date.now()-a>100"
        if code.count(marker) != 1:
            print("--gate marker not found exactly once, aborting (runner changed?)")
            return 1
        code = code.replace(marker, f"Date.now()-a>{args.gate}")
        print(f"gate threshold baked: {args.gate}ms")
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
    Path(args.dst).write_text(header + code, encoding="utf-8", newline="\n")
    print(f"wrote {args.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
