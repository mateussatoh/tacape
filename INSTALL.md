# Install

tacape ships in three shapes so it works on any agent:

| Shape | File | Who reads it |
|---|---|---|
| Claude Code plugin | `.claude-plugin/plugin.json` | Claude Code. Hooks, skills, slash command. |
| Codex plugin | `.codex-plugin/plugin.json` | Codex. Skills. |
| Gemini extension | `gemini-extension.json` | Gemini CLI. Context file. |
| Plain instruction file | `AGENTS.md` | Everything else. Cursor, Windsurf, Cline, Copilot, Aider, Zed, OpenCode, and any agent that reads an instruction file. |

`AGENTS.md` is the portable ruleset for agents with no plugin system. `CLAUDE.md` and `GEMINI.md`
are one-line pointers to it.

`AGENTS.md` and `skills/tacape/SKILL.md` are two hand-maintained copies of the same rules, because
the plugin reads the skill at runtime and other agents cannot. They are kept in step by assertions
in `tests/run.sh` that fail the build when a rule is present in one and missing from the other.
That is a weaker guarantee than generating one from the other, and it is the honest description of
what is there. Change a rule in one, change it in the other, in the same commit.

Only the Claude Code plugin currently ships the write-time guard. Everywhere else the ban is a rule
in `AGENTS.md`, which is advisory.

---

## Claude Code

```bash
claude plugin marketplace add mateussatoh/tacape
claude plugin install tacape@tacape
```

Restart the session. Hooks load at `SessionStart`.

You get: the style layer always on, four skills, `/tacape:tacape` to switch levels, and the em dash guard
on every `Write`, `Edit` and `NotebookEdit`.

> Do not run tacape alongside another always-on output-style plugin. Two `SessionStart` hooks
> injecting competing style rules produce drift, not a blend. Uninstall the other one first, and
> check `~/.claude/settings.json` for a leftover standalone install: a plugin uninstall does not
> remove hooks that were written directly into settings.

## Codex

```bash
codex plugin marketplace add mateussatoh/tacape --ref main
codex plugin add tacape@tacape
```

The first line only registers the marketplace. Without the second, `codex plugin list` shows
`tacape@tacape  not installed`.

Or drop `AGENTS.md` at the root of your project, which Codex reads natively.

## Gemini CLI

```bash
gemini extensions install https://github.com/mateussatoh/tacape
```

The extension points Gemini at `AGENTS.md` through `contextFileName`.

## Cursor, Windsurf, Cline, Copilot, Aider, Zed, and the rest

Every one of these reads a plain instruction file. Point it at `AGENTS.md`.

```bash
# from your project root
curl -fsSL https://raw.githubusercontent.com/mateussatoh/tacape/main/AGENTS.md -o AGENTS.md
```

Then wire it up if your agent uses a different filename:

| Agent | Expected file |
|---|---|
| Cursor | `.cursor/rules/tacape.mdc` or `.cursorrules` |
| Windsurf | `.windsurfrules` |
| Cline | `.clinerules` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Aider | `CONVENTIONS.md`, referenced with `--read` |
| Zed | `.rules` |
| OpenCode, Codex, Jules, Amp | `AGENTS.md` (native) |

Copy or symlink:

```bash
ln -s AGENTS.md .clinerules
mkdir -p .github && ln -s ../AGENTS.md .github/copilot-instructions.md
```

Symlinks keep one source of truth. Use a copy on Windows without developer mode.

## Skills registry

Agents that support the skills registry can pull the skills directly:

```bash
npx skills add mateussatoh/tacape -a cursor
```

## Manual, any agent at all

Paste `AGENTS.md` into your agent's system prompt or custom instructions field. It is
self-contained and assumes no tooling.

---

## Verify

After installing on Claude Code:

```bash
# 1. Style layer loads and reports the active level
node ~/.claude/plugins/cache/tacape/tacape/*/hooks/tacape-activate.js | head -1
# expect: TACAPE ACTIVE - level: full

# 2. Guard denies a payload carrying the em dash
printf '{"tool_input":{"file_path":"a.md","content":"x \u2014 y"}}' \
  | node ~/.claude/plugins/cache/tacape/tacape/*/hooks/tacape-emdash-guard.js
# expect: a JSON object with "permissionDecision":"deny"

# 3. Guard stays out of the way otherwise, and does NOT auto-approve
out=$(echo '{"tool_input":{"content":"x - y"}}' \
  | node ~/.claude/plugins/cache/tacape/tacape/*/hooks/tacape-emdash-guard.js)
echo "bytes: ${#out}"
# expect: bytes: 0
```

In the session itself: `/tacape:tacape` should answer with the current level, and asking the agent to
write a file containing an em dash should be blocked with an explanation.

## Statusline (Claude Code, optional)

```
[TACAPE:FULL] ~/dev/tacape (main*) Opus 4.8
```

Add to your settings file, pointing at wherever tacape lives:

```json
"statusLine": {
  "type": "command",
  "command": "bash \"/path/to/tacape/hooks/tacape-statusline.sh\""
}
```

Prefer a stable path such as a git clone over the plugin cache, since the cache path carries the
version number and changes on every upgrade.

Test it without restarting:

```bash
echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"}}' \
  | bash /path/to/tacape/hooks/tacape-statusline.sh
```

tacape never wires this for you and never replaces an existing statusline. It offers once, on a
session where none is configured.

## Turn it off

```
/tacape:tacape off        style layer off, guard stays on
"stop tacape"      same, for one session
```

Escape hatch for a repo that legitimately needs the character, such as quoting a source verbatim:

```bash
TACAPE_ALLOW_EMDASH=1 claude
```

## Uninstall

```bash
claude plugin uninstall tacape
claude plugin marketplace remove tacape
```

For the plain-file installs, delete `AGENTS.md` and any symlink you created.

## Requirements

Node 18 or newer, for the two hooks. The plain-file install needs nothing at all.
