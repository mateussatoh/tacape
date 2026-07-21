<p align="center">
  <strong>tacape</strong>
</p>

<p align="center">
  <em>A tacape is a wooden war club. Blunt, short, ends the conversation.</em>
</p>

<p align="center">
  Your agent stops burying the answer, and starts writing code that survives review.
</p>

<p align="center">
  <a href="https://github.com/mateussatoh/tacape/stargazers"><img src="https://img.shields.io/github/stars/mateussatoh/tacape?style=flat&color=b5651d" alt="Stars"></a>
  <a href="./INSTALL.md"><img src="https://img.shields.io/badge/works_with-5_agent_families-b5651d?style=flat" alt="Agents"></a>
  <a href="./tests/run.sh"><img src="https://img.shields.io/badge/tests-46_passing-4c9a2a?style=flat" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/mateussatoh/tacape?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="#the-problem-is-not-that-agents-talk-too-much">Why</a> ·
  <a href="#install">Install</a> ·
  <a href="#see-it">See it</a> ·
  <a href="#layer-3-the-part-nobody-else-ships">Principles</a> ·
  <a href="#the-one-original-idea">The guard</a> ·
  <a href="#levels">Levels</a> ·
  <a href="#honest-numbers">Honest numbers</a> ·
  <a href="#where-the-principles-come-from">Credits</a>
</p>

<p align="center"><a href="./README_pt.md">Português brasileiro</a></p>

---

## The problem is not that agents talk too much

It is, a little.

But imagine an agent answer as a negotiation. One part knows the answer. Another part wants
to explain every possible edge case. A third part wants to make the response sound helpful
before doing anything helpful.

The result is familiar: you ask for a fix, receive a small essay, and discover the command
you need hiding near the end. You understood it. You still did not start.

Then comes the worse version. The answer is short, the action is first, and the code is
still wrong. It validates input and casts anyway, catches failures into a log nobody watches,
or ships without a test. Fast, organized, unsafe.

There are three failures, and they stack:

1. Volume hides the fact.
2. Order hides the action.
3. Weak engineering hides the defect.

Three failures, three layers:

| | Layer | Fixes |
|---|---|---|
| 1 | **Compression** | Volume. Articles, filler, hedging, preamble, closers. |
| 2 | **Structure** | Order. First line is the action, steps numbered, one next step at the end. |
| 3 | **Principles** | The code. Fifteen language-agnostic rules, applied while writing and reviewing. |

Plus a hard ban on the em dash, enforced by a hook instead of a prompt rule. That sounds like a typography obsession. It is actually the most interesting part of the repo, and there is [a section on why](#the-one-original-idea).

## Install

**Claude Code**

```bash
claude plugin marketplace add mateussatoh/tacape
claude plugin install tacape@tacape
```

Restart the session. That is the whole thing. Everything else on this page is already on.

**Codex**

```bash
codex plugin marketplace add mateussatoh/tacape --ref main
codex plugin add tacape@tacape
```

**Gemini CLI**

```bash
gemini extensions install https://github.com/mateussatoh/tacape
```

**Cursor, Windsurf, Cline, Copilot, Aider, Zed, anything else**

Every one of them reads a plain instruction file:

```bash
curl -fsSL https://raw.githubusercontent.com/mateussatoh/tacape/main/AGENTS.md -o AGENTS.md
```

Then symlink it to whatever your agent expects, so one copy stays the source of truth. Per-agent filenames, the skills-registry route, verification commands and uninstall live in **[INSTALL.md](./INSTALL.md)**.

> [!TIP]
> Requirements: Node 18 or newer for the hooks. The plain-file install needs nothing at all.

> [!WARNING]
> **One style plugin at a time.** Two always-on `SessionStart` hooks injecting competing style rules produce drift, not a blend. Uninstall the other one first, then check your settings file, because a plugin uninstall does not remove hooks that a standalone installer wrote directly into settings. That failure mode is real and it is silent: your old plugin keeps running and you cannot work out why nothing changed.


## See it

<table>
<tr>
<th width="50%">Default agent</th>
<th width="50%">tacape</th>
</tr>
<tr>
<td valign="top">

> Sure! I'd be happy to help you with that. The issue you're experiencing is most likely caused by your authentication middleware not properly validating the token expiry. Let me take a look and suggest a fix.

</td>
<td valign="top">

> Bug in auth middleware. Token expiry check uses `<`, needs `<=`.

</td>
</tr>
<tr>
<td valign="top">

> I've looked into the migration. There are a few things going on here. The schema change touches three tables, and you'll want to be careful about the ordering because of the foreign keys. I've updated the first one already. Let me know if you want me to continue with the rest.

</td>
<td valign="top">

> `[1/3] users.tenant_id added. Next: backfill it.`
>
> 1. Run the backfill on a copy first
> 2. Add the FK on `orders.tenant_id`
> 3. Drop the old column
>
> About 20 minutes. Next: run step 1 and paste the row count.

</td>
</tr>
</table>

Look at the second row again. The default version is not much longer. It is organized so that the only actionable sentence is "let me know if you want me to continue", which is not an action, it is a request for permission to keep going. Layer 2 is about that, not about word count.

Code, commands and error strings are never compressed. Your language is never translated: write Portuguese, get Portuguese back.

## Layer 3: the part nobody else ships

Layers 1 and 2 shape what the agent says. Layer 3 shapes what it writes, which is the part you live with afterwards.

Same task, an agent with the principles loaded and without:

```diff
- export function getUser(raw: unknown) {
-   if (!isValid(raw)) throw new Error('bad')      // validated, then forgotten
-   const u = raw as User                          // the cast is the whole safety story
-   try { return db.users.find(u.id) }
-   catch (e) { log.info('lookup failed', e); return null }   // gone quiet
- }
+ export function getUser(raw: unknown): User {
+   const input = UserInput.parse(raw)     // parse once, at the edge, into a type
+   try {                                  // that cannot hold a bad value   (rule 7)
+     return db.users.find(input.id)
+   } catch (err) {
+     alert.capture(err, { op: 'getUser' })  // a retried path must page     (rule 6)
+     throw err
+   }
+ }
```

The left version passes review, passes tests, and goes silent in production. That is the whole argument.

<details>
<summary><strong>All fifteen rules</strong></summary>

<br>

**1. Boring, searchable, safe to edit.** Obvious beats clever. Name for the domain, not the mechanism: `activateSubscriptionAfterPayment`, never `process`, `handle`, `manager`, `helper`. A good name is the one a stranger greps for. Comments explain WHY, since the code already says what.

**2. Abstract late.** Duplication is cheaper than the wrong abstraction. Two similar things are not one thing. You get about three innovation tokens: spend them where the novelty is the product, take the well understood option everywhere else. The exception to "no dependency for something small": crypto, auth, timezone math, and hostile-format parsing. Hand-rolling those is a CVE with your name on it.

**3. Modules are deep, not wide.** Judge an interface by what a caller must understand, and the implementation by how much work it does for them. A pass-through layer whose methods map one to one onto the layer below is negative value: delete it. And define errors out of existence where you honestly can. An idempotent operation needs no "already applied" branch. Every error eliminated is a branch nobody can get wrong.

**4. Write code that is easy to delete.** You will be wrong about the future. Code you can delete in an afternoon costs nothing when you are wrong; code everything extends costs a quarter. Layer by expected lifetime, so the vendor integration and the experiment can be cut out whole. Repeat yourself to avoid a dependency, never to manage one.

**5. Boundaries are one-way and enforced.** Dependencies point one direction. Cross through the public interface, never into internals. Verify the enforcement with a negative probe: write the forbidden import, confirm it actually fails, then delete it. A rule that silently never fires is indistinguishable from a rule that passes.

**6. Failures stay visible.** A caught error on a retried path must reach the alerting system, not just the log. Swallowing an exception into a log line nobody watches is how a system stays broken for days while every dashboard reads green. Never pattern-match a wrapped error's surface field: walk the cause chain, or the next version bump turns a handled case into a crash.

**7. Make invalid states unrepresentable.** Push correctness into types and schemas at the boundary. A comment saying "must be positive" is a wish. Parse untrusted input once, at the edge. Never return an internal record to a caller you do not control without whitelisting the fields.

**8. Data and time.** Store instants in UTC, render in the viewer's timezone. Never format a date without an explicit timezone, or the output changes depending on which machine ran it. A store holds what its name says.

**9. Tests that would have caught it.** Mocking the layer under test hides the bug you are shipping. A suite that is green because everything is faked proves only that the fakes agree. Deterministic, isolated, fast. Test the race, the duplicate, the timeout, the empty list. A bug fix ships with its reproducing test.

**10. Copy and locale.** User-facing text in the product's language, identifiers in English. Never render an internal enum or code raw to a user.

**11. Interface states are not optional.** Every async view handles all four: loading, empty, error, loaded. A blank screen during load is a bug, not a default.

**12. Secrets and destructive actions.** Never run or suggest a command that prints secret values. Confirm before anything irreversible or outward-facing. Approval for one such action does not carry to the next.

**13. Find the file, do not grep the repo.** Map, then scope, then read. Filename search before content search. Scoped before repo-wide. Read the nearby tests before editing.

**14. Ask versus decide.** Ask only when the answer changes the outcome and the call is the owner's. Do not ask about cosmetics or conventional defaults. Make the call, state it in one line, keep moving.

**15. Documentation is part of the change.** Each rule lives in exactly one place. Decisions are append-only: supersede, never rewrite. A stale doc is worse than no doc, because it is believed.

</details>

Full text with the reasoning behind each rule: **[`skills/tacape-code/SKILL.md`](./skills/tacape-code/SKILL.md)**.

> [!IMPORTANT]
> **Precedence, and it matters.** The target repo's own `CLAUDE.md`, `AGENTS.md` and visible conventions always win over these principles. tacape never imposes a style on a codebase that consistently does otherwise. A style guide that overrides the house it is a guest in is not a style guide, it is a bulldozer.

## The one original idea

Layers 1 and 2 are merged from two existing plugins, credited [below](#inspiration). This part is not.

Here is the observation. Every rule you give an agent through a prompt is advisory. It sits in context competing with everything else, and over a long session it loses. You have watched this happen: the agent is perfectly terse for twenty turns and then slowly, without announcing it, goes back to writing essays. Nobody turned it off. It decayed.

There is a second failure no prompt rule can fix at all. If the agent pastes a template, or generates a file from a string it fetched, or copies a block from documentation, the rule was never consulted. The character arrives from outside the model's own composition.

So: take one rule, and move it out of the prompt and into the tool layer, where it is not advice and cannot decay.

tacape does this for the em dash. A `PreToolUse` hook on `Write`, `Edit` and `NotebookEdit` walks every string in the payload, and if a dash-family character is in there, the write is denied with an explanation before anything touches disk. Not a reminder. A wall.

<details>
<summary><strong>Three non-obvious things about building this</strong></summary>

<br>

**The guard file cannot contain the character it bans.** It stores it as a `\u2014` escape, or it fails its own check the moment the repo-wide test runs.

**The allow path must emit nothing.** The obvious implementation returns `permissionDecision: "allow"` when the payload is clean. That would auto-approve every single write in your session, which is a vastly worse bug than the one the hook fixes. Emitting nothing lets the call fall through to normal permission handling.

**One thing we got wrong and reverted.** Adding `Bash` to the matcher looked like closing a bypass, since `echo "x" > f.md` writes whatever it wants. It closed the remedy instead: a command string cannot distinguish writing the character from searching for it or deleting it, so `grep -rn "<char>" .` and `sed -i "s/<char>/,/g" f.md` both got denied. The two commands you most need in a repo that bans the character. A guard that blocks the fix is worse than no guard. Bash writes are caught one layer down now, by the pre-commit hook and CI, which look at the result instead of guessing at intent.

</details>

> [!NOTE]
> **Scope, stated honestly.** This is not a filesystem-level guarantee. A write by a program the agent launches, a formatter or a codegen step or a shell redirect, is outside what a `PreToolUse` hook can see. The repo-wide invariant belongs in CI, which is where tacape checks its own.

Escape hatch, for a repo that legitimately needs the character:

```bash
TACAPE_ALLOW_EMDASH=1 claude
```

The guard is independent of the style level. `/tacape:tacape off` does not disable it.

## Levels

| Level | Same sentence, shrunk |
|---|---|
| *no plugin* | You should wrap the object in `useMemo`, since a new reference is created on every render. |
| `lite` | Wrap the object in `useMemo`. A new reference is created every render. |
| `full` *(default)* | New ref each render. Wrap object in `useMemo`. |
| `ultra` | New ref per render. `useMemo` it. |
| `off` | Style layer off. Guard stays on. |

```
/tacape:tacape          show the current level
/tacape:tacape ultra    switch
/tacape:tacape off      disable the style layer
```

Persists in `~/.claude/.tacape-mode`. `TACAPE_LEVEL=ultra` overrides for one session without changing your default.

**It stands down on its own** for security warnings, irreversible actions, and any sequence where dropped words would make the order ambiguous. Safety beats brevity, always. It also stands down when you ask it to explain something: then it runs as long as the topic needs, still with no preamble and no closer. A brevity plugin that makes an agent terse about `rm -rf` is a liability, not a feature.

## Statusline

Optional, Claude Code only.

```
[TACAPE:FULL] ~/dev/tacape (main*) Opus 4.8
```

Level, directory, branch with a dirty marker, model. Not wired automatically, because overwriting a statusline you already built would be rude. tacape offers once, on a session where none is configured. Setup in [INSTALL.md](./INSTALL.md).

Pure bash, no node and no jq, since it runs on every refresh. It refuses to read the level from a symlink, caps the read, and strips control bytes, because a statusline writes straight into your terminal and a planted file would otherwise inject ANSI escape sequences on every refresh.

## Honest numbers

**tacape does not report tokens saved, and that is deliberate.**

Every "X% saved" number in this category is an estimate against a counterfactual nobody observed. You cannot know what the agent *would* have said without the plugin, because it did not say it. You can estimate, and the estimates are not worthless, but they are estimates wearing the costume of a measurement.

What can be said honestly, without a number:

- **Output tokens go down.** Obviously. That is what layer 1 does.
- **Input tokens go up slightly.** The ruleset is injected at `SessionStart`. It is not free.
- **On already-terse workloads the net can go negative.** If your prompts are one-liners and the answers are three words, you are paying the ruleset cost for compression you did not need.
- **The real win is not money.** It is that you can find the answer, and that the code coming back has fewer of the specific defects layer 3 targets. Cost is a side effect.

An earlier version of this README carried an attribution table crediting eleven essays for ideas only partly in the file. An audit caught it. The lesson generalizes: this project would rather ship no number than a flattering one. If a measured A/B eval lands later, the number goes here with the harness next to it.

## Where the principles come from

Two lineages, and it is worth being precise about which is which.

**The immediate source is production incidents.** Most of these rules were written the week after something broke. "A caught error on a retried path must reach the alerting system" is here because a payment webhook logged its failures and returned success, so the gateway stopped retrying and nothing paged, and the path stayed dead for two days while every dashboard read green. "Verify a boundary rule with a negative probe" is here because a lint config that looked correct was silently enforcing nothing. That is why the rules are phrased as consequences and not as preferences.

**The ideas underneath are not original.** Each of these named the thing long before it appeared here:

| Idea | Source | Rule |
|---|---|:---:|
| Duplication is far cheaper than the wrong abstraction | Sandi Metz, [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) (2016) | 2 |
| Complexity is the enemy, resist the complexity demon | Carson Gross, [The Grug Brained Developer](https://grugbrain.dev/) (2022) | 1 |
| Innovation tokens: spend novelty where it is the product | Dan McKinley, [Choose Boring Technology](https://mcfunley.com/choose-boring-technology) (2015) | 2 |
| Deep modules, push complexity down, define errors out of existence | John Ousterhout, A Philosophy of Software Design (2018) | 3 |
| Optimize for deletion, layer by expected lifetime | tef, [Write code that is easy to delete](https://programmingisterrible.com/post/139222674273/write-code-that-is-easy-to-delete-not-easy-to) (2016) | 4 |
| Dependencies point one direction, inward | Robert C. Martin, the Dependency Rule | 5 |
| Pure decision logic first, effects at the shell | Gary Bernhardt, Functional Core / Imperative Shell (2012) | 6, 7 |
| Parse untrusted input once, at the edge, into a type that cannot be wrong | Alexis King, [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) (2019) | 7 |
| Make illegal states unrepresentable | Yaron Minsky, Jane Street, from the OCaml tradition | 7 |
| Deterministic, isolated, fast, behavior over implementation | Kent Beck, Test Desiderata (2019) | 9 |
| The rule of three, and YAGNI | Martin Fowler, Refactoring, crediting Don Roberts | 2 |

Every row names the rule carrying it. If a row ever stops tracing to a rule, the row gets deleted rather than keeping the borrowed authority.

What tacape adds is not a new idea. It is that an agent applies these by default, on every diff, without you remembering to ask. Reading the essays changes what you believe. A skill file changes what gets written at 2am.

## Inspiration

Two plugins solved half the problem each, and tacape owes both.

**[caveman](https://github.com/JuliusBrussee/caveman)** by Julius Brussee is layer 1. It proved an agent can drop most of its words without losing any technical substance, and, importantly, that the ruleset has to be re-injected every session or the model drifts back to verbose. That single observation is the seed of the entire tool-layer argument above.

**[i-have-adhd](https://github.com/ayghri/i-have-adhd)** by ayghri is layer 2. Its argument is that brevity alone is not enough: working memory is small, starting is the hardest step, and a buried answer does not register. Lead with the action, number the steps, end with one thing to do.

They are orthogonal, compression is about how words look and structure is about where things go, but running both as separate always-on plugins means two style prompts competing for the same job. tacape merges them into one ruleset and adds what neither has: the enforced ban and the engineering principles.

## Skills

| Skill | Fires on |
|---|---|
| `tacape` | Always, via `SessionStart`. Compression and structure. |
| `tacape-code` | Writing, refactoring or reviewing code in any language. |
| `tacape-commit` | "write a commit". Conventional Commits, 50 char subject, body only when the diff cannot answer why. |
| `tacape-review` | "review this diff". One line per finding, severity ranked, capped at 8 and never silently truncated. |

## Development

```bash
bash tests/run.sh                  # 46 assertions, no framework, no dependencies
bash hooks/install-git-hooks.sh    # pre-commit guard against the banned characters
```

CI runs the same file on every push. The suite covers the hooks against adversarial input, the manifests, and assertions that fail when `AGENTS.md` and `skills/tacape/SKILL.md` drift apart, since those are two hand-maintained copies of one ruleset.

This exists because the principles in this repo demand tests and tool-enforced rules, and for the first three commits tacape had neither. An audit pointed that out, correctly, as the finding that undercut everything else it claims. A plugin arguing that prompt rules decay and belong in the tool layer has to hold its own rules in the tool layer too, or it is a blog post with a manifest.

## Compare instruction styles

Run OpenAI benchmark against neutral, Caveman, i-have-adhd and tacape instructions:

```bash
python3 benchmarks/run-openai.py --dry-run
OPENAI_API_KEY=... python3 benchmarks/run-openai.py
```

Same prompts, same model, fixed request shape, repeated trials, median output tokens. Benchmark
reports data for this prompt set. It does not claim universal superiority.

## What it deliberately does not do

No runtime token accounting. No subagents. No statusline wired without asking. It shapes output
and encodes principles, nothing more.
## License

MIT.
