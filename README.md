# pstack (adopted)

Harness-agnostic agent skills, adopted from Lauren Tan's
[pstack](https://github.com/cursor/plugins/tree/main/pstack) and rewritten to name
no harness.

This is not a fork. Nothing here is copied verbatim. The ideas are hers; the
portability layer and the failure modes encoded in the tests are local.

## Why harness-agnostic

The original skills assume one harness: its task tool, its agent types, its model
slugs, its plugin manifest. Those are the fastest-rotting nouns in the stack. A
skill that says "spawn a `scout`" breaks silently the day `scout` is renamed.

So the split here is:

- **Skills** carry logic and name no mechanism.
- **Adapters** (`references/harness-<name>.md`) carry mechanisms and no logic.
- **The contract** (`references/harness-contract.md`) defines the eight verbs both sides use.

A test fails the build if a skill body names a harness token. That is enforced,
not aspirational.

## Skills

| Skill | Use when |
|---|---|
| `create-verification-skill` | A project has no scripted way to prove its behavior end to end. Builds a control script plus a feature map. |
| `maintain-verification-skill` | The verification skill or feature map may have drifted from the code. One source sweep, one live pass, corrections only where a run proves drift. |

Both are extractions of the two most load-bearing skills in the original pack.
Everything else in pstack composes on top of them; start here.

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
