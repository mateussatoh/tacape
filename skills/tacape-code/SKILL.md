---
name: tacape-code
description: >
  Language-agnostic engineering principles: boring and searchable code, one-way module boundaries,
  errors that stay visible, data at the edges, honest tests, and a discovery order that finds the
  right file fast. No stack, no framework, no project assumptions.
  Use when writing, refactoring, or reviewing code in any language, when starting a new repo, or
  when the user asks for "the principles", "house style", "how we write code".
  Defer to the repo's own CLAUDE.md or AGENTS.md when one exists: that file always wins.
---

Principles, not rules for a stack. They hold in any language and any framework.

Precedence: the repo's own `CLAUDE.md` / `AGENTS.md` > the conventions already visible in the
surrounding code > this skill. Never impose these over a codebase that consistently does otherwise.

## 1. Boring, searchable, safe to edit

- **Boring wins.** Obvious, explicit and local beats clever. If it looks smart, simplify it.
  Code is read far more often than written, and it is read under pressure.
- **Name for the domain, not the mechanism.** `activateSubscriptionAfterPayment`, not `process`,
  `handle`, `execute`, `doWork`, `manager`, `helper`. A good name is the one a stranger greps for.
- **One unit, one responsibility.** No `utils` / `helpers` / `misc` grab-bags. A module that
  collects unrelated functions has no reason to change together, so it changes constantly.
- **Boring control flow.** Early returns, guard clauses, named booleans, flat `if`/`else`.
  No nested ternaries, no five-level indentation, no clever short-circuit chains.
- **Smallest correct diff.** No drive-by refactors, no formatting churn, no renaming on the way
  past. A reviewable diff gets reviewed. A large one gets approved unread.
- **Comments explain WHY.** The code already says what. Comment the constraint, the tradeoff, the
  bug this guards against, the thing that looks wrong but is not.

## 2. Abstract late

- **Duplication is cheaper than the wrong abstraction.** Two similar things are not one thing.
  Wait for the third occurrence, and wait for it to actually be the same shape.
- **No architecture cosplay.** No factory, registry, manager, adapter, wrapper, plugin system, or
  framework without a concrete repeated need you can point at. Patterns are a response to pressure,
  not a starting position.
- **Do not extract a shared library until a second real consumer duplicates the code.**
  Premature extraction turns a local edit into a cross-repo negotiation.
- **New dependencies are guilty until proven.** For anything small, check the standard library and
  the deps you already have. Every dependency is a supply chain, a version bump, and a license.

## 3. Boundaries are one-way and enforced

- **Dependencies point one direction.** Low-level and general at the bottom, specific and
  deployable at the top. Policy does not import mechanism's caller. Cycles are a design smell,
  not a build problem to work around.
- **Cross a boundary through its public interface**, never by reaching into another module's
  internals. Internals are internal so they can change.
- **The owner of a resource is the layer that can see all of it.** A generic mechanism should not
  own domain state it cannot fully observe. Let the owner declare it and pass it in.
- **Enforce boundaries with a tool, and verify with a negative probe.** Write the forbidden import,
  confirm the check actually fails, then delete it. A rule that silently never fires is
  indistinguishable from a rule that passes. Config that looks right is not evidence.

## 4. Failures stay visible

- **Structured logging, never bare stdout printing.** Distinguish the levels and mean them:
  `error` is an operational alert someone is paged for, `warn` is an expected anomaly that resolves
  itself, `info` is flow.
- **A caught error on a retried path must reach the alerting system**, not just the log.
  Swallowing an exception into a log line that nobody watches is how a system stays broken in
  production for days while every dashboard reads green.
- **Never pattern-match on a wrapped error's surface.** Libraries wrap driver and transport errors
  and move the original to a cause chain. Match by walking the chain behind a named helper.
  A direct field check silently stops matching on a version bump and converts a handled case into
  a crash.
- **Fail closed on ambiguity** for anything touching money, permissions, or deletion.
  When the code cannot tell, it refuses. It does not guess.

## 5. Make invalid states unrepresentable

- Push correctness into types, schemas and validators at the boundary. A comment saying "must be
  positive" is a wish. A type that cannot hold a negative is a guarantee.
- **Validate at the edge, trust inside.** Parse untrusted input once, at the entry point, into a
  known-good shape. Do not re-check the same thing in nine places.
- **Never return an internal record straight to a caller you do not control.** Whitelist the fields
  you mean to expose. Spreading an internal object is how a password hash, an internal flag, or a
  soft-deleted row ships to a client.
- **Separate decision from effect.** Pure logic first, then the writes, calls and logs. The pure
  part is the part you can test without a world.

## 6. Data and time

- **Store instants in UTC, render in the viewer's timezone.** Every timestamp is an absolute
  instant. Never persist local wall-clock time, never do arithmetic on a formatted string.
- **Never format a date without an explicit timezone.** Defaulting to the machine's zone means the
  output changes depending on which server ran it.
- **A store holds what its name says.** Do not smuggle UI state, flow progress or preferences into
  a domain record because it was the convenient table. It is convenient once and wrong forever.
- **Identifiers are opaque and stable.** Never key on a mutable human-readable string.

## 7. Tests that would have caught it

- **A feature ships with tests.** Integration across the real critical path, unit on new pure
  logic. No test, not done.
- **Read the existing tests before editing the implementation.** They are the contract, and they
  document intent better than the code does.
- **Mocking the layer under test hides the bug you are shipping.** If a path writes to a store or
  speaks a protocol, pin its real shape in at least one test that does not mock the boundary.
  A suite that is green because everything is faked proves only that the fakes agree.
- **Test the failure, not just the happy path.** The race, the duplicate, the timeout, the retry,
  the empty list, the permission denial.
- **A bug fix ships with the test that reproduces it.** Otherwise it comes back.

## 8. Localization and copy

- **User-facing text in the product's language, identifiers in English.** No mixed-language
  identifiers, keys, columns, or route segments. Code is read by people who did not ship it.
- **Never render an internal enum, code or id raw to a user.** Map stored values through an
  explicit label layer. A new enum value ships its label in the same change.
- **Zero U+2014 (em dash)** in code, comments, docs, commit messages, UI copy and emails.
  Use a comma, a colon, a period, or a real hyphen.
- **No `X - Y - Z` dash-parenthetical in user-facing prose.** A faux em dash built from hyphens
  fencing an aside is the same tell. Rewrite with a colon, a period, or a different sentence.

## 9. Interface states are not optional

- **Every asynchronous view handles all four states**: loading, empty, error, loaded.
  A blank screen during load is a bug, not a default.
- **Extend a component through its parameters, never by forking a variant.** Two nearly identical
  components drift, and the fix lands in one of them.
- **Keep presentation, data access and business rules in different places.** A view that queries is
  a view you cannot reuse or test.

## 10. Secrets and destructive actions

- Secrets live in a secret store, never in the repo and never in a local file the agent reads.
- **Never run or suggest a command that prints secret values.** If something fails on a missing
  secret, report only its NAME and let a human set it.
- **Confirm before anything irreversible or outward-facing**: deletion, migration, force push,
  deploy, or sending to a real recipient. Approval for one such action does not carry to the next.

## 11. Find the file, do not grep the repo

Map, then scope, then read. Blind repo-wide content search is the last resort, not the first move.

1. Map the task to likely modules using the repo's own index, package map, or directory layout.
2. **Filename search before content search.** Names are cheap to scan and usually right.
3. **Scoped content search before repo-wide.** Widen only after the narrow search fails.
4. **Read the nearby tests before editing the implementation.**
5. **Structural search when the shape matters** more than the text ("find every call to X with
   two arguments"). Fall back to text search when no structural tool is available.

## 12. Ask versus decide

Ask only when the answer changes the outcome AND the call belongs to the owner: conflicting
requirements, an architectural fork with real tradeoffs, a product, pricing, legal or safety
judgment, anything irreversible or outward-facing, or scope materially larger than requested.
Batch the questions into one round.

Do not ask about cosmetics, conventional defaults, reversible low-stakes choices, or anything
derivable from the code and docs. Make the call, state it in one line, keep moving.

## 13. Documentation is part of the change

- **Docs live next to what they describe.** Do not dump new files at the repo root.
- **Changed a decision, contract, or rule? Update its doc in the same change.** A stale doc is
  worse than no doc: it is believed.
- **Each rule lives in exactly one place.** The index links, the owning document details.
  Duplicated rules drift and then disagree.
- **Decisions are append-only.** Supersede a decision with a new dated one, never rewrite the
  record. The reasoning that was wrong is the most useful part of the history.
- **Maintenance is incremental and on contact.** No full rewrites in the middle of a feature.
