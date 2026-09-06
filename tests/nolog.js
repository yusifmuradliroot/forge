// nolog torture: statements stripped, expressions kept, keep-log survives.
console.log('strip me');
console.warn('strip me too');
const x = console.log('keep: expression value') + 1;
w.console.log('keep: prop access');
setTimeout(console.log, 100);
console.log('%cBANNER', 'color:red'); // keep-log
