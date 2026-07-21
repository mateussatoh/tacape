# tacape

Read [`AGENTS.md`](./AGENTS.md) and follow it for every reply in this session.

It is the canonical ruleset: compression, action-first structure, the U+2014 em dash ban, and the
engineering principles that apply whenever you touch code.

Claude Code users who installed the plugin already receive these rules through the `SessionStart`
hook, plus the write-time em dash guard. This file matters when the repo is opened directly, or
when tacape is used as a plain instruction file instead of an installed plugin.

## Working on tacape itself

- `skills/tacape/SKILL.md` is the source of truth for the style layer. The activation hook reads it
  at runtime and filters the intensity table to the active level, so edits propagate with no
  duplicated copy to go stale. Keep the `| **level** |` table row format intact.
- `AGENTS.md` is the portable copy for agents with no plugin system. When a rule changes in
  `SKILL.md`, change it here in the same commit.
- The em dash guard must never contain a literal U+2014. It stores the character as a JavaScript
  `\u2014` escape sequence, so the file survives its own check.
- The guard emits nothing on the allow path. Returning an explicit allow decision would
  auto-approve every write in the session.
- Before committing, run the checks in `INSTALL.md` under "Verify".
