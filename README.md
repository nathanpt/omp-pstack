# omp-pstack

An **OMP-first implementation** of Lauren Tan's
[pstack](https://github.com/cursor/plugins/tree/main/pstack). Her skills assume
Cursor: its task tool, its agent types, its model slugs, its plugin manifest, its
cloud agents. This repo keeps the ideas and supplies OMP's mechanisms.

This is not a fork. Nothing here is copied verbatim. The ideas are hers; the
port, the closed test suite, and the recorded failure modes are local.

## What this repo claims, precisely

It is **not** harness-agnostic, and the earlier version of this README was wrong
to say so. The accurate claim is narrower:

> One logic layer, per-harness adapters, one adapter proven.

The skill bodies are verified to name no harness token, and a test enforces it.
What has never happened is a second harness actually running them. One adapter is
not evidence of portability; it is evidence of one working adapter.

The seam is kept for a concrete reason, not for purity. A terminal multiplexer
that can open a pane and run a code session is the intended second adapter, and
one of the eight verbs maps cleanly to a pane while the rest need real work. With
the seam, that adapter is an afternoon. Without it, the logic rots into OMP nouns
and the option closes silently.

## Status: four skills, one evaluated run

`create-verification-skill` and `maintain-verification-skill` are adopted. They
have been run once against a real project, which produced a working control
script, a feature map carrying four empirically earned traps, and a proven green
path.

What they have not proven is the failure path. See
[`EVALUATION.md`](EVALUATION.md) for the measured numbers, the split between what
was verified and what was merely reported, and the gaps that remain. The short
version is that the green path is evidenced and the red path is not.

`interrogate` and `arena` followed, both built OMP-first rather than ported, and
both still without a real run behind them.

## How the split works

- **Skills** carry logic and name no harness mechanism.
- **Adapters** (`references/harness-<name>.md`) carry mechanisms and no logic.
- **The contract** (`references/harness-contract.md`) defines the eight verbs both sides use.

A test fails the build if a skill body names a harness token. That is enforced,
not aspirational. `disable-model-invocation` is the one documented exception: it
is an OMP mechanism, and since this repo no longer pretends otherwise, skills may
gate themselves with it directly instead of deferring to install time.

## Skills

| Skill | Use when |
|---|---|
| `create-verification-skill` | A project has no scripted way to prove its behavior end to end. Builds a control script plus a feature map. |
| `maintain-verification-skill` | The verification skill or feature map may have drifted from the code. One source sweep, one live pass, corrections only where a run proves drift. |
| `interrogate` | A change needs to be broken before it lands. Two adversaries on different model families, and only findings reproduced by a run survive. |
| `arena` | One attempt would lock in the wrong shape. Two candidates built blind, judged from outside both their families, best of the loser grafted in, result verified. |

The first two are extractions of the two most load-bearing skills in the original
pack. `interrogate` is the third and the first built OMP-first rather than ported.

`interrogate` and `arena` are both gated behind explicit invocation and appear in
no model-facing catalog. OMP treats that flag as `hide`, so the skill is invisible
rather than merely unselected: invoke it as `/skill:<name>`. That is deliberate.
Deciding on its own to seat two adversaries, or to spend two builds and a judge on
one decision, is not a call an agent should make quietly.

## Install

Skills are discovered at `<skills-dir>/<name>/SKILL.md` — one level only in OMP.
This repository is a container, not a skill directory, so expose each skill by
symlink at depth one:

```bash
./install.sh ~/.omp/agent/skills
```

The script refuses to overwrite an existing directory of the same name, and
prints what it linked. Uninstall with `./install.sh --uninstall ~/.omp/agent/skills`.

For another harness, read `references/harness-<name>.md` first, then run the same
script pointed at that harness's skills directory. If there is no adapter for it
yet, write one — the tests enforce that every adapter maps all eight verbs.

## What is deliberately not here

- No harness-specific frontmatter keys. Quieting auto-invocation is a per-harness
  install decision, not something shipped in a portable file.
- No model routing. Capability tiers resolve through each harness's own
  configuration.
- No orchestration playbooks yet. Verification had to exist first, because every
  other loop depends on being able to prove behavior cheaply.

## Layout

```
skills/
  create-verification-skill/
    SKILL.md
    references/feature-map.md
  maintain-verification-skill/
    SKILL.md
references/
  harness-contract.md      the eight verbs
  harness-omp.md           OMP adapter
  evidence.md              what was tested vs. read
tests/
  test_portability.py      no harness nouns in skill bodies
  test_structure.py        size, sections, adapter completeness
```

## Tests

```bash
python3 -m unittest discover -s tests
```

No dependencies beyond the standard library.

## License and attribution

MIT, matching upstream. The skills are adapted from pstack by Lauren Tan
(Copyright (c) 2026 Lauren Tan, MIT). See `ATTRIBUTION.md` for what came from
where and what changed.
