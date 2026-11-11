---
name: create-verification-skill
description: Use when a project has no scripted way to prove its behavior end to end. Builds a project-local verification skill with a control script and a feature map, so an agent can close its own loop instead of asserting success.
version: 0.2.0
license: MIT
---

# Create a verification skill

A verification skill lets an agent check its own work against the real artifact.
Without one, every claim of done is a self-report and you are the only real test.

**Stop if the project already has one.** Extending it is `maintain-verification-skill`.

## Scope: the project root is the boundary

Work only inside the project you were asked about. Never infer a convention from a
sibling project, a parent directory, or a global skill library: a sibling's layout
is not this project's convention, and copying it produces a skill no harness loads.

- If the project has a project-local skills directory, use it. If it has several,
  use the one its own instructions name, and say which you chose and why.
- If it has none, say so and use the documented default. Never survey the parent
  directory or open a sibling project to find an example.

## 1. Establish the observable surface

List what can be seen from outside the code, ranked by what a user would notice:
command output and exit codes; files written and their shape; records read back
through the consumer's own interface; a served endpoint including status and
headers; rendered interface state.

Pick the richest surface that runs locally and cheaply. A check nobody runs
because it takes ten minutes is not a check. If nothing is observable, say so and
build the smallest harness that makes one thing observable. Do not fake a surface.

## 2. Build the control script

One entry point, one file, inside the project. Every check calls it. In order of
importance:

- **Composable interface.** Small commands that chain, not one monolith of flags.
- **Machine-readable output** by default; human formatting behind a flag. `--dry-run` on anything with side effects.
- **Errors that name the fix.** "No baseline at <path>; run `baseline capture` first."
- **Subcommands over flags**, with real help text per subcommand.

The control script is code: tested, committed, and re-run by reviewers.

## 3. Build the feature map

One index plus one file per feature area under `references/features/`, shaped by
`references/feature-map.md`. Each records what it does, how a user reaches it,
which command drives it, and its traps. The map is compressed context, not human
documentation: write it for a reader who cannot open a browser.

## 4. Wire the project-local skill

Create `verify-<project>` in the skills location Scope identified. It names two
paths: the control script and the feature map. Under thirty lines: a signpost.

Its frontmatter description is the discovery mechanism: name the project, the
surface, and when to reach for it. The harness advertises that line and nothing
else, so no frontmatter means it never registers and a vague one never fires.

Register it per the register row of `references/harness-contract.md`. If the
harness does not discover it, report that. Never invent an alternative location.

## 5. Prove it before declaring it done

Run three checks across different features and show the output. For each, break
the behavior deliberately and confirm the check fails. A check that passes when
the feature is removed is decoration.

Report: what was built, features mapped, checks red then green, what stays
unobservable, and which skills location you used.

## Anti-patterns

- **Only running the unit suite.** The gap here is the boundary tests cannot see.
- **Borrowing a sibling project's layout.** The only convention that matters is
  the one this project's harness actually reads.
- **Scripting the eyeball.** Printing a screenshot is not a check. Assert something.
- **Mapping features that cannot be driven.** That is a wish list.
- **Adding a rules-file pointer when discovery fails.** A second statement of the same command goes stale silently, and the rules file is usually local-only while the skill ships.
