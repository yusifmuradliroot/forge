// regex vs division torture
var g = 1;
var a = b / c / 2;
var r1 = s.replace(/\s+/g, "");
var r2 = /ab+c/gi.test(s);
var r3 = x ? /y/ : /z/m;
function f() { return /w+/; }
console.log(g, a, r1, r2, r3, f);
