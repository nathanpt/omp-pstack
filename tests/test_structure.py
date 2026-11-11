"""Structure tests: size discipline, section coverage, and adapter completeness."""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"
REFERENCES = REPO / "references"
CONTRACT = REFERENCES / "harness-contract.md"

# Procedures need room for numbered steps. This is a ceiling, not a target.
#
# Raised 85 -> 110 on 2026-11-11. At 85 every skill sat at 0-1 lines of headroom,
# so each improvement forced a deletion, and the deletions removed the reason
# rather than the padding: the address a copy goes to, what it costs, and when it
# is torn down all fell out of a port under this cap. It stopped bloat by making
# every skill the same size and punished the clauses that explain why.
#
# The cap was always a proxy for "readable cold", which is what actually matters.
# That property is now guarded directly by the duplicate-rule test below, which
# fails when one rule is stated in two skill bodies. Size alone never caught that.
MAX_SKILL_LINES = 110
VERB_COUNT = 8
DUPLICATE_RULE_WORDS = 8


def skill_files():
    return sorted(SKILLS.glob("*/SKILL.md"))


def adapter_files():
    """Adapters only. The contract defines the verbs; it does not map them."""
    return sorted(p for p in REFERENCES.glob("harness-*.md") if p != CONTRACT)


def contract_verbs():
    """The verb names defined in the harness contract table."""
    text = CONTRACT.read_text()
    return re.findall(r"^\|\s*`([a-z][a-z-]+)`\s*\|", text, re.M)


class SizeDisciplineTests(unittest.TestCase):
    def test_skills_stay_small(self):
        for path in skill_files():
            lines = len(path.read_text().splitlines())
            with self.subTest(skill=path.parent.name):
                self.assertLessEqual(
                    lines, MAX_SKILL_LINES,
                    f"{path.parent.name}/SKILL.md is {lines} lines; move content into "
                    "references/ rather than raising this ceiling",
                )

    def test_no_rule_is_stated_in_two_skill_bodies(self):
        """One rule, one statement. Two statements drift and nobody notices which wins.

        This is the property size limits were standing in for. A line cap never
        caught duplication, because two copies of a rule cost exactly as much as
        one and a cap cannot tell them apart. Shared phrasing can.
        """
        def sentences(path):
            # Section headings are structural and required in every skill, so they
            # repeat by design. Rules are prose.
            prose = " ".join(
                line for line in path.read_text().splitlines()
                if not line.lstrip().startswith("#")
            )
            body = " ".join(prose.split())
            return {
                " ".join(s.split())
                for s in re.split(r"(?<=[.!?])\s+", body)
                if len(s.split()) >= DUPLICATE_RULE_WORDS
            }

        seen = {}
        for path in skill_files():
            for sentence in sentences(path):
                seen.setdefault(sentence, []).append(path.parent.name)

        offenders = {
            s: names for s, names in seen.items() if len(set(names)) > 1
        }
        self.assertEqual(
            offenders,
            {},
            "These sentences appear in more than one skill body, so the rule has two "
            f"sources: {offenders}. State it once, in references/, and point at it.",
        )

    def test_reference_files_exist_and_are_linked(self):
        """Every reference on disk is reachable from the skill that ships it."""
        for path in skill_files():
            body = path.read_text()
            refs = path.parent / "references"
            if not refs.is_dir():
                continue
            for ref in sorted(refs.rglob("*.md")):
                rel = ref.relative_to(path.parent).as_posix()
                with self.subTest(skill=path.parent.name, ref=rel):
                    self.assertIn(
                        ref.name, body,
                        f"{rel} exists under {path.parent.name} but the SKILL.md never "
                        "points at it, so it will not be read",
                    )


class SectionCoverageTests(unittest.TestCase):
    REQUIRED = {
        "create-verification-skill": (
            "## Scope: the project root is the boundary",
            "## 1. Establish the observable surface",
            "## 2. Build the control script",
            "## 3. Build the feature map",
            "## 4. Wire the project-local skill",
            "## 5. Prove it before declaring it done",
            "## Anti-patterns",
        ),
        "maintain-verification-skill": (
            "## Scope: the project root is the boundary",
            "## 1. Sweep the source",
            "## 2. One live pass",
            "## 3. Correct only what a run proved",
            "## 4. One bounded change",
            "## 5. Report",
            "## Stop conditions",
        ),
        "arena": (
            "## Scope: the project root is the boundary",
            "## When this earns its cost",
            "## 1. Frame, and write the rubric first",
            "## 2. Build two candidates",
            "## 3. Judge blind, then read everything yourself",
            "## 4. Graft, or ship the consensus",
            "## 5. Verify the result",
            "## Report",
        ),
        "interrogate": (
            "## Scope: the project root is the boundary",
            "## 1. Frame the scope and the intent",
            "## 2. Seat two adversaries",
            "## 3. Verify every finding yourself",
            "## 4. Account for every seat",
            "## 5. Report",
            "## Anti-patterns",
        ),
    }

    CONTAINMENT = (
        "sibling project",
        "parent directory",
    )

    def test_every_skill_states_its_containment_rule(self):
        """A skill that does not fence itself invites a walk into neighbouring projects.

        Observed failure: a run inside one project read a sibling project's
        skills layout and adopted it as the local convention, ignoring the
        project's own skills directory. The fix is a stated boundary, and this
        test keeps it from being edited away.
        """
        for path in skill_files():
            body = " ".join(path.read_text().split())
            with self.subTest(skill=path.parent.name):
                self.assertIn("## Scope: the project root is the boundary", body)
                for phrase in self.CONTAINMENT:
                    self.assertIn(phrase, body, f"{path.parent.name} never forbids {phrase!r}")

    def test_required_sections_present(self):
        for path in skill_files():
            expected = self.REQUIRED.get(path.parent.name)
            if not expected:
                continue
            body = path.read_text()
            for section in expected:
                with self.subTest(skill=path.parent.name, section=section):
                    self.assertIn(section, body)

    def test_skills_teach_the_discovery_mechanism(self):
        """A generated skill nobody can discover is a skill that does not exist.

        Observed failure: an agent wired the skill correctly, then patched
        discoverability into a rules file because nothing told it the skill's
        description is what a harness advertises. The rules file was local-only
        and the skill shipped, so the two drifted immediately.
        """
        body = " ".join((SKILLS / "create-verification-skill" / "SKILL.md").read_text().split())
        self.assertIn("description is the discovery mechanism", body)
        self.assertIn("never registers", body)
        self.assertIn("a vague one never fires", body)
        self.assertIn("adding a rules-file pointer when discovery fails", body.lower())

    def test_maintain_locates_its_target_before_sweeping(self):
        body = " ".join((SKILLS / "maintain-verification-skill" / "SKILL.md").read_text().split())
        self.assertIn("Locate the target first", body)
        self.assertIn("Several candidates, ask which", body)
        self.assertIn("point at the create skill", body)

    def test_steps_are_ordered(self):
        """Numbered steps must appear in ascending order, not just exist."""
        for path in skill_files():
            body = path.read_text()
            numbers = [int(n) for n in re.findall(r"^## (\d+)\.", body, re.M)]
            if len(numbers) < 2:
                continue
            with self.subTest(skill=path.parent.name):
                self.assertEqual(numbers, sorted(numbers), f"steps out of order: {numbers}")
                self.assertEqual(numbers, list(range(1, len(numbers) + 1)))


class AdapterCompletenessTests(unittest.TestCase):
    def test_contract_defines_eight_verbs(self):
        verbs = contract_verbs()
        self.assertEqual(len(verbs), VERB_COUNT, f"contract defines {len(verbs)}: {verbs}")

    def test_every_adapter_maps_every_verb(self):
        verbs = contract_verbs()
        adapters = adapter_files()
        self.assertTrue(adapters, "no harness adapter found")
        for adapter in adapters:
            text = adapter.read_text()
            for verb in verbs:
                with self.subTest(adapter=adapter.name, verb=verb):
                    self.assertIn(
                        f"`{verb}`", text,
                        f"{adapter.name} does not map the {verb!r} verb, so a skill using it "
                        "would fail at the moment it needs it",
                    )

    def test_adapter_declares_what_was_verified(self):
        """An adapter that does not separate tested from inferred is just a guess."""
        for adapter in adapter_files():
            text = adapter.read_text()
            with self.subTest(adapter=adapter.name):
                self.assertIn("## Verified, not inferred", text)


if __name__ == "__main__":
    unittest.main()
