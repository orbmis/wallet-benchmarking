# Hermes Release Tracker

Hermes is a small, generic competitor release tracker for self-custody wallets.
It is designed to run in any agent harness or cron-like environment: execute one
Python script, keep one JSON state file, and review one Markdown report.

Hermes does not analyze release notes and does not edit the wallet dataset. It
only reports that a new release or release announcement was detected.

## What It Checks

Hermes reads competitors from `hermes/sources.json`. Each competitor can have:

- `github_repos`: GitHub repositories to check for latest releases.
- `x_accounts`: X handles to query through the X API for release announcement tweets.
- `blog_urls`: blog, changelog, release, or announcement pages to watch for release-related updates.

When Hermes detects a new release, it writes a dated Markdown report to:

```text
reports/hermes/YYYY-MM-DD-wallet-releases.md
```

The first run establishes a baseline and normally reports no releases. Later
runs compare against `hermes/state.json`.

## Configuration

Edit `hermes/sources.json` to add or remove competitors:

```json
{
  "id": "example-wallet",
  "name": "Example Wallet",
  "x_accounts": ["ExampleWallet"],
  "blog_urls": ["https://example.com/blog"],
  "github_repos": ["https://github.com/example/wallet"]
}
```

Keep arrays empty when a source type is not available.

## Credentials

X checks require an X API bearer token:

```sh
export X_BEARER_TOKEN="..."
```

GitHub checks work without a token but may hit public rate limits. To increase
rate limits:

```sh
export GITHUB_TOKEN="..."
```

## Run

```sh
python3 hermes/hermes.py
```

Useful options:

```sh
python3 hermes/hermes.py --competitor metamask
python3 hermes/hermes.py --competitor metamask --competitor rabby
python3 hermes/hermes.py --no-state-write
python3 hermes/hermes.py --sources /path/to/sources.json --state /path/to/state.json --reports-dir /path/to/reports
```

## Maintenance

- Add new wallets by editing `hermes/sources.json`; no code change is needed.
- Prefer official release/changelog/blog URLs over general homepages.
- Use exact GitHub repository URLs, not organization URLs.
- Keep X handles without the leading `@`.
- Commit source config changes, but do not commit `hermes/state.json` or generated reports.
