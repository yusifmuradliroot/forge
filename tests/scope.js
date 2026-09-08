function outer(total) {
  function bonus(total) { return total + 1; }
  function plain(a, b) { return a * b + total; }
  var r = bonus(total) + plain(3, 4);
  console.log("SCOPE", r);
}
outer(10);
function sib1(v) { return v + 1; }
function sib2(v) { return v * 2; }
console.log("SIB", sib1(5), sib2(5));
function guarded(x) {
  function inner(x) { return eval("x"); }
  return inner(x);
}
console.log("GUARD", guarded(7));
