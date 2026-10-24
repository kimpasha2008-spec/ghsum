# ghsum

Summarize a GitHub repository from the command line, built on
[githubkit](https://github.com/yanyongyu/githubkit).

```bash
pip install -e .
export GITHUB_TOKEN=ghp_...        # optional; raises rate limit from 60 to 5000 req/h
ghsum psf/requests
ghsum https://github.com/pallets/flask --commits 10 --contributors 8
ghsum owner/repo --json | jq .languages
```

Shows: description, stars/forks/open issues+PRs, license, topics, language
breakdown, top contributors, latest release, recent commits and a README excerpt.

Each run uses 6 API calls. Missing parts (no release, empty repo, no README,
contributor stats too large to compute) are skipped instead of failing.

## Project layout

```
src/ghsum/
  api.py        parse repo specs, fetch data from the GitHub API
  render.py     format the summary as text
  cli.py        argument parsing and entry point
  __main__.py   enables `python -m ghsum`
tests/          unit tests (no network needed)
```

## Development

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
```

## License

MIT, see [LICENSE](LICENSE).
