# League check — is anything better than forge at its own game?
Date: 2026-09-06 | sources: live web (obfuscator.io docs, npm, GitHub) | v1

## The league (lightweight, offline/free, userscript-suitable)
- **javascript-obfuscator** (OSS): the heavyweight of the lightweights.
  Presets incl. LOW (stringArray + selfDefending, no flattening).
- **veil-obfuscator** (new, 18 stars): closest philosophy rival — "practical
  protection without the performance hit", VM-string mode, userscript-friendly.
- **Classic packers** (Dean Edwards P_A_C_K_E_R family): our FS model is this
  bloodline (eval-decode-run), modernized with segments + signature.
- Out of league (ceiling, not rivals): Jscrambler, obfuscator.io Pro VM,
  JSDefender (price/platform/VM-perf cost).

## Verdict: nothing strictly better IN-league, but two rivals teach us plenty
javascript-obfuscator LOW beats us on transform breadth; veil beats us on
threat-model honesty + VM-strings. Our独家 advantages hold: data-file model
(code never rests on disk as code), 1 KB runner, determinism, audit gate,
zero deps, offline.

## Gaps worth closing (ranked, borrowable without leaving our league)
1. **DomainLock in runner** — biggest missing cheap win. j-obfuscator and veil
   both ship it; for userscripts it's THE anti-theft primitive (stolen copy
   won't run off-domain). Cost: ~2 lines in runner + allowed-host list in
   manifest. Recommend FIRST.
2. **String array rotate/shuffle + per-build keys** — our XOR-0x5A is static
   across all files ever forged. j-obfuscator: base64/rc4 + rotate + shuffle
   + wrappers; veil: per-build structure variance. Minimum: per-file salt in
   manifest (keys differ per build); medium: rotate segments.
3. **Self-defending tripwire** — j-obfuscator/veil refuse beautified/tampered
   runtimes. Our runner verifies the FILE, never ITSELF. Cheap version: runner
   hashes its own source length/shape at boot (any edit breaks it).
4. **Seedable builds** — j-obfuscator has `seed`; ours is deterministic but
   unseeded (same input ⇒ same file forever ⇒ pattern stability helps the
   analyst). Add `--seed` (shuffle + key schedule derive from it).
5. **disableConsoleOutput equivalent** — we HAVE it build-time (nolog, arguably
   cleaner). Note as parity, not gap.
6. **simplify/boolean-expression transforms** — cheap AST-less wins we never
   took (`true`→`!0`, constant folding). Small pass, real readability cost.

## Deliberately NOT borrowed (out of league by design)
- Control-flow flattening, dead-code injection, VM bytecode, debugProtection
  intervals: perf cost + mobile risk + bloat. Our threat model (curious +
  free-AI) doesn't pay for them. Revisit only on observed cracking.
- Anti-LLM defenses (2026 trend: vmDefenseHook, automation decoys): watch,
  don't chase; our content is small enough that obscurity + speed wins.

## Suggested order
domainLock → per-file salt → self-tripwire → --seed → simplify-pass.
Each is a minor version; each is independently verifiable by the battery.

## Decision (owner, 2026-09-06): NO built-in domainLock
Domain binding stays the developer's choice, not forge's: some scripts must
run everywhere (adblock-style), some are site-bound. A built-in would force
everyone into one model. Forge remains neutral; per-script locks (if wanted)
live in consumer code. Item closed, not queued.
