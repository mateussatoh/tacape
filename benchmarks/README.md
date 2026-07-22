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

A saída mostra tokens de saída de `neutral` e `tacape`, além da diferença percentual contra neutro.
Token menor não prova resposta melhor. Use benchmark de qualidade separado para medir correção,
ação, segurança e clareza.
