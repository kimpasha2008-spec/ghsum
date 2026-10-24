import unittest

from ghsum.render import render

SAMPLE = {
    "full_name": "octo/demo",
    "url": "https://github.com/octo/demo",
    "description": "A demo repo",
    "homepage": None,
    "topics": ["cli", "github"],
    "stars": 1234,
    "forks": 56,
    "watchers": 7,
    "open_issues_and_prs": 8,
    "license": "MIT",
    "default_branch": "main",
    "created_at": "2020-01-02T00:00:00Z",
    "pushed_at": "2026-10-01T00:00:00Z",
    "archived": True,
    "fork": False,
    "languages": [{"language": "Python", "percent": 90.0}, {"language": "Shell", "percent": 10.0}],
    "top_contributors": [{"login": "alice", "contributions": 1500}],
    "recent_commits": [
        {"sha": "abc1234", "date": "2026-10-01T00:00:00Z", "author": "alice", "message": "x" * 100},
    ],
    "latest_release": {"tag": "v1.0", "name": "First", "published_at": "2026-09-01T00:00:00Z"},
    "readme_excerpt": "# demo",
}


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.text = render(SAMPLE)

    def test_title_and_flags(self):
        self.assertTrue(self.text.startswith("octo/demo  [archived]\n"))

    def test_counts_formatted(self):
        self.assertIn("★ 1,234", self.text)
        self.assertIn("license MIT", self.text)

    def test_sections(self):
        for heading in ("Languages", "Top contributors", "Recent commits", "README (excerpt)"):
            self.assertIn(heading, self.text)
        self.assertIn("Latest release: v1.0 (First), 2026-09-01", self.text)

    def test_long_commit_message_truncated(self):
        self.assertIn("x" * 69 + "...", self.text)
        self.assertNotIn("x" * 70, self.text)

    def test_minimal_summary(self):
        minimal = dict(SAMPLE, description=None, topics=[], languages=[], top_contributors=[],
                       recent_commits=[], latest_release=None, readme_excerpt=None,
                       archived=False, pushed_at=None)
        text = render(minimal)
        self.assertTrue(text.startswith("octo/demo\n"))
        self.assertIn("last push ?", text)


if __name__ == "__main__":
    unittest.main()
