# Tacape benchmarks

## Skills comparison

`run-openai.py` compares four instruction sets on identical prompts:

- neutral system prompt;
- Caveman;
- i-have-adhd;
- Tacape.

Both reference repositories are optional inputs. Defaults expect local comparison clones at:

```text
/tmp/caveman-reference/skills/caveman/SKILL.md
/tmp/i-have-adhd-reference/skills/i-have-adhd/SKILL.md
```

Dry run, no network:

```bash
python3 benchmarks/run-openai.py --dry-run
```

Real OpenAI run:

```bash
OPENAI_API_KEY=... OPENAI_MODEL=gpt-5.6 python3 benchmarks/run-openai.py
```

Override reference paths:

```bash
python3 benchmarks/run-openai.py \
  --caveman-skill /path/to/caveman/SKILL.md \
  --adhd-skill /path/to/i-have-adhd/SKILL.md
```

The benchmark uses OpenAI Responses API, fixed request shape, repeated trials, median output tokens, and records Tacape ruleset SHA256. It reports measurements, not promises. Results depend on model, prompt set, and trial count.
