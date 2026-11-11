# Evidence

What was exercised versus what was read. Untested mappings are claims, not facts.

## Tested live — OMP 18.18.3

**Skill discovery depth.** Three probe skills, identical bodies, different layouts,
asked the model which it could see:

| Layout | Reported visible |
|---|---|
| `skills/probe-flat/SKILL.md` | yes |
| `skills/container/skills/link-probe/SKILL.md` (depth 3) | no |
| `skills/link-probe` symlink → container | yes |

Conclusion: discovery is exactly one level; symlinked directories are followed.
This is why `install.sh` symlinks rather than copying, and why this repository can
live inside the skills directory without being mistaken for a skill.

**Project-local discovery root.** Two independent confirmations:

- A throwaway project containing only `.omp/skills/proj-probe/SKILL.md`, opened as
  the working directory, reported the skill visible (`PROJLOCAL=yes`).
- A real repository where `.omp/skills/verify-fin3/` resolved via `skill://` and
  the repo-root `skills/` directory did not.

Conclusion: `<project>/.omp/skills/<name>/SKILL.md` is a second discovery root at
the same depth. Project-specific skills belong there, not in the global root.

**Agent types.** Enumerated with `omp agents unpack --dir <throwaway>`. Six bundled
definitions, including the `spawns:` nesting declarations. Observed config, not
documentation.

**Model roles.** `@task`, `@smol`, `@slow`, `@plan` observed as `model:` values in
the bundled agent frontmatter.

**Frontmatter gating.** `disableModelInvocation` confirmed to be honoured by the
loader, which filters skills on it. Not used in this repository.

## Read, not exercised

- `collect` and `await` behaviour under concurrency and load.
- `isolate` on a repository large enough for copy cost to matter.
- `ask-human` escalation semantics.

## Not attempted

- Any Cursor, Claude Code, OpenCode, or Pi adapter. No adapter file ships for
  those harnesses; writing one requires the same live probe this report describes,
  not a translation of the OMP file.
