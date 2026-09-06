// crypt must never touch regex content (quotes inside /.../ are not strings).
const m1 = str.match(/42\["(10|34)",("[^"]+"|[^,\]]+)/);
const m2 = s.replace(/__voyagerHash\s*=\s*['"][^'"]{8}['"]/, 'x');
const re = /ab+"cd"+/g;
