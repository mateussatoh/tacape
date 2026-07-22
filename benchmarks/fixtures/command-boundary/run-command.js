import { spawn } from "node:child_process";

export function runCommand(command, args, done) {
  const child = spawn(command, args, { shell: true });
  let output = "";
  child.stdout.on("data", (chunk) => { output += chunk; });
  child.on("close", (code) => done(null, { code, output }));
  child.on("error", (error) => done(error));
}
