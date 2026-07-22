import { strict as assert } from "node:assert";
import { runCommand } from "./run-command.js";

const result = await new Promise((resolve, reject) => {
  runCommand(process.execPath, ["-e", "process.stdout.write(process.argv[1])", "safe;touch SHOULD_NOT_EXIST"], (error, value) => {
    if (error) reject(error);
    else resolve(value);
  });
});

assert.equal(result.code, 0);
assert.equal(result.output, "safe;touch SHOULD_NOT_EXIST");
console.log("command boundary tests passed");
