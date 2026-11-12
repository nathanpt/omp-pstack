"""Behaviour tests: things the suite actually executes, not just reads.

Every other test in this repo asserts that a file says the right thing. That is
worth having, but it cannot catch a skill whose prose is correct and whose
effects are wrong. The interrogate run of 2026-11-11 passed fifteen prose tests
while scattering 1.1 GB of copies across a projects directory. Nothing executed.

These tests run something and check what happened.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "install.sh"
SKILLS = REPO / "skills"


def run(args, cwd=None):
    return subprocess.run(
        ["bash", str(INSTALL), *args],
        capture_output=True,
        text=True,
        cwd=cwd or REPO,
        timeout=120,
    )


class InstallScriptBehaviourTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omp-pstack-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def targets(self):
        return sorted(p.name for p in self.tmp.iterdir())

    def test_links_every_shipped_skill_at_depth_one(self):
        proc = run([str(self.tmp)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        expected = sorted(p.name for p in SKILLS.iterdir() if p.is_dir())
        self.assertEqual(self.targets(), expected)
        for name in expected:
            link = self.tmp / name
            self.assertTrue(link.is_symlink(), f"{name} is not a symlink")
            self.assertTrue((link / "SKILL.md").is_file(), f"{name}/SKILL.md unreadable")

    def test_refuses_to_clobber_a_real_directory(self):
        squatter = self.tmp / "interrogate"
        squatter.mkdir()
        (squatter / "SKILL.md").write_text("not ours")
        proc = run([str(self.tmp)])
        self.assertEqual(proc.returncode, 1, "expected a non-zero exit on collision")
        self.assertIn("REFUSED", proc.stderr)
        self.assertEqual((squatter / "SKILL.md").read_text(), "not ours")

    def test_prunes_a_stale_link_into_this_repo(self):
        """A renamed or deleted skill must not leave a dangling link behind."""
        stale = self.tmp / "retired-skill"
        stale.symlink_to(REPO / "skills" / "retired-skill")
        proc = run([str(self.tmp)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(stale.exists() or stale.is_symlink(), "stale link survived")
        self.assertIn("pruned stale link", proc.stdout)

    def test_leaves_a_neighbouring_library_alone(self):
        """Pruning must not reach outside this repo's own skill paths."""
        foreign = self.tmp / "someone-elses-skill"
        foreign.symlink_to(Path("/nonexistent/elsewhere/skill"))
        run([str(self.tmp)])
        self.assertTrue(foreign.is_symlink(), "pruned a link it does not own")

    def test_uninstall_removes_only_this_repos_links(self):
        run([str(self.tmp)])
        foreign = self.tmp / "someone-elses-skill"
        foreign.symlink_to(Path("/nonexistent/elsewhere/skill"))
        proc = run(["--uninstall", str(self.tmp)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(foreign.is_symlink(), "uninstall removed a foreign link")
        for name in (p.name for p in SKILLS.iterdir() if p.is_dir()):
            self.assertFalse((self.tmp / name).exists(), f"{name} survived uninstall")

    def test_is_idempotent(self):
        run([str(self.tmp)])
        first = self.targets()
        proc = run([str(self.tmp)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.targets(), first)


class RepoShapeTests(unittest.TestCase):
    def test_every_shipped_skill_has_parseable_frontmatter(self):
        """A skill with no frontmatter never registers, and nothing else notices."""
        for skill in sorted(SKILLS.glob("*/SKILL.md")):
            text = skill.read_text()
            with self.subTest(skill=skill.parent.name):
                self.assertTrue(text.startswith("---\n"), "no frontmatter block")
                head = text.split("---", 2)[1]
                self.assertIn("name:", head)
                self.assertIn("description:", head)

    def test_every_repo_reference_is_linked_from_a_skill_or_the_readme(self):
        """An orphan reference nobody opens is dead weight."""
        readers = [p.read_text() for p in SKILLS.glob("*/SKILL.md")]
        readers.append((REPO / "README.md").read_text())
        blob = "\n".join(readers)
        for ref in sorted((REPO / "references").glob("*.md")):
            with self.subTest(ref=ref.name):
                self.assertIn(ref.name, blob, f"{ref.name} is not linked from anywhere")

    def test_isolation_rules_are_stated_once(self):
        """Location, cost, teardown, and credential containment live in one file."""
        iso = (REPO / "references" / "isolation.md").read_text()
        for topic in ("disk-backed", "What it costs", "Teardown", "Secrets travel with the copy"):
            with self.subTest(topic=topic):
                self.assertIn(topic, iso)
        for skill in ("interrogate", "arena"):
            body = (SKILLS / skill / "SKILL.md").read_text()
            with self.subTest(skill=skill):
                self.assertIn("references/isolation.md", body)


if __name__ == "__main__":
    unittest.main()
