<p align="center">
  <strong>tacape</strong>
</p>

<p align="center">
  <img src="./tacape-banner.png" width="474" height="281" alt="Banner do tacape">
</p>

<p align="center">
  Menos novela no output. Ação primeiro. Código que sobrevive ao review.
</p>

<p align="center">
  <a href="https://github.com/mateussatoh/tacape/stargazers"><img src="https://img.shields.io/github/stars/mateussatoh/tacape?style=flat&color=b5651d" alt="Stars"></a>
  <a href="./INSTALL.md"><img src="https://img.shields.io/badge/funciona_com-5_familias_de_agente-b5651d?style=flat" alt="Agentes"></a>
  <a href="./tests/run.sh"><img src="https://img.shields.io/badge/testes-48_passando-4c9a2a" alt="Testes"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/mateussatoh/tacape?style=flat" alt="Licença"></a>
</p>


## O problema

Agentes de código fazem duas coisas ruins: escrevem uma novela para responder uma pergunta simples e mostram a resposta numa ordem confusa. Você ainda precisa encontrar a ação e transformar o texto em plano.

E brevidade sozinha não resolve tudo. Um agente pode responder em três linhas e ainda validar input de forma insegura, esconder erro em log, ignorar webhook duplicado, criar retry sem alerta ou mandar código sem teste.

Tacape junta três camadas:

1. **Compressão:** corta filler, preâmbulo, hedging e repetição.
2. **Estrutura:** ação na primeira linha, passos claros e próximo passo explícito.
3. **Engenharia:** regras para código seguro, testável e fácil de deletar.

Não é linter nem framework. As regras do seu projeto continuam mandando. Tacape entra como convidado, não como bulldozer.

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

### Qualquer outro agente

```bash
curl -fsSL https://raw.githubusercontent.com/mateussatoh/tacape/main/AGENTS.md -o AGENTS.md
```

O arquivo simples não precisa de Node. Hooks precisam de Node 18 ou mais novo. Configuração completa, integrações e desinstalação estão em [INSTALL.md](./INSTALL.md).

Não rode dois plugins de estilo sempre ativos ao mesmo tempo. Eles competem pelo mesmo output.

## As regras que fazem diferença

Tacape não tenta impor gosto pessoal. As regras atacam falhas concretas de produção:

1. **Código chato e pesquisável:** `activateSubscriptionAfterPayment()`, não `process()`.
2. **Abstraia tarde:** repita `canRefundOrder()` e `canCancelSubscription()` até existir regra compartilhada.
3. **Módulos profundos:** `billing.createRenewalCycle(id)` esconde retry, idempotência e persistência.
4. **Código fácil de deletar:** mantenha `createCheckoutExperiment()` isolado do fluxo principal.
5. **Fronteiras de mão única:** `import { billing } from '@/billing'`, nunca `@/billing/internal/tax`.
6. **Falhas visíveis:** `catch (error) { alert.capture(error); throw error }`.
7. **Estados inválidos irrepresentáveis:** `const id = UserId.parse(raw)`, não `raw as UserId`.
8. **Tempo explícito:** `new Date().toISOString()` para guardar, timezone do usuário para renderizar.
9. **Testes que pegariam o bug:** chame o webhook duas vezes e espere um ciclo, não dois.
10. **Texto separado de código:** `t('payment.pending')`, não renderize `'PENDING'`.
11. **Interface completa:** trate `loading`, `error`, lista vazia e dados carregados.
12. **Segredos e destruição:** nunca `console.log(process.env.SECRET)`; confirme antes de deletar produção.
13. **Descoberta antes da edição:** localize `getUser`, leia o teste próximo, depois edite.
14. **Pergunte só quando importa:** decida um default convencional; pergunte antes de apagar dados.
15. **Documentação acompanha contrato:** mudou uma regra? Atualize o documento dono dela.


A precedência é simples: regras visíveis do repositório alvo ganham das regras do Tacape.

## Modos

```text
/tacape:tacape          mostra o nível atual
/tacape:tacape ultra    reduz mais
/tacape:tacape off      desliga estilo, mantém segurança
```

Níveis: `lite`, `full`, `ultra` e `off`. O modo persiste em `~/.claude/.tacape-mode`. Avisos de segurança, ações irreversíveis e explicações completas não são comprimidos de forma irresponsável.

## Guard de escrita

O guard de em dash é opcional na proposta pública e separado da camada de estilo. Quando instalado, bloqueia escrita de prosa com U+2014 em `Write`, `Edit` e `NotebookEdit`. O pre-commit e o CI cobrem caminhos que o hook não vê.

Não é uma regra sobre código, fixtures ou intervalos numéricos. Existe para evitar copy com aparência automática, não para quebrar o repositório.

## Benchmark

Benchmark executado no OMP com `openai-codex/gpt-5.6-terra`, cinco prompts, dois trials por modo e
20 execuções bem-sucedidas. Métrica: mediana de tokens de saída por categoria.

| Categoria | Neutra | Tacape | Diferença |
|---|---:|---:|---:|
| coding | 593 | 540 | 9% menos |
| debugging | 779 | 601 | 23% menos |
| review | 204 | 154 | 25% menos |
| refactor | 544 | 960 | 76% mais |
| explanation | 676 | 490 | 27% menos |
| **geral** | **625** | **490** | **21% menos** |

Tacape reduziu output em quatro categorias. `refactor` foi o ponto ruim: as regras de engenharia
fizeram a resposta crescer 76%. Isso virou próximo alvo de ajuste. Token menor não prova qualidade;
o benchmark mede custo de saída, não correção, clareza ou segurança.

Rode localmente:

```bash
python3 benchmarks/run-omp.py \
  openai-codex/gpt-5.6-terra \
  --trials 2
```

### Refactor real no sandbox

O benchmark real copia uma fixture isolada, permite que o agente leia e edite arquivos, e executa
testes de comportamento depois da mudança. Terra passou quatro de quatro trials, dois neutros e
dois com Tacape.

Casos verificados:

1. retry da mesma entrada antes de avançar;
2. callbacks assíncronos preservando ordem;
3. falha permanente visível, sem processar entradas seguintes.

Esse é o poder útil do Tacape: não apenas resposta curta, mas invariantes explícitos, erro visível,
sequência segura e verificação executável. O resultado ainda não prova que Tacape é melhor que
neutro: ambos passaram todos os casos. A diferença deve ser medida pelo patch produzido, testes e
decisões inventadas, não por tokens isolados.

## Contribua

O projeto está em beta e precisa de código, exemplos e dados melhores.

Boas contribuições:

- adicionar um caso de falha reproduzível;
- melhorar uma regra com exemplo concreto;
- adicionar suporte a outro agente;
- aumentar cobertura do benchmark;
- corrigir documentação ou instalação;
- abrir issue com output antes e depois.

Antes de abrir PR:

```bash
bash tests/run.sh
```

PRs pequenos são melhores. Explique qual problema observável muda, inclua teste quando houver contrato novo e não altere regra apenas por preferência estética.

## Skills

| Skill | Uso |
|---|---|
| `tacape` | Compressão e estrutura em toda sessão |
| `tacape-code` | Escrever, refatorar e revisar código |
| `tacape-commit` | Criar mensagens Conventional Commits |
| `tacape-review` | Revisar diff e ordenar achados por severidade |

## Licença

MIT.

https://github.com/mateussatoh/tacape
