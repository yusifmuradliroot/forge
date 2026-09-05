// end-to-end fixture: raw JS -> .fs -> runner -> identical behavior
const greeting = "hello packed world, this is a longer string";
function add(a, b) { return a + b; }
console.log(greeting, add(20, 22));
