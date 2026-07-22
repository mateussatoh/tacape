import { strict as assert } from "node:assert";
import { importFiles } from "./imports.js";

function runImport(files, failures = new Set(), permanent = new Set()) {
  const calls = [];
  const attempts = new Map();
  return new Promise((resolve, reject) => {
    importFiles(files, (file, callback) => {
      calls.push(file);
      const count = (attempts.get(file) ?? 0) + 1;
      attempts.set(file, count);
      if (permanent.has(file) || (failures.has(file) && count === 1)) {
        callback(new Error(`temporary ${file}`));
      } else {
        callback();
      }
    }, (error) => error ? reject(Object.assign(error, { calls })) : resolve({ calls, attempts }));
  });
}

const result = await runImport(["a", "b"], new Set(["a"]));
assert.deepEqual(result.calls, ["a", "a", "b"]);
assert.equal(result.attempts.get("a"), 2);
assert.equal(result.attempts.get("b"), 1);

await assert.rejects(
  runImport(["a", "b"], new Set(), new Set(["a"])),
  /temporary a/,
);
console.log("fixture tests passed");
