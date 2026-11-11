---
name: arena
description: Use when one attempt would lock in the wrong shape, or when asked to arena, compare approaches, or pick between competing designs. Builds two candidates blind, judges them from another model family, grafts the best of the loser, and verifies the result.
disable-model-invocation: true
---

# Arena

Two candidates, judged blind, merged once. Use it when the first design you think
of would be expensive to unthink.

## Scope: the project root is the boundary

Everything here happens inside one project. A candidate works in its own copy and
nothing else. Never read a sibling project, the parent directory, or a
neighbouring repository for a pattern or fixture. If the work needs another
repository, name it in the brief instead.

## When this earns its cost

Two builds and a judge for one decision. Run it only when the cost of choosing
wrong is larger than the cost of exploring: a shape other work builds on, an
interface two projects share, a schema painful to migrate. Skip it when the
choice is reversible or the options are already concrete. And skip it when you
cannot say what good looks like, because that is a five-minute question to
yourself, not a fan-out.

## 1. Frame, and write the rubric first

State the artifact each candidate produces. Then write three to six gradeable
criteria for success on this task and keep them to yourself. The rubric is the
measuring stick in step 3.

Candidates never see the rubric. You cannot rationalise toward the nicest-looking
option when you already wrote down what good means. If you cannot write the
criteria, stop and reframe the question before spending two builds on it.

## 2. Build two candidates

Two, not more. Give each its own isolated copy of the tree and the identical
brief: the task, the shared context, its own output location, and an instruction
to write a short rationale naming the alternatives it considered and rejected.

The prompt is the contract, so both get the same one. Dispatch both in one turn,
then wait for both to finish. A candidate that produces nothing is a dropout you
record, not a silent pass.

## 3. Judge blind, then read everything yourself

Send the rubric and the candidates, labelled by position not by author, to one
judge. It scores each criterion and recommends a base with a reason. The judge
must not be from the same model family as you, because a family member shares
your blind spots and that is what you are paying to escape.

Read both end to end anyway and score them yourself. Agreement confirms the pick.
Disagreement means one of you is biased or the rubric was ambiguous, so read both
rationales rather than deferring to the judge. Pick the one a future maintainer
can extend without breaking its invariants. On a tie, prefer the cleaner boundary
and the smaller surface.

## 4. Graft, or ship the consensus

If both converged on the same shape, that is strong agreement. Ship it and graft
nothing.

If they diverge so far that no merge is possible, step 1 was under-specified.
Reframe and re-run. Do not average the divergence into something neither
candidate proposed.

Otherwise walk the loser once and take one or two things worth keeping. Fold them
in by hand so the result stays coherent under one mental model. Never paste
mechanically.

## 5. Verify the result

Prove the merged artifact works, the same way you would prove any other change.
If verification finds a problem neither candidate caught, either the frame was
wrong or you missed a graft. Fix the cause, do not paper over it.

## Report

The rubric as written before the builds. Each candidate in a line. The judge's
recommendation and where it disagreed with yours. Which base and why. Each graft
with its source. What verification ran and what it returned. Name any dropout.
