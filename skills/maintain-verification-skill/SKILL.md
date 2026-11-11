---
name: maintain-verification-skill
description: Use when a project's verification skill or feature map may have drifted from the code. Runs a source sweep plus one live pass, then corrects only what a run proves wrong.
version: 0.1.0
license: MIT
---

# Maintain a verification skill

A verification skill rots silently. The code moves, the map does not, and the next
agent follows a confident instruction to a place that no longer exists, then reports
success on a feature it never reached. Maps do not fail loudly. That is the problem.

## When to run this

- On a schedule, because drift is continuous and cheap to fix but expensive to find.
- After any change that adds, renames, removes, or moves a user-visible surface.
- When a verification command fails in a way that suggests the map, not the code.

## Scope: the project root is the boundary

Read and correct only inside the project you were asked about. Never open a sibling
project, a parent directory, or a global skill library to see how something is done
elsewhere; their conventions are not this project's.

## 1. Sweep the source

Locate the target first: the project-local skill whose body has launch and drive
sections plus a feature map. Several candidates, ask which. None, point at the
create skill rather than inventing a target. Then enumerate the surface from the
code, not the map: entry points, commands, options, routes, exported functions,
whatever the project's observable edge is.

Diff that list against the map. The diff is the work item.

## 2. One live pass

Actually run each documented command. This is the step that gets skipped and the
only step that produces evidence.

For each command, record one of three outcomes:

- **ran, matched** — the map is right
- **ran, diverged** — the map or the code changed; investigate which
- **could not run** — a precondition is missing, or the command is gone

"No output but exit zero" is not a match. Check what it was supposed to produce.

## 3. Correct only what a run proved

A correction needs a reason you can point at: the command errored, the flag no
longer exists, the assertion no longer holds, the feature is gone.

Do not "improve" wording, reorganise files, or add features while you are in
here. A maintenance pass that also redesigns is unreviewable, because nobody can
tell drift corrections from preference.

## 4. One bounded change

Deliver the corrections as a single reviewable unit — one branch, one pull
request, one description listing each drift and its evidence. If there are more
than a handful, split by feature area rather than shipping an unreviewable wall.

State explicitly which commands you could not run. Silently omitting them reads as
"all verified". Never record a command as verified when what you verified was that a
file exists: an agent marking a feature green from documentation rather than behavior
is the failure this skill exists to catch.

## 5. Report

- drift found, per feature: map wrong, code wrong, or gone
- commands run, and their actual result
- commands not run, and the missing precondition
- corrections made, each tied to its evidence
- anything you noticed but deliberately left alone

## Stop conditions

- **The map is right and nothing drifted.** Say so and stop. Do not manufacture
  edits to look productive.
- **The control script is broken, not the map.** That is a bug fix in the project,
  not a maintenance pass. Report it instead of papering over it in the map.
- **A command fails because a precondition is missing** (no fixture, no
  credentials, no seeded data). Report it as unverifiable. Do not guess what it
  would have printed.
