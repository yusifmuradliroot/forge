"use strict";
var step = "boot";
function tick(n) { return n + 1; }
tick(1);
tick(2);
var out = "done";
if (!out) { tick(3); } else { tick(4); }
var i = 0;
while (!0) { i++; if (i > 2) break; }
