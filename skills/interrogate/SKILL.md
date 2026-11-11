---
name: interrogate
description: Use when asked to interrogate, adversarially review, multi-model review, challenge, stress test, or tear apart a change. Adversaries must prove every finding with a run, and only reproducible findings survive.
disable-model-invocation: true
---

# Interrogate

Adversaries try to break a change. A finding survives only when a run proves it.
Report what survives. Apply no fixes.

## Scope: the project root is the boundary

Everything here happens inside one project. An adversary gets a copy of this
project and nothing else. Never read a sibling project, the parent directory, or
a neighbouring repository to borrow fixtures, infer a convention, or find a
comparison. If the change genuinely depends on another repository, name that
dependency in the brief and let the adversary work without it.

## 1. Frame the scope and the intent

The scope is what the user names. Otherwise it is the diff from the merge base
with the base branch, through the working tree.

State the intent in one or two sentences, from the user's message, the commits,
and the diff. This is the yardstick every finding is measured against, so write
it before spawning anything and pass it verbatim. If the intent is unclear and
the diff does not settle it, stop and ask. A wrong intent makes every verdict
wrong in the same direction.

## 2. Seat two adversaries

Two is the default, on two different model families. Diversity is the point, and
it stops paying after two or three seats.

Give each adversary its own isolated copy of the tree. Repros are written there,
never in the working tree, and nothing is applied back. Two adversaries sharing
one tree corrupt each other's repros.

Brief each one with the scope, the stated intent, and this instruction word for
word:

> Break this change. Prove every finding with a run against the real code, such
> as a failing test, a repro script, or command output showing the wrong
> behaviour. Keep your repros in your own copy. Report each finding with a title,
> the exact command, the output it printed, and the output the intent requires.
> Leave out anything you did not run, including style, naming, structure, and
> risks that need a future change to matter. No findings is a valid result.

Dispatch both in one turn, then wait for both to reach a terminal state.

## 3. Verify every finding yourself

Rerun each claimed finding's command in that adversary's copy. Read the output
yourself rather than trusting the report.

Keep a finding only when the output shows the failure and the failure breaks the
stated intent. Drop the rest. Merge findings that share a root cause. A finding
you did not rerun is not a finding.

## 4. Account for every seat

An adversary that failed, timed out, or never reported is a gap. A gap is not a
pass, and it never reads as clean. An adversary that returned only opinions, with
nothing reproducible, is dropped and counted as dropped.

## 5. Report

- **Intent**: the restatement, unchanged from step 1.
- **Findings**: for each survivor, the command, its output, how it breaks the
  intent, and which adversaries found it.
- **Dropped**: per adversary, the count and the reason.
- **Gaps**: any seat that produced nothing, and what it cost you.
- Say **no verified findings** when none survive. That is common and it is a
  real result, not a failure.

## Anti-patterns

- Counting an opinion, a style note, or a future risk as a finding.
- Keeping a finding you did not rerun.
- Letting a silent seat become a green result.
- Fixing what you found. This skill reports; repair is a separate act.
- Using it on a design, a plan, or a document. Those cannot be proven by a run,
  so review them with the decision-record red-team skill instead.
