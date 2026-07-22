#!/usr/bin/env python3
import argparse, json, shutil, subprocess, tempfile, time
from pathlib import Path

ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixtures" / "refactor-pipeline"
PROMPT = """You are editing a real isolated fixture. Refactor imports.js from callbacks to async functions.
Preserve observable behavior: files run in input order, a transient file failure retries that same file
before the next file, and a permanent failure remains visible to the caller. Do not add concurrency,
logging, progress callbacks, new domain policy, or dependencies. Inspect files, edit imports.js, and run
node imports.test.js. Finish only after the test passes."""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--trials", type=int, default=2)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--output", default="benchmarks/results-refactor-sandbox.jsonl")
    args = p.parse_args()
    out = Path(args.output)
    with out.open("w") as f:
        for trial in range(1, args.trials + 1):
            sandbox = Path(tempfile.mkdtemp(prefix="tacape-refactor-"))
            shutil.copytree(FIXTURE, sandbox / FIXTURE.name)
            cwd = sandbox / FIXTURE.name
            started = time.perf_counter()
            command = ["omp", "-p", "--mode", "json", "--model", args.model, PROMPT]
            try:
                result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=args.timeout)
                answer = result.stdout[-12000:]
                test = subprocess.run(["node", "imports.test.js"], cwd=cwd, capture_output=True, text=True)
                row = {"model": args.model, "trial": trial, "ok": test.returncode == 0,
                       "duration_ms": round((time.perf_counter() - started) * 1000),
                       "agent_exit": result.returncode, "test_exit": test.returncode,
                       "answer": answer, "test_output": (test.stdout + test.stderr)[-4000:]}
            except subprocess.TimeoutExpired as error:
                row = {"model": args.model, "trial": trial, "ok": False, "error": str(error)}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(json.dumps({k: row[k] for k in row if k not in {"answer", "test_output"}}), flush=True)
            shutil.rmtree(sandbox, ignore_errors=True)

if __name__ == "__main__":
    main()
