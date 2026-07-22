#!/usr/bin/env python3
import argparse, hashlib, json, shutil, subprocess, tempfile, time
from pathlib import Path

ROOT = Path(__file__).parent
PROMPTS = {
    "refactor-pipeline": "Inspect implementation and tests. Fix imports.js. Preserve input order, retry same file, visible permanent failure. Do not edit tests. Run node imports.test.js.",
    "command-boundary": "Inspect implementation and tests. Fix run-command.js so arguments cannot trigger shell injection. Preserve stdout, exit code, and error visibility. Do not edit tests. Run node run-command.test.js.",
}
TEST_FILES = {"refactor-pipeline": "imports.test.js", "command-boundary": "run-command.test.js"}
IMPLEMENTATION_FILES = {"refactor-pipeline": ["imports.js"], "command-boundary": ["run-command.js"]}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    test_file = TEST_FILES[args.fixture]
    implementation_files = IMPLEMENTATION_FILES[args.fixture]
    instructions = "You are a helpful coding assistant."
    if args.mode == "tacape":
        instructions = (ROOT.parent / "skills" / "tacape" / "SKILL.md").read_text()
    out = Path(args.output)
    with out.open("w") as f:
        for trial in range(1, args.trials + 1):
            sandbox = Path(tempfile.mkdtemp(prefix="tacape-refactor-"))
            shutil.copytree(fixture, sandbox / fixture.name)
            cwd = sandbox / fixture.name
            test_path = cwd / test_file
            test_hash = digest(test_path)
            baseline = subprocess.run(["node", test_file], cwd=cwd, capture_output=True, text=True)
            started = time.perf_counter()
            command = ["omp", "-p", "--mode", "json", "--model", args.model,
                       "--system-prompt", instructions, PROMPTS[args.fixture]]
            try:
                result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=args.timeout)
                test_unchanged = digest(test_path) == test_hash
                post = subprocess.run(["node", test_file], cwd=cwd, capture_output=True, text=True)
                diffs = {}
                for name in implementation_files:
                    before = (fixture / name).read_text()
                    after = (cwd / name).read_text()
                    diffs[name] = {"changed": before != after, "before": before, "after": after}
                ok = baseline.returncode != 0 and test_unchanged and post.returncode == 0
                row = {"model": args.model, "mode": args.mode, "fixture": args.fixture, "trial": trial,
                       "ok": ok, "baseline_failed": baseline.returncode != 0,
                       "tests_unchanged": test_unchanged, "duration_ms": round((time.perf_counter() - started) * 1000),
                       "agent_exit": result.returncode, "test_exit": post.returncode,
                       "diffs": diffs, "answer": result.stdout[-12000:],
                       "test_output": (post.stdout + post.stderr)[-4000:]}
            except subprocess.TimeoutExpired as error:
                row = {"model": args.model, "mode": args.mode, "fixture": args.fixture,
                       "trial": trial, "ok": False, "error": str(error)}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(json.dumps({k: row[k] for k in row if k not in {"answer", "test_output", "diffs"}}), flush=True)
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    main()
