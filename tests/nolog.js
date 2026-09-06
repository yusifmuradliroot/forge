// nolog torture: statements stripped, expressions kept, keep-log survives,
// if/else bodies stay valid.
console.log('strip me');
if (x) console.error('dangling if');
else console.warn('dangling else');
while (y) console.log('dangling while');
y ? console.log('ternary') : z;
const q = console.log('expr') + 1;
// console.log('in comment');
console.log('%cBANNER', 'color:red'); // keep-log
