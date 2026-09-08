// forge example: build with ./forge hello.js hello.fs -- then run hello.fs.
// The `keep-log` comment exempts this line from the nolog pass;
// without it the console.* statement would be stripped (silence is default).
function greet(name) {
  var message = "hello brave world, welcome ";
  return message + name;
}
console.log(greet("ada")); // keep-log
