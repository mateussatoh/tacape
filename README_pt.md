# tacape

> Um tacape é curto, direto e encerra a conversa.

`tacape` combina compressão de respostas, estrutura amigável para atenção e convenções de engenharia para agentes de programação.

[English](./README.md)

## O problema não é só falar demais

É um pouco.

Imagine a resposta de um agente como uma negociação. Uma parte sabe a resposta. Outra quer explicar cada caso extremo. Uma terceira quer parecer prestativa antes de fazer algo útil.

O resultado: você pede uma correção, recebe um pequeno ensaio e encontra a ação necessária escondida no fim. Entendeu. Ainda não começou.

Existe uma versão pior. A resposta é curta, a ação vem primeiro, mas o código continua errado: valida a entrada e faz cast mesmo assim, captura falhas em um log que ninguém monitora ou envia sem teste.

São três falhas:

1. Volume esconde o fato.
2. Ordem esconde a ação.
3. Engenharia fraca esconde o defeito.

`tacape` trata as três:

| Camada | Corrige |
|---|---|
| Compressão | Filler, preâmbulo, repetição e ruído |
| Estrutura | Ação na primeira linha, passos numerados e próximo passo único |
| Princípios | Validação na borda, erros visíveis, testes honestos e mudanças deletáveis |

## Instalação

### Claude Code

```bash
claude plugin marketplace add mateussatoh/tacape
claude plugin install tacape@tacape
```

### Codex

```bash
codex plugin marketplace add mateussatoh/tacape --ref main
codex plugin add tacape@tacape
```

### Gemini CLI

```bash
gemini extensions install https://github.com/mateussatoh/tacape
```

Outros agentes podem usar `AGENTS.md` diretamente.

## Níveis

| Nível | Comportamento |
|---|---|
| `lite` | Remove filler e mantém frases completas |
| `full` | Padrão. Direto, compacto e legível |
| `ultra` | Mínimo de palavras, máximo de ação |
| `off` | Desliga estilo. Guard permanece ativo |

No Claude Code:

```text
/tacape:tacape
/tacape:tacape ultra
/tacape:tacape off
```

## Guard de escrita

O hook do Claude Code bloqueia caracteres de travessão proibidos em `Write`, `Edit` e `NotebookEdit`. O pre-commit e o CI verificam caminhos que o hook não enxerga.

O guard não aprova automaticamente uma escrita limpa. Ele não emite saída e deixa a permissão normal continuar.

## Princípios de código

- Prefira código óbvio, pesquisável e fácil de editar.
- Abstraia tarde. Duas repetições não formam uma arquitetura.
- Empurre complexidade para módulos profundos.
- Faça mudanças fáceis de deletar.
- Mantenha limites entre módulos em uma direção.
- Mantenha falhas visíveis.
- Valide uma vez na borda e confie internamente.
- Separe decisão pura de efeito.
- Teste falhas, limites e comportamento observável.
- Nunca esconda segredo ou ação destrutiva.

As regras completas estão em [`skills/tacape-code/SKILL.md`](./skills/tacape-code/SKILL.md).

## Comparação das skills

```bash
python3 benchmarks/run-openai.py --dry-run
OPENAI_API_KEY=... python3 benchmarks/run-openai.py
```

O benchmark compara respostas neutras com Caveman, i-have-adhd e tacape usando os mesmos prompts,
modelo, temperatura zero e trials repetidos. Resultado mede este conjunto de prompts, não superioridade universal.

## Licença

MIT.
