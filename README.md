<p align="center"><strong>tacape</strong></p>

<p align="center">
  Your agent stops burying the answer, and starts writing code that survives review.
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#before--after">Before / after</a> ·
  <a href="#the-three-layers">Layers</a> ·
  <a href="#the-engineering-principles">Principles</a> ·
  <a href="#the-em-dash-guard">Em dash guard</a> ·
  <a href="#levels">Levels</a> ·
  <a href="#inspiration">Inspiration</a>
</p>

---

A *tacape* is a wooden war club. Blunt, short, gets the job done.

Most output-style plugins do one thing: they make the agent use fewer words. That helps, but a
short answer with the action buried at the bottom is still a wall, and a terse agent still writes
the same mediocre code. tacape does three things instead.

1. **Compression.** Drops articles, filler, hedging, preamble and closers.
2. **Structure.** The first line is what to do. Steps are numbered. Every answer ends with one
   concrete next action.
3. **Engineering principles.** Language-agnostic rules applied while writing and reviewing code.
   This is the part the other plugins do not have.

Plus a hard ban on U+2014, the em dash, enforced by a hook rather than by a prompt rule that decays.

Works with Claude Code, Codex, Gemini CLI, Cursor, Windsurf, Cline, Copilot, Aider, Zed, and any
other agent that reads an instruction file.

## Install

**Claude Code**

```bash
claude plugin marketplace add mateussatoh/tacape
claude plugin install tacape@tacape
```

Restart the session. Hooks load at `SessionStart`.

**Codex**

```bash
codex plugin marketplace add mateussatoh/tacape --ref main
```

**Gemini CLI**

```bash
gemini extensions install https://github.com/mateussatoh/tacape
```

**Everything else** reads a plain instruction file. Drop `AGENTS.md` in your project root:

```bash
curl -fsSL https://raw.githubusercontent.com/mateussatoh/tacape/main/AGENTS.md -o AGENTS.md
```

Cursor wants `.cursorrules`, Cline wants `.clinerules`, Copilot wants
`.github/copilot-instructions.md`. Symlink `AGENTS.md` to whichever your agent expects, so there
stays exactly one copy of the rules.

Per-agent filenames, the skills-registry route, verification commands and uninstall live in
**[INSTALL.md](./INSTALL.md)**. Requirements: Node 18 or newer for the hooks. The plain-file
install needs nothing.

> **One style plugin at a time.** Two always-on `SessionStart` hooks injecting competing style
> rules produce drift, not a blend. Uninstall the other one first, and check your settings file for
> a leftover standalone install, because a plugin uninstall does not remove hooks that were written
> directly into settings.

## Before / after

**Compression**, layer one:

> Sure! I'd be happy to help you with that. The issue you're experiencing is most likely caused by
> your authentication middleware not properly validating the token expiry. Let me take a look.

becomes

> Bug in auth middleware. Token expiry check uses `<`, needs `<=`.

**Structure**, layer two. Same information, reordered so the first line is actionable:

> I've looked into the migration. There are a few things going on here. The schema change touches
> three tables, and you'll want to be careful about the ordering because of the foreign keys. I've
> updated the first one already. Let me know if you want me to continue with the rest.

becomes

> ```
> [1/3] users.tenant_id added. Next: backfill it.
>
> 1. Run the backfill script on a copy first
> 2. Add the FK constraint on orders.tenant_id
> 3. Drop the old column
>
> About 20 minutes. Next: run step 1 and paste the row count.
> ```

Nothing technical is lost in either case. Code, commands and error strings are never compressed,
and the user's language is never translated. Write Portuguese, get Portuguese back.

## The three layers

| Layer | What it governs | Where it lives |
|---|---|---|
| Compression | How the words look | `skills/tacape/SKILL.md`, always on |
| Structure | Where the information goes | same file, always on |
| Principles | How the code gets written | `skills/tacape-code/SKILL.md`, loads when you touch code |

Keeping the principles in a separate skill is deliberate. They are long, and they are irrelevant
when you are asking about a shell command. Loading them into every turn would burn the tokens the
compression layer just saved.

## The engineering principles

This is the part that makes tacape more than a style plugin. Thirteen sections, no framework, no
language, no stack assumptions. The short version:

**1. Boring, searchable, safe to edit.** Obvious beats clever. Name for the domain, not the
mechanism: `activateSubscriptionAfterPayment`, never `process`, `handle`, `manager`, `helper`.
A good name is the one a stranger greps for. Comments explain WHY, since the code already says what.

**2. Abstract late.** Duplication is cheaper than the wrong abstraction. Two similar things are not
one thing. No factory, registry, manager or wrapper without a repeated need you can point at.
Patterns are a response to pressure, not a starting position.

**3. Boundaries are one-way and enforced.** Dependencies point one direction. Cross a boundary
through its public interface, never by reaching into internals. And verify the enforcement with a
negative probe: write the forbidden import, confirm it actually fails, then delete it. A rule that
silently never fires is indistinguishable from a rule that passes.

**4. Failures stay visible.** A caught error on a retried path must reach the alerting system, not
just the log. Swallowing an exception into a log line nobody watches is how a system stays broken
in production for days while every dashboard reads green. Never pattern-match a wrapped error's
surface field: walk the cause chain, or the next version bump turns a handled case into a crash.

**5. Make invalid states unrepresentable.** Push correctness into types and schemas at the
boundary. A comment saying "must be positive" is a wish. Parse untrusted input once, at the edge.
Never return an internal record to a caller you do not control without whitelisting the fields.

**6. Data and time.** Store instants in UTC, render in the viewer's timezone. Never format a date
without an explicit timezone, or the output changes depending on which machine ran it. A store
holds what its name says.

**7. Tests that would have caught it.** Mocking the layer under test hides the bug you are
shipping. A suite that is green because everything is faked proves only that the fakes agree.
Test the race, the duplicate, the timeout, the empty list. A bug fix ships with its reproducing test.

**8. Copy and locale.** User-facing text in the product's language, identifiers in English. Never
render an internal enum or code raw to a user. Zero em dashes.

**9. Interface states are not optional.** Every async view handles all four: loading, empty, error,
loaded. A blank screen during load is a bug, not a default.

**10. Secrets and destructive actions.** Never run or suggest a command that prints secret values.
Confirm before anything irreversible or outward-facing. Approval for one such action does not carry
to the next.

**11. Find the file, do not grep the repo.** Map, then scope, then read. Filename search before
content search. Scoped search before repo-wide. Read the nearby tests before editing.

**12. Ask versus decide.** Ask only when the answer changes the outcome and the call is the
owner's. Do not ask about cosmetics or conventional defaults. Make the call, state it in one line,
keep moving.

**13. Documentation is part of the change.** Each rule lives in exactly one place. Decisions are
append-only: supersede, never rewrite. A stale doc is worse than no doc, because it is believed.

Full text with the reasoning behind each rule: **[`skills/tacape-code/SKILL.md`](./skills/tacape-code/SKILL.md)**.

Precedence is explicit and it matters: **the target repo's own `CLAUDE.md`, `AGENTS.md` and
visible conventions always win over these principles.** tacape never imposes a style on a codebase
that consistently does otherwise.

## The em dash guard

A `PreToolUse` hook on `Write`, `Edit` and `NotebookEdit`. If the payload contains U+2014, the
write is denied with an explanation before anything reaches disk.

Why a hook and not a rule: a prompt rule is advisory and decays over a long session. A hook does
not have opinions. It also catches the character arriving from a paste or a generated template,
which no prompt rule could.

The faux em dash is banned too. `X - Y - Z`, two hyphens fencing an aside, is the same tell.

Escape hatch, for a repo that legitimately needs the character:

```bash
TACAPE_ALLOW_EMDASH=1 claude
```

The guard is independent of the style level. `/tacape off` does not disable it. On agents without a
pre-tool hook the ban is a rule in `AGENTS.md`, which is advisory rather than enforced.

## Levels

| Level | Same sentence, shrunk |
|---|---|
| *no plugin* | You should wrap the object in `useMemo`, since a new reference is created on every render. |
| `lite` | Wrap the object in `useMemo`. A new reference is created every render. |
| `full` *(default)* | New ref each render. Wrap object in `useMemo`. |
| `ultra` | New ref per render. `useMemo` it. |
| `off` | Style layer off. Guard stays on. |

```
/tacape          show the current level
/tacape ultra    switch
/tacape off      disable the style layer
```

The level persists in `~/.claude/.tacape-mode`. Override for one session with `TACAPE_LEVEL=ultra`.

**It stands down on its own** for security warnings, irreversible actions, and any sequence where
dropped words would make the order ambiguous. Safety beats brevity, always. It also stands down
when you ask it to explain something: then it runs as long as the topic needs, still with no
preamble and no closer.

## Statusline

Optional, Claude Code only. Shows the active level, the directory, the git branch with a dirty
marker, and the model.

```
[TACAPE:FULL] ~/dev/tacape (main*) Opus 4.8
```

It is not wired automatically, because overwriting a statusline you already built would be rude.
On first session with no statusline configured, tacape offers to set it up. Or add it yourself:

```json
"statusLine": {
  "type": "command",
  "command": "bash \"/path/to/tacape/hooks/tacape-statusline.sh\""
}
```

Pure bash, no node and no jq, since it runs on every refresh. It refuses to read the level from a
symlink, caps the read, and strips everything outside `[a-z]`, because a statusline renders
straight into your terminal and a planted file could otherwise inject ANSI escape sequences.

## Skills

| Skill | Fires on |
|---|---|
| `tacape` | Always, via `SessionStart`. Compression and structure. |
| `tacape-code` | Writing, refactoring or reviewing code in any language. |
| `tacape-commit` | "write a commit", `/tacape-commit`. Conventional Commits, 50 char subject, body only when the diff cannot answer why. |
| `tacape-review` | "review this diff", `/tacape-review`. One line per finding, severity ranked, capped at 8 and never silently truncated. |

## Where the principles come from

Two different lineages, and it is worth being precise about which is which.

**The immediate source is production incidents.** Most of these rules were extracted from real
codebases, and most of them were written the week after something broke. "A caught error on a
retried path must reach the alerting system" is in here because a payment webhook logged its
failures and returned success, so the gateway stopped retrying and nothing paged, and the path
stayed dead for two days while every dashboard read green. "Verify a boundary rule with a negative
probe" is in here because a lint config that looked correct was silently enforcing nothing. That is
why the rules are phrased as consequences rather than as style preferences.

**The ideas underneath are not original, and the people who articulated them deserve the credit.**
Each of these named the thing long before it showed up as a rule here:

| Idea | Source |
|---|---|
| Duplication is far cheaper than the wrong abstraction | Sandi Metz, [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) (2016) |
| Complexity is the enemy, boring wins, resist the demon spirit of complexity | Carson Gross, [The Grug Brained Developer](https://grugbrain.dev/) (2022) |
| Optimize for deletion, not extension. Layer so the hard parts are isolated | tef, [Write code that is easy to delete, not easy to extend](https://programmingisterrible.com/post/139222674273/write-code-that-is-easy-to-delete-not-easy-to) (2016) |
| Parse untrusted input once, at the edge, into a type that cannot be wrong | Alexis King, [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) (2019) |
| Make illegal states unrepresentable | Yaron Minsky, Jane Street, from the OCaml tradition |
| Pure decision logic first, effects at the shell | Gary Bernhardt, Functional Core / Imperative Shell, Destroy All Software (2012) |
| The rule of three, and YAGNI | Martin Fowler, Refactoring, crediting Don Roberts |
| Dependencies point one direction, inward | Robert C. Martin, the Dependency Rule, Clean Architecture |
| Complexity is incremental, and interfaces should be deeper than they are wide | John Ousterhout, A Philosophy of Software Design (2018) |
| Prefer the boring, well-understood option | Dan McKinley, [Choose Boring Technology](https://mcfunley.com/choose-boring-technology) (2015) |
| Tests should be about behavior, fast, and give confidence rather than coverage | Kent Beck, Test Desiderata (2019) |

What tacape adds is not a new idea. It is that an agent applies these by default, on every diff,
without you having to remember to ask. Reading the essays changes what you believe. A skill file
changes what actually gets written at 2am.

## Inspiration

On the output side, tacape stands on two plugins that each solved one half of the problem.

**[caveman](https://github.com/JuliusBrussee/caveman)** by Julius Brussee gave it the compression
layer. It proved an agent can drop most of its words without losing any technical substance, and
that the ruleset has to be re-injected every session or the model drifts back to verbose.

**[i-have-adhd](https://github.com/ayghri/i-have-adhd)** by ayghri gave it the structure layer.
Its argument is that brevity alone is not enough: working memory is small, starting is the hardest
step, and a buried answer does not register. Lead with the action, number the steps, end with one
next thing to do.

The two are orthogonal, compression is about how words look and structure is about where things go,
but running both as separate always-on plugins means two style prompts competing. tacape merges
them into one ruleset and adds what neither covers: the enforced em dash ban and the engineering
principles.

## What it deliberately does not do

No token accounting or savings dashboard. No statusline. No subagents. It shapes output and
encodes principles, nothing more.

## License

MIT.
