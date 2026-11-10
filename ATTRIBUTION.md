# Attribution

## Upstream

[pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan
(`@poteto`) — Copyright (c) 2026 Lauren Tan, MIT.

Upstream describes a set of 58 skills for rigorous engineering work, developed
against Cursor, Claude Code, and Grok Bot.

## What was taken

Two skills, as ideas rather than text:

**`create-verification-skill`** — the concept of generating a project-local
verification skill containing a control script and a feature map; the argument that
verification is infrastructure rather than an instruction; the properties of an
agent-friendly CLI (composable, machine-readable, `--dry-run` on destructive
commands, errors that name the fix, subcommands over flags, real help text); and
the "materialized memory" framing of the feature map.

**`maintain-verification-skill`** — the maintenance loop: sweep the source, run one
live pass, correct only what a run proves, deliver as one bounded change.

## What was changed

Everything else. Specifically:

- **No mechanism names in skill bodies.** Upstream says `subagent_type`,
  `Task`, `run_in_background`, `/loop`, cloud agents, model slugs. Those are
  replaced with eight contract verbs, with mechanisms moved to adapters.
- **No harness-specific frontmatter.** Upstream sets `disable-model-invocation` on
  nearly every skill. That key is harness-specific, so it is absent here and
  documented as an install-time option instead.
- **No model routing.** Upstream's `/setup-pstack` writes per-role model config.
  Omitted; capability tiers resolve through each harness's own configuration.
- **Rewritten prose.** Short declarative sentences, no rhetorical padding, and
  failure modes stated as consequences rather than preferences.
- **Tests.** Upstream ships no tests for its skills. This repo enforces portability,
  size discipline, section coverage, and adapter completeness mechanically.
- **Scope.** Two skills, not 58. The other 56 compose on top of verification, so
  they were deliberately deferred until this pair proves useful.

## What was deliberately not carried over

- The 2,000-PRs-a-month framing. It is real for a team on a mature harness and
  meaningless as a target for a single operator.
- "I don't believe in planning." This repo takes no position on planning; that
  conflict belongs to the project standard, not to a verification skill.
- Any dependency on cloud execution, stacked pull requests, merge queues, or
  review bots.

## Ideas credited but not yet implemented here

`one owner per PR with an independent verifier`, `only findings a run proves
survive`, and the triage → reproduce → bounded-fix → draft-PR boundary contract.
Those are recorded as design references for the issue-loop work, not shipped as
skills.
