---
description: Set the tacape output level (lite, full, ultra, off)
argument-hint: "[lite|full|ultra|off]"
---

Set the tacape level to `$1`.

Steps:

1. If `$1` is empty, report the current level by reading `~/.claude/.tacape-mode`
   (default `full` when the file is missing) and stop.
2. If `$1` is not one of `lite`, `full`, `ultra`, `off`, say so and stop without writing anything.
3. Write the bare level string to `~/.claude/.tacape-mode` (no newline, no quotes).
4. Adopt the new level immediately for this response and every response after it.
   Do not wait for a session restart.
5. Confirm in one line: `tacape: <level>`.

Level behavior is defined in the `tacape` skill. `off` disables the style layer only.
The em dash guard is a PreToolUse hook and stays active regardless of level.
