#!/bin/bash
# forge selftest (L13): one command runs the whole battery. Exit 0 = green.
# Usage: bash tests/selftest.sh
set -u
cd "$(dirname "$0")/.." || exit 1
fail=0
say() { printf '%-28s %s\n' "$1" "$2"; }
python3 tools/check.py > /tmp/st_check.txt 2>&1 || fail=1
say "check.py" "$(tail -1 /tmp/st_check.txt)"
node tests/check_runner.js > /tmp/st_run.txt 2>&1 || fail=1
say "runner battery" "$(tail -1 /tmp/st_run.txt)"
python3 tools/forge.py tests/e2e.js /tmp/st_e2e.fs > /dev/null 2>&1 || fail=1
node -e "
const fs=require('fs');
eval(fs.readFileSync('src/runner/forgescript.js','utf8'));
const logs=[]; const o=console.log; console.log=(...a)=>logs.push(a.join(' '));
ForgeScript.run(fs.readFileSync('/tmp/st_e2e.fs','utf8'));
console.log=o;
if (logs[0]!=='hello packed world, this is a longer string 42') { console.log('E2E MISMATCH'); process.exit(1); }
console.log('E2E IDENTICAL');
" > /tmp/st_e2e.txt 2>&1 || fail=1
say "e2e chain" "$(tail -1 /tmp/st_e2e.txt)"
python3 -c "
import sys, re; sys.path.insert(0,'src')
from passes import short, strip
# cross-file contract: embedded runner name must survive for other files
host = short.run(strip.run('/*__FORGE_RUNNER__*/'.replace('/*__FORGE_RUNNER__*/', open('src/runner/forgescript.js').read())))
assert 'var ForgeScript=' in host, 'RUNNER RENAMED'
assert len(re.findall(r'(?<![\w\$.])ForgeScript(?![\w\$])', host)) >= 1, 'RUNNER REFS LOST'
open('/tmp/st_runner.txt','w').write('RUNNER-NAME PASS')" || fail=1
say "runner name" "$(cat /tmp/st_runner.txt)"
node --check tests/crypt_regex.js > /dev/null 2>&1 || fail=1
python3 tools/forge.py tests/crypt_regex.js /tmp/st_cr.js --passes strip,short,crypt --dev > /dev/null 2>&1 || fail=1
node --check /tmp/st_cr.js > /dev/null 2>&1 || fail=1
python3 -c "
import sys; sys.path.insert(0,'src')
from passes import crypt
out = open('/tmp/st_cr.js').read()
assert '/42' in out and '__f(' not in out, 'REGEX EATEN'
open('/tmp/st_crypt.txt','w').write('CRYPT-REGEX PASS')" || fail=1
say "crypt regex" "$(cat /tmp/st_crypt.txt)"
python3 tools/forge.py tests/nolog.js /tmp/st_nl.js --passes nolog,strip,short,crypt --dev > /dev/null 2>&1 || fail=1
node --check /tmp/st_nl.js > /dev/null 2>&1 || fail=1
python3 -c "
import sys; sys.path.insert(0,'src')
from passes import nolog
out = open('/tmp/st_nl.js').read()
assert 'BANNER' in out, 'keep-log lost'
assert 'strip me' not in out and 'dangling' not in out, 'statement logs leaked'
assert 'console.log' in out, 'expression uses must survive (ternary/expr kept by design)'
open('/tmp/st_nolog.txt','w').write('NOLOG PASS')" || fail=1
say "nolog fixture" "$(cat /tmp/st_nolog.txt)"
python3 -c "
import sys; sys.path.insert(0,'src')
from passes import simp
cases = [
  ('if (true) { foo(); }', '{ foo(); }'),
  ('if (false) { foo(); } else { bar(); }', '{ bar(); }'),
  ('while (false) { foo(); }', ''),
  ('var s = 2 + 3;', 'var s = 5;'),
  ('if (x) { y(); } else if (z) { w(); }', 'if (x) { y(); } else if (z) { w(); }'),
  ('var o = {if(true){y}};', 'var o = {if(!0){y}};'),
]
bad = 0
for src, want in cases:
    got = simp.run(src)
    if got != want: bad += 1; print('SIMP-FAIL', repr(src), '->', repr(got))
open('/tmp/st_simp.txt','w').write('SIMP ' + ('PASS' if bad == 0 else f'FAIL({bad})'))" || fail=1
say "simp behavior" "$(cat /tmp/st_simp.txt)"
python3 -c "
import sys; sys.path.insert(0,'src')
from passes import short
# H2/H3/H4 regression probes: property positions must survive
probes = [
  ('const a1 = 1; const {b1} = o; f(a1, b1);', ['{b1}']),
  ('const a2 = 1; f({a2});', ['{a2}']),
  ('const a3 = 1; var n = 5n; g(a3, n);', ['5n']),
  ('const a4 = 1; var o = {m4() { return a4; }};', ['m4()']),
  ('function h({p5}, [q5], r5) { return r5; }', ['{p5}', '[q5]']),
]
bad = 0
for src, keeps in probes:
    out = short.run(src)
    for k in keeps:
        if k not in out: bad += 1; print('PROBE-FAIL', src, '->', out)
open('/tmp/st_probe.txt','w').write('PROBES ' + ('PASS' if bad == 0 else f'FAIL({bad})'))
" || fail=1
say "short probes" "$(cat /tmp/st_probe.txt)"
[ $fail -eq 0 ] && echo "SELFTEST GREEN" || echo "SELFTEST RED"
exit $fail
