"""Portability tests: a skill body that names a harness is a skill that only runs there."""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"

# Mechanisms that belong in references/harness-<name>.md, never in a skill body.
BANNED_IN_BODY = (
    "agent://",
    "history://",
    "isolated:",
    "subagent_type",
    "run_in_background",
    "@smol",
    "@slow",
    "@task",
    "@plan",
    "modelRoles",
    "disable-model-invocation",
    "AskQuestion",
    "/loop",
    ".cursor/",
    ".omp/",
    "~/.omp",
    "~/.cursor",
    "Bugbot",
    "/poteto-mode",
    "grok-",
    "claude-opus",
    "claude-sonnet",
    "gpt-4",
    "gpt-5",
    "Task tool",
    "subagent",
)

# Frontmatter keys that are portable. A harness-specific key makes the shipped
# file work on exactly one harness.
ALLOWED_FRONTMATTER = {"name", "description", "version", "license"}

DESCRIPTION_LIMIT = 1024


def skill_files():
    return sorted(SKILLS.glob("*/SKILL.md"))


def split_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw, body = parts[1], parts[2]
    meta = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, body


class BodyStaysPortableTests(unittest.TestCase):
    def test_skill_files_exist(self):
        self.assertGreaterEqual(len(skill_files()), 2, "expected at least two adopted skills")

    def test_body_names_no_harness_mechanism(self):
        for path in skill_files():
            _, body = split_frontmatter(path.read_text())
            for token in BANNED_IN_BODY:
                with self.subTest(skill=path.parent.name, token=token):
                    self.assertNotIn(
                        token,
                        body,
                        f"{path.parent.name}/SKILL.md names {token!r}; put it in "
                        f"references/harness-*.md and use a contract verb instead",
                    )

    def test_body_invokes_no_harness_command(self):
        """A literal shell command in a skill body is a harness assumption."""
        for path in skill_files():
            _, body = split_frontmatter(path.read_text())
            for match in re.finditer(r"^\s*```(bash|sh|shell|zsh)", body, re.M):
                self.fail(f"{path.parent.name}/SKILL.md contains a shell block at offset "
                          f"{match.start()}; commands belong in the adapter or the project")

    def test_frontmatter_is_portable_only(self):
        for path in skill_files():
            meta, _ = split_frontmatter(path.read_text())
            extra = set(meta) - ALLOWED_FRONTMATTER
            with self.subTest(skill=path.parent.name):
                self.assertEqual(
                    extra, set(),
                    f"{path.parent.name} frontmatter has non-portable keys {sorted(extra)}; "
                    "harness-specific keys belong in the install step, not the shipped file",
                )

    def test_description_is_a_trigger_and_fits(self):
        for path in skill_files():
            meta, _ = split_frontmatter(path.read_text())
            desc = meta.get("description", "")
            with self.subTest(skill=path.parent.name):
                self.assertTrue(desc, "description is required")
                self.assertLessEqual(len(desc), DESCRIPTION_LIMIT)
                self.assertTrue(
                    desc.startswith("Use when"),
                    "description must open with a self-contained trigger phrase",
                )

    def test_frontmatter_name_matches_directory(self):
        for path in skill_files():
            meta, _ = split_frontmatter(path.read_text())
            with self.subTest(skill=path.parent.name):
                self.assertEqual(meta.get("name"), path.parent.name)


if __name__ == "__main__":
    unittest.main()
