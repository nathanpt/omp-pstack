"""Contract tests for arena: the rules that stop it becoming an expensive coin flip.

Arena's failure mode is not a bad merge. It is a defensible-looking verdict
produced by a process that quietly skipped the step that makes it defensible.
Each test below guards one of those steps.
"""

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "arena" / "SKILL.md"
ADAPTER = REPO / "references" / "harness-omp.md"


def body() -> str:
    return " ".join(SKILL.read_text().split())


def adapter() -> str:
    return " ".join(ADAPTER.read_text().split())


class RubricBeforeBuildTests(unittest.TestCase):
    def test_rubric_is_written_before_anything_is_built(self):
        """A rubric written after the builds is a rationalisation of a favourite."""
        text = body()
        self.assertIn("write the rubric first", text)
        self.assertIn("The rubric is the measuring stick", text)

    def test_candidates_never_see_the_rubric(self):
        text = body()
        self.assertIn("Candidates never see the rubric", text)

    def test_refuses_to_run_without_criteria(self):
        """No rubric means the question is not ready, not that arena should guess."""
        text = body()
        self.assertIn("If you cannot write the criteria, stop", text)


class JudgeIndependenceTests(unittest.TestCase):
    def test_judge_never_sits_in_a_candidates_family(self):
        """A judge inside a candidate's family grades its own priors."""
        self.assertIn("must not sit in a candidate's model family", body())

    def test_same_family_judge_weights_disagreement_over_agreement(self):
        """A correlated judge agrees cheaply, so agreement stops being evidence."""
        text = body()
        self.assertIn("its agreement only confirms your framing", text)
        self.assertIn("treat disagreement as the strong signal", text)

    def test_judge_does_not_replace_the_operators_own_reading(self):
        """Deferring to the judge turns a second opinion into the only opinion."""
        text = body()
        self.assertIn("Read both end to end anyway", text)
        self.assertIn("your own read as the verdict", text)

    def test_candidates_are_labelled_by_position_not_author(self):
        text = body()
        self.assertIn("labelled by position not by author", text)


class ConvergenceTests(unittest.TestCase):
    def test_consensus_shape_ships_without_a_graft(self):
        text = body()
        self.assertIn("that is strong agreement", text)
        self.assertIn("graft nothing", text)

    def test_divergence_means_reframe_not_average(self):
        """Averaging two incompatible designs yields something nobody proposed."""
        text = body()
        self.assertIn("Reframe and re-run", text)
        self.assertIn("Do not average the divergence", text)

    def test_grafts_are_folded_by_hand(self):
        text = body()
        self.assertIn("Fold them in by hand", text)
        self.assertIn("Never paste mechanically", text)


class CostDisciplineTests(unittest.TestCase):
    def test_is_gated_to_one_way_doors(self):
        """Arena costs two builds and a judge; most decisions do not warrant it."""
        text = body()
        self.assertIn("Run it only when the cost of choosing wrong is larger", text)
        self.assertIn("Skip it when the choice is reversible", text)

    def test_defaults_to_two_candidates(self):
        self.assertIn("Two, not more", body())

    def test_names_no_model_or_harness_mechanism(self):
        """Seating is the adapter's job, not the skill's."""
        text = body()
        for token in ("@reviewer", "@advisor", "@judge", "modelRoles", "gpt-", "glm-", "grok-"):
            with self.subTest(token=token):
                self.assertNotIn(token, text)

    def test_adapter_seats_three_distinct_families(self):
        text = adapter()
        for role in ("@reviewer", "@advisor", "@judge"):
            with self.subTest(role=role):
                self.assertIn(role, text)
        self.assertIn("Nothing here should touch a per-token provider", text)

    def test_adapter_warns_against_the_parent_family_seat(self):
        """@slow looks like a worker role and silently lands on the caller's family."""
        self.assertIn("Do not seat a candidate on `@slow`", adapter())

    def test_adapter_names_the_same_family_cost(self):
        """A same-family judge confirms the rubric instead of testing the candidates."""
        text = adapter()
        self.assertIn("confirms your framing rather than testing your candidates", text)
        self.assertIn("Disagreement is the strong signal", text)

    def test_adapter_forbids_a_degraded_run_when_quota_runs_out(self):
        """Better to postpone arena than to judge it with a candidate's family."""
        text = adapter()
        self.assertIn("do not", text.lower())
        self.assertIn("Wait for the quota to reset", text)

    def test_adapter_seats_candidates_on_their_own_roles(self):
        """Candidates must not borrow @reviewer or @advisor, which other skills own."""
        text = adapter()
        self.assertIn("@arena-a", text)
        self.assertIn("@arena-b", text)


class ScopeTests(unittest.TestCase):
    def test_states_the_containment_rule(self):
        text = body()
        self.assertIn("## Scope: the project root is the boundary", text)
        self.assertIn("sibling project", text)
        self.assertIn("parent directory", text)

    def test_verifies_the_merged_result(self):
        text = body()
        self.assertIn("Prove the merged artifact works", text)
        self.assertIn("do not paper over it", text)


if __name__ == "__main__":
    unittest.main()
