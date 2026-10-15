// template-inner fixture: live ${} strings are protected, template TEXT middles
// between `}` and `${` stay verbatim (an __f() call there is a syntax error).
var who = "world";
var live = `x${who + "this is a very long string value"}w`;
var mid = `a${who}"b"${who}c`;
console.log(live, mid); // keep-log
