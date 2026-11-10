# Feature map template

One index file plus one file per feature area. Keep each entry short enough to
read in a few seconds and concrete enough that a command is obvious.

The test of a good entry: a reader who has never opened this project can drive the
feature correctly on their first attempt, without opening a browser.

---

## Index (`references/features/README.md`)

```markdown
# Features

One line per area, linking to its file. Group by what a user does, not by how the
code is organised.

- [Ingest](ingest.md): pulling source data into the store
- [Retrieval](retrieval.md): reading bars back for analysis
- [Config](config.md): how a run resolves its settings
```

---

## Per-feature file

```markdown
# <Feature name>

One sentence on what this does and who notices it.

## Sub-features

- `<name>`: what it covers, in a phrase
- `<name>`: what it covers, in a phrase

## How to reach it

From a user's point of view, in order. Include the precondition: a clean store, a
seeded fixture, an authenticated session. If reaching it needs setup, say what
setup and how to undo it.

## How to drive it

The exact commands, in the order they must run. These are copy-pasteable, not
paraphrases.

## What to assert

The observable outcomes that mean this worked. Name the value, the shape, the
count, or the exit code. "It looks right" is not an assertion.

## Traps

- State that looks like a bug and is not, with the reason.
- Orderings that matter and fail confusingly when violated.
- Things that are environment-dependent, and what to check first.
- Any sub-feature that is absent under some conditions, with the condition.
```

---

## Rules for writing these

- **Never invent a command.** If you did not run it, do not document it.
- **State preconditions.** Most confusing failures are a missing precondition, not
  a broken feature.
- **Name the trap's reason.** "This fails intermittently" without a cause teaches
  nothing and invites a retry loop.
- **Keep it current.** A stale map is worse than no map, because it produces
  confident wrong instructions. That is what the maintenance skill is for.
