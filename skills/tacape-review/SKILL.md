---
name: tacape-review
description: >
  Compressed code review. One line per finding: location, problem, fix. Severity ranked, no praise,
  no scope creep, capped and never silently truncated. Language and framework agnostic.
  Use when the user says "review this PR", "code review", "review the diff", or invokes
  /tacape-review.
---

Review the diff. One line per finding. No praise. No summary paragraph. No preamble.

## Output format

```
path/to/file:42   BLOCKER  Internal record returned unfiltered. Whitelist the exposed fields.
path/to/other:88  MAJOR    Catch logs only on a retried path. Route it to the alerting system.
path/to/view:12   MINOR    Loading state unhandled, renders blank. Add the loading branch.
```

| Severity | Meaning |
|---|---|
| **BLOCKER** | Data loss, security hole, silent failure in production, broken boundary. Do not merge. |
| **MAJOR** | Wrong behavior on a real path, missing test on the critical path, internal shape leaked. |
| **MINOR** | Works, will bite later: naming, duplication past the third, missing state branch. |

Cap at 8 findings. Past 8, report the top 8 and state how many were dropped and of what kind.
Never truncate silently: a short list reads as "nothing else was wrong".

## What to check

Ordered by what actually causes incidents.

1. **Exposure.** An internal record, error, or object returned to a caller you do not control
   without an explicit field whitelist.
2. **Boundaries.** A module reaching into another's internals instead of its public interface.
   A dependency pointing the wrong way. A new cycle.
3. **Ownership.** A generic mechanism declaring or mutating domain state it cannot fully observe.
4. **Silent failure.** A caught error on a retried or scheduled path that never reaches alerting.
   A bare print instead of structured logging. An empty catch.
5. **Fragile error matching.** Pattern-matching a wrapped error's surface field instead of walking
   the cause chain. Breaks invisibly on the next version bump.
6. **Tests.** New critical path with no integration test. A test that mocks the very boundary the
   change touches. A bug fix with no reproducing test.
7. **Validation.** Untrusted input used before parsing. Re-validation scattered instead of done
   once at the edge. An invalid state the types still permit.
8. **Time and data.** A timestamp stored as local wall-clock. A date formatted with no explicit
   timezone. Domain state smuggled into the convenient record.
9. **Copy and locale.** Mixed-language identifiers. An internal enum or code rendered raw to a
   user. U+2014 em dash, or the `X - Y - Z` dash-parenthetical, in user-facing text.
10. **Interface states.** An async view missing loading, empty, or error. A forked component
    variant that should have been a parameter.
11. **Secrets and destruction.** A credential in the diff. A command that prints secret values.
    An irreversible operation with no confirmation.
12. **Complexity debt.** Deep nesting, nested ternaries, a `utils` grab-bag, a factory or manager
    with one caller, a new dependency for something small.

## What to skip

- Anything the formatter or linter already owns.
- Style preference that does not change meaning or risk.
- Anything outside the diff. No scope creep, no "while you are here".
- Praise. "Nice work" carries zero information and dilutes the findings.
- Restating what the change does. The author knows.

## Close

One line: `Verdict: merge | merge after BLOCKERs | needs rework.`
Then one concrete next action, doable in under two minutes.
