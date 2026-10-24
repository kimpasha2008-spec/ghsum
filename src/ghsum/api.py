"""Parse repository specs and collect repository data from the GitHub API."""

from __future__ import annotations

import base64
import re
from typing import Any, Callable, Optional

from githubkit import GitHub
from githubkit.exception import RequestFailed

REPO_PATTERNS = [
    # https://github.com/owner/repo(.git)(/anything)
    re.compile(r"^(?:https?://)?(?:www\.)?github\.com/([^/\s]+)/([^/\s#?]+)"),
    # git@github.com:owner/repo(.git)
    re.compile(r"^git@github\.com:([^/\s]+)/([^/\s]+)$"),
    # owner/repo
    re.compile(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$"),
]


def parse_repo(spec: str) -> tuple[str, str]:
    spec = spec.strip().rstrip("/")
    for pat in REPO_PATTERNS:
        m = pat.match(spec)
        if m:
            owner, name = m.group(1), m.group(2)
            if name.endswith(".git"):
                name = name[:-4]
            return owner, name
    raise ValueError(f"can't parse repository: {spec!r} (expected owner/repo or a GitHub URL)")


def optional(call: Callable[[], Any]) -> Optional[Any]:
    """Run an API call; return parsed JSON, or None for 'not available' responses.

    404 = no release / no README, 409 = empty repo, 204 = no content,
    403 on contributors = repo too large for GitHub to compute.
    """
    try:
        resp = call()
    except RequestFailed as e:
        if e.response.status_code in (403, 404, 409, 422):
            return None
        raise
    if resp.status_code == 204 or not resp.content:
        return None
    return resp.json()


def collect(gh: GitHub, owner: str, name: str, n_commits: int, n_contrib: int,
            readme_lines: int) -> dict[str, Any]:
    repos = gh.rest.repos
    # Use raw JSON (resp.json()) rather than parsed models so schema drift
    # in GitHub's OpenAPI spec can't break the CLI.
    repo = repos.get(owner, name).json()

    languages = optional(lambda: repos.list_languages(owner, name)) or {}
    total = sum(languages.values()) or 1
    lang_pct = [
        {"language": k, "percent": round(v * 100 / total, 1)}
        for k, v in sorted(languages.items(), key=lambda kv: kv[1], reverse=True)
    ]

    contributors = optional(
        lambda: repos.list_contributors(owner, name, per_page=n_contrib)
    ) or []
    commits = optional(lambda: repos.list_commits(owner, name, per_page=n_commits)) or []
    release = optional(lambda: repos.get_latest_release(owner, name))
    readme = optional(lambda: repos.get_readme(owner, name))

    readme_excerpt = None
    if readme and readme.get("encoding") == "base64":
        text = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")
        lines = [ln.rstrip() for ln in text.splitlines()]
        # drop leading blank lines, keep the first N
        while lines and not lines[0].strip():
            lines.pop(0)
        readme_excerpt = "\n".join(lines[:readme_lines])

    return {
        "full_name": repo["full_name"],
        "url": repo["html_url"],
        "description": repo.get("description"),
        "homepage": repo.get("homepage") or None,
        "topics": repo.get("topics", []),
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "watchers": repo.get("subscribers_count"),
        "open_issues_and_prs": repo["open_issues_count"],
        "license": (repo.get("license") or {}).get("spdx_id"),
        "default_branch": repo["default_branch"],
        "created_at": repo["created_at"],
        "pushed_at": repo.get("pushed_at"),
        "archived": repo.get("archived", False),
        "fork": repo.get("fork", False),
        "languages": lang_pct,
        "top_contributors": [
            {"login": c.get("login") or c.get("name") or "anonymous",
             "contributions": c["contributions"]}
            for c in contributors[:n_contrib]
        ],
        "recent_commits": [
            {
                "sha": c["sha"][:7],
                "date": (c["commit"].get("author") or {}).get("date"),
                "author": (c.get("author") or {}).get("login")
                or (c["commit"].get("author") or {}).get("name"),
                "message": c["commit"]["message"].splitlines()[0] if c["commit"]["message"] else "",
            }
            for c in commits[:n_commits]
        ],
        "latest_release": None if not release else {
            "tag": release["tag_name"],
            "name": release.get("name"),
            "published_at": release.get("published_at"),
        },
        "readme_excerpt": readme_excerpt,
    }
