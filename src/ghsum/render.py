"""Format a repository summary as plain text."""

from __future__ import annotations

from typing import Any


def render(s: dict[str, Any]) -> str:
    out: list[str] = []
    title = s["full_name"]
    flags = [f for f, on in (("archived", s["archived"]), ("fork", s["fork"])) if on]
    if flags:
        title += f"  [{', '.join(flags)}]"
    out += [title, "=" * len(title)]
    if s["description"]:
        out.append(s["description"])
    out.append(s["url"])
    if s["homepage"]:
        out.append(f"Homepage: {s['homepage']}")
    out.append("")
    out.append(
        f"★ {s['stars']:,}   forks {s['forks']:,}   "
        f"open issues+PRs {s['open_issues_and_prs']:,}   "
        f"license {s['license'] or 'none'}"
    )
    out.append(
        f"Created {s['created_at'][:10]}   last push {(s['pushed_at'] or '?')[:10]}   "
        f"default branch {s['default_branch']}"
    )
    if s["topics"]:
        out.append("Topics: " + ", ".join(s["topics"]))

    if s["languages"]:
        out += ["", "Languages"]
        for lang in s["languages"][:8]:
            bar = "█" * max(1, int(lang["percent"] / 5))
            out.append(f"  {lang['language']:<16} {lang['percent']:>5.1f}%  {bar}")

    if s["top_contributors"]:
        out += ["", "Top contributors"]
        for c in s["top_contributors"]:
            out.append(f"  {c['login']:<24} {c['contributions']:>6,} commits")

    if s["latest_release"]:
        r = s["latest_release"]
        out += ["", f"Latest release: {r['tag']}"
                + (f" ({r['name']})" if r["name"] and r["name"] != r["tag"] else "")
                + (f", {r['published_at'][:10]}" if r["published_at"] else "")]

    if s["recent_commits"]:
        out += ["", "Recent commits"]
        for c in s["recent_commits"]:
            date = (c["date"] or "")[:10]
            msg = c["message"] if len(c["message"]) <= 72 else c["message"][:69] + "..."
            out.append(f"  {c['sha']}  {date}  {c['author'] or '?':<16.16}  {msg}")

    if s["readme_excerpt"]:
        out += ["", "README (excerpt)", "-" * 16, s["readme_excerpt"]]

    return "\n".join(out)
