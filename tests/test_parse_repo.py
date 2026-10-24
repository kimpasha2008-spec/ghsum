import unittest

from ghsum.api import parse_repo


class ParseRepoTests(unittest.TestCase):
    def test_owner_slash_repo(self):
        self.assertEqual(parse_repo("psf/requests"), ("psf", "requests"))

    def test_https_url_with_path_and_trailing_slash(self):
        self.assertEqual(parse_repo("https://github.com/pallets/flask/tree/main/"),
                         ("pallets", "flask"))

    def test_url_without_scheme(self):
        self.assertEqual(parse_repo("github.com/pallets/flask"), ("pallets", "flask"))

    def test_dot_git_suffix(self):
        self.assertEqual(parse_repo("https://github.com/psf/requests.git"), ("psf", "requests"))

    def test_ssh_remote(self):
        self.assertEqual(parse_repo("git@github.com:psf/requests.git"), ("psf", "requests"))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            parse_repo("not a repo")


if __name__ == "__main__":
    unittest.main()
