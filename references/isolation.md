# Isolated copies

Every skill that fans out workers needs each worker to write without touching the
real tree. This file is the single place that says where those copies live, what
they cost, and when they go away. Skills point here rather than restating it,
because three statements of the same rule drift.

## Where

Outside the project, on a **disk-backed** filesystem, in a directory named for the
project and the seat.

- Never beside the project. A sibling directory is invisible to `git`, surprises
  the developer, and is found by accident weeks later.
- Never inside the project. A copy inside the tree is one `git add` away from
  being committed.
- Never assume the system temporary directory is a disk. On many Linux systems
  `/tmp` is `tmpfs`, so "scratch space" is RAM: copies compete with running
  processes, capacity is the machine's memory rather than its disk, and everything
  vanishes on reboot along with any repro a worker still needed.

Check `df -hT` on the candidate root before writing. If `Type` is `tmpfs`, pick a
different root. A copy of a real project is hundreds of megabytes, and two seats
run at once.

The operator designates the scratch root. Name each copy for the project and the
seat so it is identifiable and removable without guesswork.

## What it costs

Measure before copying. A project copy is not a source checkout: it carries
whatever the worker needs to run, including dependency trees and data fixtures
that are usually git-ignored and usually the largest thing in the directory.

Two choices, and pick deliberately rather than by habit:

- **Copy everything.** The worker gets a working environment immediately and you
  pay the full size per seat. Fine for small projects or a single run.
- **Exclude the dependency tree.** Use a worktree for tracked files, or copy and
  drop the install directory. The worker must then build its own environment
  before it can prove anything, which costs time rather than disk.

A worktree is only cheap if the worker does not need what a worktree omits. Say
which choice you made and what the worker must do first, in its brief.

## Secrets travel with the copy

A copy carries whatever the working tree carries, and that includes credentials:
`.env` files, provider keys, tokens, service-account files. A worker told to read
only is not prevented from spending money, because the vendor's client library
does not know the worker's intent.

This is not hypothetical. On a real run, a seat's first repro constructed a live
market-data client from a `.env` in its copy and made two billable API calls
before the seat noticed and scrubbed its own environment. Both seats then worked
around it by hand. Nothing in this file had told them to, and the next seat might
not be as careful.

Before a worker starts, make it unable to reach a paid or production service:

- **Blank the real values.** Substitute obvious dummies for every credential in
  the copy, and leave the variables present. Deleting the file outright can make a
  project fail at config validation instead of exercising the code, which hides
  the very behavior you are testing.
- **Point endpoints at a closed port.** `127.0.0.1:1` resolves, refuses
  immediately, and needs no network. Reserve a real endpoint for a run that
  genuinely requires one, and say so in the brief.
- **Keep the network out of the proof.** If a finding needs a vendor, mock it in
  the repro. A finding that requires a live account is not reproducible by the
  operator, which makes it not a finding.

Say in the brief which credentials were neutralized and how. A run that reached a
live API has failed isolation regardless of what it found, and that failure
belongs in the report rather than in a footnote.

## Teardown

Remove the copies when the run ends, in every outcome including a failed run.
Left-behind copies accumulate silently, one per run, and nothing else will
collect them.

Teardown removes copies and scratch state. It never removes the evidence: the
proof is the command and the output the worker reported, which lives in your
report, not in the tree it worked in. Confirm a reported proof is captured before
deleting the copy that produced it.

If a copy must survive for a follow-up, say so and where, rather than letting it
persist by omission.
