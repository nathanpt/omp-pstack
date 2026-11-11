# Evaluation: does the vendored verification pair pay for itself?

Run recorded 2026-11-11 against a private target project. Last re-checked the
same day.

The question this file answers is not "is pstack good." It is narrower. Two
skills were taken from Lauren Tan's pack. Did they produce work worth the cost
of adopting them, in a real project, or would hand-writing the same thing have
been cheaper?

The answer below rests on one target project and one harness. Treat it as a first
data point, not a settled verdict. The target project is deliberately not named;
it is private, and nothing here needs it to be identifiable.

## Subject

- **Library:** this repo at commit `0548ffe`, holding `create-verification-skill`
  and `maintain-verification-skill`.
- **Target:** a private data-ingestion project with a documented CLI, a manifest
  format, and a deliberate module layering. The verification work landed there as
  a single commit adding the control script, the project skill, the feature map,
  and two guard tests.
- **Harness:** OMP 18.18.3. The skills were discovered through symlinks at depth
  one in `~/.omp/agent/skills/`.

## What was actually built in the target

| Artifact | Size |
|---|---|
| control script, 5 subcommands | 703 lines |
| project skill | 39 lines |
| feature map, 4 files | 187 lines |
| guard tests, 2 cases | 58 lines |

## What was measured

Run from the target repo root with the object-store environment variables removed
from the environment:

```
python scripts/verify.py all
```

| Property | Measured |
|---|---|
| Exit code | 0 |
| Checks | 3 (`cli`, `plan`, `idempotent`) |
| Assertions | 28 (cli 7, plan 16, idempotent 5) |
| Failures | 0 |
| Wall time | about 3.2s |
| stdout | 1 line, 3,312 bytes, parses as one JSON value |
| stderr | 32 lines of library noise |
| Assertions that drive the create path | 8 |
| Tree state | dirty, 6 modified and 4 untracked files of unrelated feature work |

The dirty-tree result matters. The offline set stayed green while the repo
carried in-flight work on a different feature, so the control script is not
coupled to unrelated churn.

Two claims from the original run were re-checked rather than carried forward.
The stdout byte count grew from 2,391 to 3,312 because the create-path
assertions were added after that run. The earlier finding that the create path
was never driven is now false, and this file records it as closed.

## Independently verified versus reported

The distinction matters because an agent's summary of its own work is a claim,
not evidence.

| Claim | Status |
|---|---|
| Offline `all` set passes, 3 checks | Verified by running it |
| stdout is exactly one parseable JSON value | Verified with streams redirected separately |
| A failed check carries a fix hint and no traceback | Verified by reading the guard test that asserts it |
| Project-local `.omp/skills/` is discovered | Verified with a throwaway probe |
| The 8 create-path assertions exist and pass | Verified in the JSON report |
| Those assertions fail when the create path breaks | **Not verified.** See gaps |
| Red to green on the original three checks | Reported by the agent, not reproduced here |
| Full suite green, linter and type checker clean | Reported by the agent, not reproduced here |

## Verdict

Worth it, with conditions.

The value was never the code. Writing 703 lines of Python is a day's work at
most. The value was the four traps the feature map now records, because each one
cost a failed run to find and each will cost the next reader nothing:

- One asset class chunks its gap detection **per hour**, so a daily bar never
  covers a range. Covered-range checks must use the class that spans the range,
  not the convenient one.
- The metadata bootstrap reaches the provider network on a cache miss **even at
  full coverage**, so offline retrieval needs a pre-seeded metadata cache.
- The planner's vocabulary is `skip|fill|create|append|refresh`, and the totals
  do not count planned actions in status or dry-run.
- Three third-party libraries print past stdout redirection, so the script
  silences stdout at the file-descriptor level.

A person writing this from scratch finds those by losing the same runs. That is
the trade the skill actually makes. It front-loads a discipline that forces the
traps out, and the map is where they stay.

The second thing it bought is the shape of the output. One JSON value on stdout,
all noise on stderr, a fix hint on every failure. That is what makes the script
usable by a later agent instead of only by its author.

## Price

What it cost, against the hand-written alternative.

The run consumed one agent session against a repo that already had a documented
CLI surface. Judged by artifact size the mechanical output is small, under a
thousand lines. Judged by what a human would have skipped, the cost sits in the
parts nobody writes unprompted. A person writing a smoke test by hand writes a
subprocess call and checks the exit code. They do not write 28 assertions, they
do not seed a local store to prove idempotency, and they do not discover the
chunking trap before it bites.

That is the honest accounting. The skill does not save typing. It removes the
option to stop early.

## Gaps this evaluation does not close

- **The create-path assertions were never red-tested.** They pass, and their
  assertion text is specific enough to be real. Nobody has proven they fail when
  the behavior breaks. The original three checks have a reported red-to-green
  trail; these eight do not. Until that is done they are plausible, not proven.
- **A red test that avoided touching the target source proved nothing.** Hiding
  the task runner from `PATH` meant the control script never started, so the
  experiment tested the shell. The failure path for a missing prerequisite is
  therefore also untested.
- **The storage check is not part of the offline set.** It needs a live
  object-store endpoint and is excluded from `all` for that reason. The claim that
  the storage boundary works rests on one read-only run against a live endpoint.
- **One target project.** It has a documented CLI, a manifest format, and a
  deliberate layering. A project without those may not support this shape at all.
- **One harness.** Only OMP was exercised. The `references/harness-contract.md`
  verbs are asserted portable by test, not by a second harness running them.
- **The map has not been maintained.** `maintain-verification-skill` has never
  been run against the target since the map was written, so the claim that it
  prevents drift is untested.

## Defects the evaluation found

Three, all fixed in this repo rather than worked around:

1. **Containment.** A run inside the target walked to a sibling project and
   reported that project's skill convention instead of the target's. The cause
   was a register verb that said "verify, do not assume" without naming a
   boundary. Both skills now carry a scope section fenced to the project root,
   and a test fails if it is removed.
2. **The adapter documented only the global skills root.** OMP also discovers
   `<project>/.omp/skills/<name>/SKILL.md`, which was missing until commit
   `0548ffe`.
3. **A legacy skill directory went unacknowledged.** The target carries skills
   under a different harness's directory, which OMP does not scan. A run that
   silently steps past a skill directory it did not use is reporting an
   incomplete survey.

## Consequence for the next skill

`interrogate` was the planned third adoption. This evaluation argues against
adding it yet. The pair here has a proven green path and an unproven failure
path, and a third skill would add surface before the second one has a verdict
anyone can audit. The next useful work is small and closed: red-test the eight
create-path assertions, and run `maintain-verification-skill` once against the
target to see whether it actually catches drift.

## Reproducing this

```
git clone <this repo> ~/.omp/agent/skills/pstack
cd ~/.omp/agent/skills/pstack && ./install.sh ~/.omp/agent/skills
cd <target project>
python scripts/verify.py all | python3 -m json.tool
```

Record the exit code, the check names, the assertion count, and the stdout byte
count. If stdout is more than one line, something is printing past the
file-descriptor silencing and the output contract has regressed.
