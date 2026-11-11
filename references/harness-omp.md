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
| `register` | Two roots, both at depth one. **Global:** `~/.omp/agent/skills/<name>/SKILL.md`. **Project:** `<project>/.omp/skills/<name>/SKILL.md`. Nested copies at `<root>/vendor/<name>/SKILL.md` are not discovered. Symlinked directories at depth one are followed, so a container repo can hold skills while exposing them by symlink. Prefer the project root for anything project-specific: it travels with the repo and does not leak one project's verifier into every other project. |
| `run` | Direct command execution. Read the exit code separately from the output; a shell wrapper can mask an inner failure. |
| `ask-human` | Ask in the session. Reserve it for irreversible actions and decisions that are genuinely not the agent's. |

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

## Optional: quiet the skill list

OMP honours `disable-model-invocation: true` in skill frontmatter, which keeps a
skill out of automatic selection while leaving the file readable on disk. It is
**not** set in this repository, because it is a harness-specific frontmatter key
and would make the shipped files non-portable. Add it locally if the skill list
gets noisy, and expect to re-add it after an update.

## Notes

- `agent-orchestration` forbids Tern pane automation and nested shell `omp` for
  dispatch. Anything here that appears to require a pane is a design error.
- Alignment with an existing local rule is worth more than a clever mechanism.
  When a mapping only works by contradicting `agent-orchestration`, the mapping
  is wrong.
