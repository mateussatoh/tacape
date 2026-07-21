---
name: tacape-commit
description: >
  Commit message generator. Conventional Commits, subject 50 chars or less, body only when the
  "why" is not obvious from the diff. Hard ban on U+2014 em dash.
  Use when the user says "write a commit", "commit message", "generate commit", or invokes
  /tacape-commit. Auto-triggers when staging changes.
---

Write the commit. Do not narrate the diff back first.

## Format

```
<type>(<scope>): <subject>

<body, only if needed>

<footer, only if needed>
```

- `type`: feat · fix · refactor · perf · test · docs · build · ci · chore · revert
- `scope`: the package or module touched (`api`, `payments`, `client`, `core`). Omit if repo-wide.
- `subject`: imperative mood, lowercase, no trailing period, 50 chars or less.
  "add pix renewal cadence", not "Added PIX renewal cadence."

## Body rules

Write a body ONLY when the diff cannot answer one of these:

1. Why this change, when the code shows only what changed.
2. What breaks, for a breaking change (`BREAKING CHANGE:` footer).
3. What was ruled out, when an obvious simpler approach was rejected for a real reason.

No body for: renames, formatting, dependency bumps, obvious one-line fixes.
Body wraps at 72 chars. Bullets with `-`. No recap of the file list, git already has it.

## Hard rules

- **Zero U+2014 (em dash)** anywhere in subject, body, or footer.
- No `X - Y - Z` dash-parenthetical. Use a colon or a period.
- Never mention the AI, the agent, or the tooling in the message.
- Never write "various fixes", "misc", "updates", "wip" as the subject.
- One logical change per commit. If the diff does two things, say so and offer to split.

## Examples

Good, no body needed:
```
fix(auth): match wrapped errors by cause chain
```

Good, body earns its place:
```
fix(webhooks): alert on errors the sender retries

The catch logged and returned success, so the sender stopped retrying
and nothing paged. The path failed silently in production for two days
while every dashboard read green.

- report to the alerting system on every retried catch
- structured log stays, for the flow trace
```

Bad:
```
Fixed a bunch of issues in the checkout module - webhooks, retries and logging - plus some cleanup
```
Subject too long, past tense, capitalized, faux em dash, several unrelated changes in one commit.

## Flow

1. Read the staged diff (`git diff --staged`). If nothing staged, read `git diff` and say so.
2. Write the message.
3. Commit only when the user asked to commit. Otherwise print the message and stop.
