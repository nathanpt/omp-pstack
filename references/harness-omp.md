# Harness adapter: OMP

Maps the eight verbs in `harness-contract.md` to OMP mechanisms, tested on
OMP 18.18.3.

**Authority.** `agent-orchestration` (a local skill, not part of this library) is
the authority on OMP dispatch. Where this file and that skill disagree, that
skill wins and this file is the bug. Read it before changing anything here.

## Verbs

| Verb | OMP mechanism |
|---|---|
| `delegate` | Native `task` with a named agent type. Bundled types: `task` (full access), `scout` (read-only research), `reviewer` (quality/security), `security-reviewer`, `sonic` (mechanical only), `seance`. Do not shell out to nested `omp -p` invocations for dispatch. |
| `collect` | `agent://<id>` returns the latest completed output. `history://<id>` returns the transcript. Nested ids are dotted. |
| `await` | Native result delivery with a bounded deadline. Do not poll a model in a loop. `agent://` reports status while unpublished. |
| `isolate` | `isolated: true` **on every task that writes.** Setting it globally does not isolate individual assignments. Native isolation may use independent copies rather than git worktrees; confirm the mechanism when it matters. |
| `model-role` | `@task`, `@smol`, `@slow`, `@plan` resolve through `modelRoles` in `config.yml`. Do not hardcode provider or model ids at dispatch, and do not override a configured agent's role mapping. |
| `register` | Four roots, all at depth one. **Global:** `~/.omp/agent/skills/<name>/SKILL.md`. **Project:** `<project>/.omp/skills/<name>/SKILL.md`. **User agents:** `~/.agents/skills/<name>/SKILL.md`. **Walk-up:** `.agent/skills` or `.agents/skills` found from the project upward. Nested copies at `<root>/vendor/<name>/SKILL.md` are not discovered. Symlinked directories at depth one are followed. Prefer the project root for anything project-specific. |
| `run` | Direct command execution. Read the exit code separately from the output; a shell wrapper can mask an inner failure. |
| `ask-human` | Ask in the session. Reserve it for irreversible actions and decisions that are genuinely not the agent's. |

## Adversarial seating (used by `interrogate`)

Two adversaries, on the same two seats arena uses: `@arena-a` and `@arena-b`.
Dedicated roles keep these prices separate from `@reviewer` and `@advisor`, which
have other jobs, and `@advisor` in particular is also the live advisor that reads
every turn. Seating an adversary on `@task` would put it on the caller's own
family and halve the point of running two.

Repros are the one case where isolation must **retain** rather than apply. An
adversary must write a repro to prove a finding, so isolation is mandatory, but
nothing it writes may reach the working tree. Prefer retained artifacts with
apply disabled, and read the repro out of the isolated copy when verifying.
Confirm which mechanism the installed version uses before relying on a path.

### Where isolated copies land

OMP's isolation decides this, not the skill, so check the mechanism before
dispatching. Native isolation may hand each worker its own copy in a location the
harness manages, and a hand-rolled copy lands wherever the agent invents one.

Observed failure (2026-11-11): an interrogate run with no location rule created
`sibling-of-project/seat-a` and `seat-b`, each a full 514 MB copy, outside the
project, outside git, and with nothing to remove them. The skill had said "its own
isolated copy" and never said where.

So confirm the location before dispatching. If the answer is "the agent chooses",
follow `references/isolation.md` and pick a disk-backed root.

On this machine that root is `/mnt/dev/tmp`, not `/tmp`. `/mnt/dev` is ext4 with
roughly 750 GB free, while `/tmp` is tmpfs: 16 GB of RAM, 4.1 GB free at the time
of writing. A single run already reached 1.1 GB because each copy carried the
project's 676 MB virtualenv. Copies in tmpfs consume memory and disappear on
reboot.

Copies land at `<scratch-root>/<skill>-<project>/seat-<x>/`.

A seat that never reports is a gap. OMP reports agent state, so check for a
terminal state rather than inferring success from absence of error.

## Arena seating

All seats sit on flat-rate plans. Nothing here should touch a per-token provider.

| Seat | Role | Resolves to | Why this one |
|---|---|---|---|
| Candidate A | `@arena-a` | `openai-codex/gpt-6-luna:max` | Cheaper tier of the strongest code family. Candidates generate bulk, so pay for volume rather than peak |
| Candidate B | `@arena-b` | `opencode-go/deepseek-v4.1-flash:max` | Third family, fast and inexpensive |
| Judge | `@judge` | `zai/glm-5.3:max` | The only family left that neither candidate occupies |

### The judge shares the caller's family, and that costs something

Three authenticated families: `zai`, `openai-codex`, `opencode-go`. The caller
runs on `zai`, the candidates occupy the other two. So the judge must either
share the rubric author's family or share a candidate's.

Sharing the rubric author's is the lesser problem. A judge on `zai` still reads
both candidates cold, which is the point of judging. A judge on a candidate's
family would be scoring an artifact built by its own priors, which is worse than
correlated framing.

What it costs: the judge and the session that wrote the rubric share a family,
so their agreement confirms your framing rather than testing your candidates.
Weight it accordingly, in this order:

- **Disagreement is the strong signal.** Take it seriously and read both
  rationales. A same-family judge that still disagrees with your scoring has
  found something.
- **Agreement is weak.** Do not treat it as confirmation. Your own
  criterion-by-criterion read is the primary verdict, not a cross-check on his.
- **Say which judge ran, and that it shares your family.** In the report.

### No fallback judge

There is no fourth family to fall back to, and a fallback on a candidate's
family would be worse than no judge at all. If `zai` quota is exhausted, do not
run arena. Wait for the quota to reset. Running arena without a judge that meets
the rule produces a verdict you should not act on.

`@judge` and `@slow` currently resolve to the same model. They stay separate
names because the judge is the one seat that may need re-pointing on its own, and
collapsing them would make that change reach the wrong callers. `@slow` remains
off limits for a candidate seat.

Do not seat a candidate on `@slow`. It resolves to the `zai` family and draws on
the same plan as the interactive session.


## Verified, not inferred

Exercised live against OMP 18.18.3:

- **Registration depth.** Two identical probe skills were placed at
  `skills/probe-flat/` and `skills/container/skills/link-probe/`. Asked the model
  which it could see: flat reported present, nested reported absent, symlinked
  reported present. So: depth one only, symlinks followed.
- **Project-local root.** A throwaway project containing only
  `.omp/skills/proj-probe/SKILL.md` was opened as the working directory. Asked
  the model whether it could see `proj-probe`: reported present. Confirmed again
  in a real repository (2026-11-10), where `.omp/skills/verify-<project>/` was
  discoverable and the repo-root `skills/` directory was not.
- **Agent types.** Enumerated from `omp agents unpack` into a throwaway
  directory. The six bundled definitions and their `spawns:` nesting are observed
  config, not documentation.
- **Model roles.** `@task` / `@smol` / `@slow` / `@plan` appear in the bundled
  agent frontmatter as `model:` values.

Not independently exercised here: `collect` and `await` latency behaviour under
concurrency, and `isolate` on a repository large enough for copy cost to matter.
Treat those as read-from-documentation until someone runs them.

## Choosing between the two roots

Put a project-specific skill (a `verify-<project>` control skill, a repo's own
conventions) in the **project** root. Put a reusable skill you want in every
session in the **global** root.

The failure mode of getting this backwards: a project verifier in the global root
appears in every unrelated project, points at paths that do not exist there, and
teaches agents that skills sometimes lie. A skill that references
`scripts/verify.py` is meaningless in a repo with no such file.

## Gating a skill

OMP honours `disable-model-invocation: true` in skill frontmatter, and aliases it
to `hide`: the skill leaves the catalog entirely rather than merely being
unselected. It stays loadable by name through `skill://<name>` and invocable as
`/skill:<name>`, but nothing surfaces it and an agent will not find it alone.

`interrogate` and `arena` set it deliberately. This repo is OMP-first, so the key
is no longer treated as non-portable. It stays banned in skill prose, where naming
it would couple the text to the harness.

## Notes

- `agent-orchestration` forbids Tern pane automation and nested shell `omp` for
  dispatch. Anything here that appears to require a pane is a design error.
- Alignment with an existing local rule is worth more than a clever mechanism.
  When a mapping only works by contradicting `agent-orchestration`, the mapping
  is wrong.
