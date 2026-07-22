#!/usr/bin/env python3
"""Compare neutral, Caveman, ADHD, and Tacape instructions with OpenAI Responses API."""
import argparse
import hashlib
import json
import os
import statistics
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROMPTS = Path(__file__).parent / "prompts.json"
API = "https://api.openai.com/v1/responses"


def read_skill(path):
    return Path(path).read_text()


def call(model, instructions, prompt):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY is required; use --dry-run without it")
    payload = json.dumps({"model": model, "instructions": instructions, "input": prompt}).encode()
    request = urllib.request.Request(API, data=payload, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        raise SystemExit(f"OpenAI API HTTP {error.code}: {detail[:500]}") from error
    usage = data.get("usage", {})
    return usage.get("output_tokens", 0), usage.get("input_tokens", 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5.6"))
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    prompts = json.loads(PROMPTS.read_text())
    modes = {
        "neutral": "You are a helpful coding assistant.",
        "tacape": read_skill(ROOT / "skills/tacape/SKILL.md"),
    }
    if args.dry_run:
        print(f"model: {args.model}")
        print(f"prompts: {len(prompts)}")
        print(f"trials: {args.trials}")
        print(f"API calls: {len(prompts) * args.trials * len(modes)}")
        print(f"tacape sha256: {hashlib.sha256(modes['tacape'].encode()).hexdigest()}")
        return

    totals = {mode: [] for mode in modes}
    for item in prompts:
        row = {mode: [] for mode in modes}
        for mode, instructions in modes.items():
            for _ in range(args.trials):
                output_tokens, _ = call(args.model, instructions, item["prompt"])
                row[mode].append(output_tokens)
                totals[mode].append(output_tokens)
        medians = {mode: statistics.median(values) for mode, values in row.items()}
        baseline = medians["neutral"]
        print(f"{item['id']}: " + ", ".join(f"{mode}={int(value)}" for mode, value in medians.items()) + f", tacape_vs_neutral={round((1 - medians['tacape'] / baseline) * 100) if baseline else 0}%")

    medians = {mode: statistics.median(values) for mode, values in totals.items()}
    baseline = medians["neutral"]
    print("\n| Mode | Median output tokens | Versus neutral |")
    print("|---|---:|---:|")
    for mode, value in medians.items():
        savings = round((1 - value / baseline) * 100) if baseline else 0
        print(f"| {mode} | {int(value)} | {savings}% |")
    print(f"\nModel: {args.model}")
    print(f"Tacape SHA256: {hashlib.sha256(modes['tacape'].encode()).hexdigest()}")


if __name__ == "__main__":
    main()
