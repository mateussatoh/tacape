#!/usr/bin/env python3
import argparse, json, shutil, subprocess, tempfile, time
from pathlib import Path

ROOT = Path(__file__).parent
PROMPTS = {
    "refactor-pipeline": "Inspect files, refactor imports.js from callbacks to async functions. Preserve input order, retry same file, visible permanent failure, and run node imports.test.js.",
    "command-boundary": "Inspect files, fix run-command.js so arguments cannot trigger shell injection. Preserve stdout, exit code, and error visibility. Do not suppress errors. Run node run-command.test.js.",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--mode", choices=("neutral", "tacape"), default="tacape")
    parser.add_argument("--fixture", choices=tuple(PROMPTS), default="refactor-pipeline")
    parser.add_argument("--trials", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--output", default="benchmarks/results-refactor-sandbox.jsonl")
    args = parser.parse_args()
    fixture = ROOT / "fixtures" / args.fixture
    test_file = "imports.test.js" if args.fixture == "refactor-pipeline" else "run-command.test.js"
    instructions = "You are a helpful coding assistant."
    if args.mode == "tacape":
        instructions = (ROOT.parent / "skills" / "tacape" / "SKILL.md").read_text()
    out = Path(args.output)
    with out.open("w") as f:
        for trial in range(1, args.trials + 1):
            sandbox = Path(tempfile.mkdtemp(prefix="tacape-refactor-"))
            shutil.copytree(fixture, sandbox / fixture.name)
            cwd = sandbox / fixture.name
            started = time.perf_counter()
            command = ["omp", "-p", "--mode", "json", "--model", args.model,
                       "--system-prompt", instructions, PROMPTS[args.fixture]]
            try:
                result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=args.timeout)
                test = subprocess.run(["node", test_file], cwd=cwd, capture_output=True, text=True)
                row = {"model": args.model, "mode": args.mode, "fixture": args.fixture, "trial": trial,
                       "ok": test.returncode == 0, "duration_ms": round((time.perf_counter() - started) * 1000),
                       "agent_exit": result.returncode, "test_exit": test.returncode,
                       "answer": result.stdout[-12000:], "test_output": (test.stdout + test.stderr)[-4000:]}
            except subprocess.TimeoutExpired as error:
                row = {"model": args.model, "mode": args.mode, "fixture": args.fixture,
                       "trial": trial, "ok": False, "error": str(error)}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(json.dumps({k: row[k] for k in row if k not in {"answer", "test_output"}}), flush=True)
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    main()
