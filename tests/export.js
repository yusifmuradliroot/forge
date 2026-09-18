// export fixture: exported bindings keep their names (importers must match),
// locals still shorten, runtime stays identical.
export function kept_fn(a) { return a + 1; }
export const kept_val = 41;
const local_add = kept_fn(kept_val);
console.log(local_add); // keep-log
