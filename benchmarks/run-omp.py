#!/usr/bin/env python3
"""Benchmark neutral versus Tacape through the local OMP CLI.

Runs each requested model explicitly. A fallback model or provider error is recorded as a failed
trial instead of being silently counted under the requested model.
"""
import argparse
import hashlib
import json
import statistics
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROMPTS = ROOT / "benchmarks" / "prompts.json"
SKILL = ROOT / "skills" / "tacape" / "SKILL.md"


def run_turn(model, instructions, prompt, timeout):
    command = [
        "omp", "-p", "--no-tools", "--no-session", "--no-title", "--no-lsp",
        "--thinking", "off", "--mode", "json", "--model", model,
        "--system-prompt", instructions, prompt,
    ]
    started = time.perf_counter()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        return {"ok": False, "error": f"timeout after {timeout}s", "duration_ms": round((time.perf_counter() - started) * 1000)}

    duration_ms = round((time.perf_counter() - started) * 1000)
    answer = ""
    usage = {}
    actual_model = model
    error = None
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") in {"message_end", "turn_end"}:
            message = event.get("message", {})
            if message.get("role") == "assistant":
                content = message.get("content", [])
                answer = "".join(block.get("text", "") for block in content if block.get("type") == "text") or answer
                usage = message.get("usage", usage)
                actual_model = f"{message.get('provider', '')}/{message.get('model', '')}".strip("/") or actual_model
                if message.get("stopReason") == "error":
                    error = message.get("errorMessage", "model error")
    if result.returncode != 0 and not error:
        error = result.stderr.strip()[-1000:] or f"omp exited {result.returncode}"
    return {
        "ok": error is None and bool(answer),
        "model": actual_model,
        "answer": answer,
        "usage": usage,
        "output_tokens": usage.get("output", 0),
        "input_tokens": usage.get("input", 0),
        "duration_ms": duration_ms,
        **({"error": error} if error else {}),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("models", nargs="+", help="OMP provider/model selectors")
    parser.add_argument("--trials", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", default="benchmarks/results-omp.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    prompts = json.loads(PROMPTS.read_text())
    modes = {"neutral": "You are a helpful coding assistant.", "tacape": SKILL.read_text()}
    calls = len(args.models) * len(prompts) * len(modes) * args.trials
    if args.dry_run:
        print(json.dumps({"models": args.models, "prompts": len(prompts), "trials": args.trials, "modes": list(modes), "calls": calls, "tacape_sha256": hashlib.sha256(modes["tacape"].encode()).hexdigest()}, indent=2))
        return

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with output_path.open("w") as output:
        for model in args.models:
            for item in prompts:
                for mode, instructions in modes.items():
                    for trial in range(1, args.trials + 1):
                        print(f"{model} {item['id']} {mode} trial {trial}/{args.trials}", flush=True)
                        result = run_turn(model, instructions, item["prompt"], args.timeout)
                        row = {"model_requested": model, "prompt_id": item["id"], "category": item["category"], "mode": mode, "trial": trial, "ruleset_sha256": hashlib.sha256(modes["tacape"].encode()).hexdigest(), **result}
                        output.write(json.dumps(row, ensure_ascii=False) + "\n")
                        output.flush()
                        rows.append(row)

    successful = [row for row in rows if row["ok"]]
    print(f"\nSaved {len(rows)} runs to {output_path}")
    print(f"Successful: {len(successful)}  Failed: {len(rows) - len(successful)}")
    for model in args.models:
        for mode in modes:
            values = [row["output_tokens"] for row in successful if row["model_requested"] == model and row["mode"] == mode]
            if values:
                print(f"{model} {mode}: median output tokens {statistics.median(values):.0f}")


if __name__ == "__main__":
    main()
