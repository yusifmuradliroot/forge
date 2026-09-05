// fixture: comments must go, strings must survive
const url = "https://example.com/x"; // trailing comment
const q = '// not a comment';
/* block
   comment */
const t = `template /* still code */`;
console.log(url, q, t); // done
