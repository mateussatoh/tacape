# Tacape benchmark

Compara resposta neutra com Tacape. O objetivo é medir o custo e o efeito do ruleset, não disputar
qual plugin fala menos.

O benchmark usa OpenAI Responses API, mesmo modelo, mesmo conjunto de prompts, formato fixo de
requisição, trials repetidos e mediana de tokens de saída. Registra também SHA256 do ruleset Tacape.
Resultados dependem do modelo, prompts e quantidade de trials.

## Dry run

```bash
python3 benchmarks/run-openai.py --dry-run
```

## Execução real

```bash
OPENAI_API_KEY=... OPENAI_MODEL=gpt-5.6 python3 benchmarks/run-openai.py --trials 3
```

## Neutral versus Tacape through OMP

```bash
python3 benchmarks/run-omp.py \
  openai-codex/gpt-5.6-terra \
  github-copilot/gpt-4.1 \
  opencode-go/glm-5.2 \
  --trials 2
```

The runner creates a fresh no-tools, no-session turn for every model, prompt, mode and trial. It
writes raw JSONL results and records failed providers separately. A provider fallback is not counted
as a successful run for the requested model.

## Quality-focused refactor benchmark

```bash
python3 benchmarks/run-omp.py \
  openai-codex/gpt-5.6-terra \
  --prompts benchmarks/quality-prompts.json \
  --trials 2 \
  --output benchmarks/results-quality-terra.jsonl
```

This isolates two quality gates: asking for missing context and applying a minimal refactor to
provided code. Review responses for correctness, invariant preservation, applicability, and
unnecessary invention. Token count is not a quality score.

## Real refactor sandbox

```bash
python3 benchmarks/run-refactor-sandbox.py \
  openai-codex/gpt-5.6-terra \
  --trials 2
```

Each trial copies isolated fixture, lets model inspect and edit real files with tools, then runs
fixture tests. A passing response must preserve ordering, retry same file, and expose permanent
failure. This measures applied behavior, not hypothetical code in prompt output.

Expanded fixture cases now verify:

1. transient failure retries same file before advancing;
2. delayed callbacks still preserve input order;
3. permanent failure remains visible and stops later files.

## Casos onde Tacape deve brilhar

`command-boundary` testa uma correção de segurança real: remover shell injection sem esconder
falhas, perder stdout ou alterar exit codes.

```bash
python3 benchmarks/run-refactor-sandbox.py \
  openai-codex/gpt-5.6-terra \
  --fixture command-boundary \
  --mode tacape \
  --trials 1
```

A saída mostra tokens de saída de `neutral` e `tacape`, além da diferença percentual contra neutro.

## Hardened contract

The sandbox verifies baseline failure, freezes test-file hashes, rejects test edits, runs unchanged
tests after the agent edit, and records implementation diffs. A passing test alone is insufficient.
Terra passed one neutral and one Tacape trial under this contract.

## Public headline

Using the same five prompts and the same `openai-codex/gpt-5.6-terra` model, Tacape produced a
median of 490 output tokens versus 625 with neutral instructions across 20 successful runs:
**21% fewer output tokens**.

This is an output-efficiency result. The benchmark does not claim that fewer tokens alone prove
better answers; answer quality is evaluated separately. Audience-facing artifacts are exempt from
Caveman compression and must remain natural and complete.
Token menor não prova resposta melhor. Use benchmark de qualidade separado para medir correção,
ação, segurança e clareza.
