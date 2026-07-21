# tacape

A Claude Code plugin that shapes how the agent answers and how it writes code.

Three layers, one install:

1. **Compression.** Cuts articles, filler, hedging, preamble and closers.
2. **Structure.** The answer is shaped so the next action is the first thing you read.
3. **Principles.** Language-agnostic engineering rules applied while writing and reviewing code.

Plus a hard ban on U+2014, the em dash, enforced by a hook rather than by a prompt rule that drifts.

A *tacape* is a wooden war club. Blunt, short, gets the job done.

## Inspiration

tacape stands on two plugins that each solved one half of the problem:

- **[caveman](https://github.com/JuliusBrussee/caveman)** by Julius Brussee, for the compression
  layer. It proved that an agent can drop most of its words without losing any technical substance,
  and that the ruleset has to be re-injected every session or the model drifts back to verbose.
- **[i-have-adhd](https://github.com/ayghri/i-have-adhd)** by ayghri, for the structure layer.
  It makes the point that brevity is not enough: a short answer with the action buried at the
  bottom is still a wall. Lead with what to do, number the steps, end with one next action.

The two are orthogonal. Compression is about how words look, structure is about where things go.
Running both as separate always-on plugins means two style prompts competing, so tacape merges
them into one ruleset and adds the parts neither covers: the em dash ban and the code principles.

## Install

```bash
claude plugin marketplace add mateussatoh/tacape
claude plugin install tacape
```

From a local checkout:

```bash
claude plugin marketplace add ~/dev/tacape
claude plugin install tacape
```

Do not run tacape alongside another always-on output-style plugin. Two `SessionStart` hooks
injecting competing style rules produce drift, not a blend.

## Levels

| Level | Output |
|---|---|
| `lite` | Full grammar. Filler, hedging, preamble and closers gone. Structure rules at full force. |
| `full` | Articles dropped, fragments allowed, short synonyms. Default. |
| `ultra` | Telegraphic. Bullets over sentences. |
| `off` | Style layer disabled. The em dash guard stays on. |

```
/tacape          show the current level
/tacape ultra    switch
/tacape off      disable the style layer
```

The level persists in `~/.claude/.tacape-mode`. Override for one session with `TACAPE_LEVEL=ultra`.

The style layer stands down on its own for security warnings, irreversible actions, and any
sequence where dropped words would make the order ambiguous. Safety beats brevity, always.

## Skills

| Skill | Fires on |
|---|---|
| `tacape` | Always, via `SessionStart`. The style layer. |
| `tacape-code` | Writing, refactoring or reviewing code in any language. The principles. |
| `tacape-commit` | "write a commit", `/tacape-commit`. Conventional Commits, 50 char subject. |
| `tacape-review` | "review this diff", `/tacape-review`. One line per finding, severity ranked. |

`tacape-code` is stack-agnostic on purpose: no framework, no language, no project assumptions.
It covers boundaries, error visibility, abstraction timing, test honesty, validation at the edge,
time handling, and discovery order. It always yields to a repo's own `CLAUDE.md` or `AGENTS.md`,
and to conventions already visible in the surrounding code.

## The em dash guard

A `PreToolUse` hook on `Write`, `Edit` and `NotebookEdit`. If the payload contains U+2014 the write
is denied, with an explanation, before anything reaches disk.

Why a hook and not a rule: a prompt rule is advisory and decays over a long session. A hook does
not have opinions. It also catches the character arriving from a paste or a generated template,
which no prompt rule ever could.

Escape hatch, for a repo that legitimately needs the character, such as quoting a source verbatim:

```bash
TACAPE_ALLOW_EMDASH=1 claude
```

The guard is independent of the style level. `/tacape off` does not disable it.

## What it deliberately does not do

- No token accounting or savings dashboard.
- No statusline. Add one yourself if you want a badge.
- No subagents. It shapes output and encodes principles, nothing more.

## License

MIT.
