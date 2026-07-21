#!/usr/bin/env python3
"""Measure neutral versus tacape response output with Anthropic usage metadata."""
import argparse
import hashlib
import json
import os
import statistics
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROMPTS = Path(__file__).parent / "prompts.json"
SKILL = ROOT / "skills" / "tacape" / "SKILL.md"
API = "https://api.anthropic.com/v1/messages"


def call(model, system, prompt):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY is required; use --dry-run without it")
    body = json.dumps({"model": model, "max_tokens": 2048, "temperature": 0, "system": system, "messages": [{"role": "user", "content": prompt}]}).encode()
    request = urllib.request.Request(API, data=body, headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.load(response)
    return data["usage"]["input_tokens"], data["usage"]["output_tokens"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    prompts = json.loads(PROMPTS.read_text())
    if args.dry_run:
        print(f"model: {args.model}\nprompts: {len(prompts)}\ntrials: {args.trials}\nAPI calls: {len(prompts) * args.trials * 2}")
        return
    tacape = SKILL.read_text()
    rows = []
    for item in prompts:
        normal, compact = [], []
        for _ in range(args.trials):
            normal.append(call(args.model, "You are a helpful coding assistant.", item["prompt"])[1])
            compact.append(call(args.model, tacape, item["prompt"])[1])
        normal_median = statistics.median(normal)
        tacape_median = statistics.median(compact)
        savings = round((1 - tacape_median / normal_median) * 100) if normal_median else 0
        rows.append({"id": item["id"], "normal": normal_median, "tacape": tacape_median, "savings_pct": savings})
    print("| Prompt | Normal output tokens | Tacape output tokens | Saved |")
    print("|---|---:|---:|---:|")
    for row in rows:
        print(f"| {row['id']} | {row['normal']} | {row['tacape']} | {row['savings_pct']}% |")
    print(f"\nRuleset SHA256: {hashlib.sha256(SKILL.read_bytes()).hexdigest()}")
    print(f"Average savings: {round(statistics.mean(row['savings_pct'] for row in rows))}%")


if __name__ == "__main__":
    main()
