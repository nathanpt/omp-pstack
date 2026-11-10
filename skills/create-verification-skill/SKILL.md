---
name: create-verification-skill
description: Use when a project has no scripted way to prove its behavior end to end. Builds a project-local verification skill with a control script and a feature map, so an agent can close its own loop instead of asserting success.
version: 0.1.0
license: MIT
---

# Create a verification skill

A verification skill lets an agent check its own work against the real artifact.
Without one, every claim of done is a self-report and you are the only real test.

**Stop if the project already has one.** Extending it is `maintain-verification-skill`.
Two overlapping verifiers are worse than one imperfect one.

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
- **Machine-readable output** by default; human formatting behind a flag.
- **`--dry-run` on anything with side effects**, or it will eventually destroy a fixture.
- **Errors that name the fix.** "No baseline at <path>; run `baseline capture` first."
- **Subcommands over flags**, so functionality discloses gradually.
- **Real help text** per subcommand, the cheapest documentation there is.

The control script is code. It gets tests and it is committed. It is the artifact
a reviewer re-runs to check the claim, which is the entire point.

## 3. Build the feature map

One index plus one file per feature area under `references/features/`. Use
`references/feature-map.md` as the shape. Each feature records what it does, how a
user reaches it, which command drives it, and its traps.

The map is compressed context, not human documentation. Write it for a reader who
has never seen the project and cannot open a browser.

## 4. Wire the project-local skill

Create `verify-<project>` inside the project, not globally. It names two paths:
the control script and the feature map. Under thirty lines. A signpost, not an essay.

Register it with the harness per the register row of `references/harness-contract.md`.
Discovery rules vary by harness and depth, so verify the skill appears rather than
assuming the file is enough.

## 5. Prove it before declaring it done

Run three checks across different features and show the output. For each, break
the behavior deliberately and confirm the check fails. A check that passes when
the feature is removed is decoration.

Report: what was built, features mapped, checks demonstrated red then green, and
what remains unobservable.

## Quality bar

Every mapped feature has a command that drives it. Every check reads the real
artifact, never a cached copy or an old log. Failure messages say what to do next.
The common case runs as one command.

## Anti-patterns

- **Only running the unit suite.** That is a test runner. The gap here is the
  boundary unit tests cannot see.
- **Scripting the eyeball.** Driving a surface and printing a screenshot is not a
  check. Assert something.
- **One command with twenty modes.** Nobody learns it and failures tell you nothing.
- **Mapping features that cannot be driven.** That is a wish list.
