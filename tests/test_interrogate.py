"""Contract tests for interrogate: the rules that make its verdict mean anything.

These are not style checks. Each one guards a behaviour whose absence would let
the skill report a confident result that is not true. The failures they prevent
are the ones that look like success.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "interrogate" / "SKILL.md"


def body() -> str:
    return " ".join(SKILL.read_text().split())


class SurvivorRuleTests(unittest.TestCase):
    def test_requires_a_rerun_before_keeping_a_finding(self):
        """An unverified finding is an opinion with a command attached."""
        text = body()
        self.assertIn("Rerun each finding's command", text)
        self.assertIn("A finding you did not rerun is not a finding", text)

    def test_survival_requires_both_failure_and_broken_intent(self):
        """A real failure that does not break the stated intent is not a finding."""
        text = body()
        self.assertIn("shows the failure and the failure breaks the stated intent", text)

    def test_no_findings_is_declared_a_valid_result(self):
        """Without this, the skill invents findings to look productive."""
        self.assertIn("No findings is a valid result", body())
        self.assertIn("no verified findings", body())

    def test_forbids_applying_fixes(self):
        """Reporting and repairing are separate acts; conflating them hides the diff."""
        text = body()
        self.assertIn("Apply no fixes", text)
        self.assertIn("Fixing what you found", text)


class HonestAccountingTests(unittest.TestCase):
    def test_gap_is_never_a_pass(self):
        """The failure that produces a confident summary built on missing data."""
        text = body()
        self.assertIn("A gap is not a pass", text)
        self.assertIn("never reads as clean", text)

    def test_dropped_findings_must_be_counted(self):
        text = body()
        self.assertIn("counted as dropped", text)
        self.assertIn("**Dropped**", text)

    def test_every_seat_must_be_accounted_for(self):
        self.assertIn("Account for every seat", body())


class SeatingTests(unittest.TestCase):
    def test_defaults_to_two_adversaries(self):
        """Diminishing returns after two or three; two families is the floor."""
        text = body()
        self.assertIn("Two is the default", text)
        self.assertIn("two seats from different model families", text)

    def test_adversaries_get_isolated_copies(self):
        text = body()
        self.assertIn("own copy per `references/isolation.md`", text)
        self.assertIn("never in the working tree", text)

    def test_copies_have_a_named_location(self):
        """Observed failure: copies landed beside the project, 1 GB, never cleaned.

        The skill said 'its own isolated copy' and never said where, so the agent
        invented a sibling directory in the projects root.
        """
        text = body()
        self.assertIn("disk-backed", text)
        self.assertIn("never beside or inside the project", text)
        self.assertIn("removed when the run ends", text)
        iso = (REPO / "references" / "isolation.md").read_text()
        self.assertIn("disk-backed", iso)
        self.assertIn("tmpfs", iso)
        self.assertIn("Teardown", iso)

    def test_names_no_model_or_harness_mechanism(self):
        """Seating is the adapter's job, not the skill's."""
        text = body()
        for token in ("@reviewer", "@advisor", "@task", "modelRoles", "gpt-", "glm-"):
            with self.subTest(token=token):
                self.assertNotIn(token, text)


class ScopeTests(unittest.TestCase):
    def test_scoped_to_code_changes_only(self):
        """Design review is the decision-record red-team skill's job."""
        text = body()
        self.assertIn("Using it on a design, plan, or document", text)

    def test_states_the_containment_rule(self):
        text = body()
        self.assertIn("## Scope: the project root is the boundary", text)
        self.assertIn("sibling project", text)
        self.assertIn("parent directory", text)

    def test_requires_intent_before_spawning(self):
        """A wrong intent makes every verdict wrong in the same direction."""
        text = body()
        self.assertIn("before spawning anything", text)
        self.assertIn("A wrong intent makes every verdict wrong", text)


if __name__ == "__main__":
    unittest.main()
