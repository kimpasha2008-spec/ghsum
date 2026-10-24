"""Command-line entry point.

Usage:
    ghsum owner/repo
    ghsum https://github.com/owner/repo --commits 10 --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from githubkit import GitHub
from githubkit.exception import RequestFailed

from ghsum import __version__
from ghsum.api import collect, parse_repo
from ghsum.render import render


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="ghsum", description="Summarize a GitHub repository.")
    p.add_argument("repo", help="owner/repo or a GitHub URL")
    p.add_argument("--token", help="GitHub token (default: $GITHUB_TOKEN or $GH_TOKEN)")
    p.add_argument("--commits", type=int, default=5, help="recent commits to show (default 5)")
    p.add_argument("--contributors", type=int, default=5, help="top contributors (default 5)")
    p.add_argument("--readme-lines", type=int, default=15, help="README lines to show (default 15)")
    p.add_argument("--json", action="store_true", help="output JSON")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = p.parse_args(argv)

    try:
        owner, name = parse_repo(args.repo)
    except ValueError as e:
        p.error(str(e))

    clamp = lambda n: max(0, min(n, 100))  # GitHub caps per_page at 100
    token = args.token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    gh = GitHub(token) if token else GitHub()

    try:
        summary = collect(gh, owner, name, clamp(args.commits), clamp(args.contributors),
                          max(0, args.readme_lines))
    except RequestFailed as e:
        code = e.response.status_code
        if code == 404:
            msg = f"repository {owner}/{name} not found (or private and no token given)"
        elif code in (401,):
            msg = "authentication failed: check your token"
        elif code in (403, 429):
            msg = "GitHub API rate limit hit or access denied; set GITHUB_TOKEN to raise the limit"
        else:
            msg = f"GitHub API error {code}"
        print(f"ghsum: {msg}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(render(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
