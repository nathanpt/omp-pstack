# Harness contract

Every harness runs agents differently. A skill that names a harness mechanism is
a skill that only works on one machine.

This repo is OMP-first: OMP is what it runs on today, and the only adapter any of
this has ever been executed against. This file is not a portability promise. It
is the seam that keeps the option open, and its cost is eight rows.

The vocabulary that skill bodies are allowed to use. Each harness supplies one
adapter file mapping that vocabulary to its own mechanisms. Adapters are data.
Skills are logic.

## The invariant

**A `SKILL.md` body names no harness, no tool, no model, and no path outside the
project.** It may say *delegate a read-only scout*. It may not say which call,
which agent type, or which model slug.

Mechanisms live only in `references/harness-<name>.md`. The test suite enforces
this: a harness token appearing in a skill body fails the build.

The reason is not purity. It is that harness nouns rot fastest. A skill saying
"spawn a `scout`" breaks the day `scout` is renamed, and it breaks silently,
mid-task, in the one place you cannot afford it.

## Verbs

Skill bodies and adapters use these eight verbs. Nothing else.

| Verb | Means | Notes |
|---|---|---|
| `delegate` | Hand a bounded job to a worker with its own context. | The job must carry everything the worker needs. Workers do not inherit the caller's conversation. |
| `collect` | Read a worker's result. | Prefer the worker's reported artifact over its prose. |
| `await` | Wait for a worker to reach a terminal state. | Distinguish done, blocked, failed, and timed out. A finished process is not an accepted artifact. |
| `isolate` | Give a worker its own copy of the tree. | Required for any worker that writes. Shared writes corrupt each other. |
| `model-role` | Request a capability tier (fast, deep, judgement) rather than a model id. | Tiers resolve through the harness's own routing. Never hardcode an id. |
| `register` | Make a project-local skill discoverable to the harness. | Use the location the project itself defines. If it defines none, use the adapter's documented default. Never survey sibling projects or the project's parent to infer a convention. Verify discovery rather than assuming it. |
| `run` | Execute a command in the project and read its exit code and output. | The exit code is part of the evidence. A wrapper can mask an inner failure. |
| `ask-human` | Stop and ask, because the next step is irreversible or the decision is not yours. | Reserve this. A reversible choice is not a human decision. |

## Adapter completeness

An adapter is complete when it maps all eight verbs. The test suite checks this,
so a half-written adapter fails loudly instead of silently leaving a verb
undefined at the moment a skill needs it.

Where an adapter contradicts a harness-specific skill that already exists in the
same library, the existing skill wins. This library is the new arrival. Adoption
does not grant it authority over tested local knowledge.

## Adding a harness

Copy `references/harness-omp.md`, fill in the eight verbs, run the tests, and
record in `references/evidence.md` which verbs you actually exercised versus
which you read out of documentation. Untested mappings are claims, not facts.
