// mangle torture: shadowing must NOT rename, properties/keys must survive
function outer(alpha) {
    const beta = alpha + 1;
    function inner(alpha) {
        return alpha * 2; // shadowed param, and outer alpha used twice -> skip both
    }
    const obj = { beta: 1, gamma: beta };
    console.log(obj.beta, obj.gamma);
    const url = "https://x.y/beta";
    const re = /beta(gamma)?/g;
    return inner(beta) + url.length + String(re);
}
const result = outer(21);
