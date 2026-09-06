// runner battery: node tests/check_runner.js
// asserts b() byte-exact on multibyte cases (all 6 manifest orders) + refusals.
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
eval(fs.readFileSync(path.join(ROOT, 'src', 'runner', 'forgescript.js'), 'utf8'));
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, 'battery_multibyte.json'), 'utf8'));
let fail = 0;
for (const [src, data] of cases) {
    if (ForgeScript.b(data) !== src) { fail++; console.log('FAIL decrypt case'); }
}
for (const bad of ['hello', 'FS:1\n00', 'FS:2\n{}\n', 'FS:2\n{"o":[0],"s":"x"}\n']) {
    if (ForgeScript.b(bad) !== null || ForgeScript.run(bad) !== null) { fail++; console.log('FAIL refusal'); }
}
// tampered blob must refuse (sig covers ciphertext)
const [src0, data0] = cases[0];
const lines = data0.split('\n');
lines[2] = (lines[2][0] === 'A' ? 'B' : 'A') + lines[2].slice(1);
if (ForgeScript.b(lines.join('\n')) !== null) { fail++; console.log('FAIL tamper accepted'); }
console.log(fail === 0 ? `RUNNER-BATTERY PASS (${cases.length} cases)` : `RUNNER-BATTERY FAIL (${fail})`);
process.exit(fail ? 1 : 0);
