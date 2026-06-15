#!/usr/bin/env python3
"""Report newly detected self-custody wallet competitor releases.

Hermes is deliberately harness-agnostic: it reads a JSON source file, checks
GitHub releases, X accounts, and blog/release pages, stores lightweight state,
and writes a Markdown report. It does not mutate the wallet dataset.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = ROOT / "hermes" / "sources.json"
DEFAULT_STATE = ROOT / "hermes" / "state.json"
DEFAULT_REPORTS_DIR = ROOT / "reports" / "hermes"

USER_AGENT = "HermesWalletReleaseTracker/1.0"
RELEASE_TERMS = (
    "release",
    "released",
    "launch",
    "launched",
    "shipping",
    "shipped",
    "now live",
    "now available",
    "introducing",
    "announcement",
    "announcing",
    "version",
    "changelog",
)


@dataclass(frozen=True)
class FetchResult:
    ok: bool
    status: int | None
    text: str
    final_url: str
    error: str | None = None


def load_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_sources(path: Path) -> list[dict]:
    payload = load_json(path)
    competitors = payload.get("competitors", [])
    if not isinstance(competitors, list):
        raise ValueError("sources file must contain a competitors array")
    for competitor in competitors:
        for key in ("id", "name", "github_repos", "x_accounts", "blog_urls"):
            if key not in competitor:
                raise ValueError(f"competitor entry missing {key}: {competitor}")
    return competitors


def request_json(url: str, headers: dict[str, str] | None = None, timeout: int = 20) -> dict:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    req_headers.update(headers or {})
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        text = response.read(2_000_000).decode("utf-8", errors="replace")
        return json.loads(text)


def fetch_url(url: str, timeout: int = 20) -> FetchResult:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(2_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return FetchResult(True, response.status, raw.decode(charset, errors="replace"), response.geturl())
    except urllib.error.HTTPError as exc:
        return FetchResult(False, exc.code, exc.read(50_000).decode("utf-8", errors="replace"), url, f"HTTP {exc.code}")
    except Exception as exc:
        return FetchResult(False, None, "", url, str(exc))


def github_repo_slug(repo_url: str) -> str | None:
    match = re.match(r"https://github\.com/([^/]+)/([^/#?]+)", repo_url.rstrip("/"))
    if not match:
        return None
    owner, repo = match.groups()
    if repo in ("releases", "tags"):
        return None
    return f"{owner}/{repo}"


def github_latest_release(repo_url: str, token: str | None = None) -> dict | None:
    slug = github_repo_slug(repo_url)
    if not slug:
        return None
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        release = request_json(f"https://api.github.com/repos/{slug}/releases/latest", headers=headers)
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        releases = request_json(f"https://api.github.com/repos/{slug}/releases?per_page=1", headers=headers)
        release = releases[0] if releases else None
    if not release:
        return None
    return {
        "id": str(release.get("id") or release.get("tag_name")),
        "title": release.get("name") or release.get("tag_name") or slug,
        "url": release.get("html_url") or repo_url.rstrip("/") + "/releases",
        "published_at": release.get("published_at") or release.get("created_at"),
        "source": repo_url,
    }


def x_request(path: str, bearer_token: str, params: dict[str, str] | None = None) -> dict:
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    return request_json(
        f"https://api.x.com/2{path}{qs}",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )


def x_user_id(handle: str, bearer_token: str) -> str:
    user = x_request(f"/users/by/username/{handle.lstrip('@')}", bearer_token)
    return user["data"]["id"]


def x_recent_release_tweets(handle: str, bearer_token: str, since_id: str | None = None) -> tuple[list[dict], str | None]:
    user_id = x_user_id(handle, bearer_token)
    params = {
        "max_results": "10",
        "tweet.fields": "created_at",
        "exclude": "replies,retweets",
    }
    if since_id:
        params["since_id"] = since_id
    payload = x_request(f"/users/{user_id}/tweets", bearer_token, params=params)
    tweets = payload.get("data", []) or []
    newest_id = tweets[0]["id"] if tweets else since_id
    release_tweets = []
    for tweet in tweets:
        text = tweet.get("text", "")
        if contains_release_signal(text):
            release_tweets.append(
                {
                    "id": tweet["id"],
                    "title": first_line(text),
                    "url": f"https://x.com/{handle.lstrip('@')}/status/{tweet['id']}",
                    "published_at": tweet.get("created_at"),
                    "source": f"https://x.com/{handle.lstrip('@')}",
                }
            )
    return release_tweets, newest_id


def clean_text(text: str) -> str:
    text = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def page_title(raw: str, fallback_url: str) -> str:
    match = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
    if match:
        title = clean_text(match.group(1))
        if title:
            return title[:180]
    return fallback_url


def content_hash(text: str) -> str:
    return hashlib.sha256(clean_text(text).encode("utf-8")).hexdigest()


def contains_release_signal(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in RELEASE_TERMS)


def first_line(text: str, limit: int = 180) -> str:
    line = clean_text(text).split(". ")[0]
    return line[:limit] + ("..." if len(line) > limit else "")


def check_github(competitor: dict, state: dict, github_token: str | None, failures: list[dict]) -> list[dict]:
    events = []
    for repo in competitor["github_repos"]:
        key = f"github:{competitor['id']}:{repo}"
        try:
            latest = github_latest_release(repo, github_token)
        except Exception as exc:
            failures.append({"competitor": competitor["name"], "source": repo, "type": "github", "error": str(exc)})
            continue
        if not latest:
            failures.append({"competitor": competitor["name"], "source": repo, "type": "github", "error": "no GitHub releases found"})
            continue
        previous = state["sources"].get(key, {})
        if previous and previous.get("latest_release_id") != latest["id"]:
            events.append(event(competitor, "GitHub release", latest["title"], latest["url"], latest.get("published_at"), repo))
        state["sources"][key] = {"latest_release_id": latest["id"], "checked_at": checked_at(), **latest}
    return events


def check_x(competitor: dict, state: dict, bearer_token: str | None, failures: list[dict]) -> list[dict]:
    if not competitor["x_accounts"]:
        return []
    if not bearer_token:
        for handle in competitor["x_accounts"]:
            failures.append({"competitor": competitor["name"], "source": f"https://x.com/{handle}", "type": "x", "error": "X_BEARER_TOKEN is not set"})
        return []

    events = []
    for handle in competitor["x_accounts"]:
        key = f"x:{competitor['id']}:{handle.lstrip('@')}"
        previous = state["sources"].get(key, {})
        since_id = previous.get("latest_tweet_id")
        try:
            tweets, newest_id = x_recent_release_tweets(handle, bearer_token, since_id)
        except Exception as exc:
            failures.append({"competitor": competitor["name"], "source": f"https://x.com/{handle}", "type": "x", "error": str(exc)})
            continue
        if previous:
            for tweet in reversed(tweets):
                events.append(event(competitor, "X announcement", tweet["title"], tweet["url"], tweet.get("published_at"), tweet["source"]))
        if newest_id:
            state["sources"][key] = {"latest_tweet_id": newest_id, "checked_at": checked_at(), "source": f"https://x.com/{handle}"}
    return events


def check_blogs(competitor: dict, state: dict, fetcher: Callable[[str], FetchResult], failures: list[dict]) -> list[dict]:
    events = []
    for url in competitor["blog_urls"]:
        key = f"blog:{competitor['id']}:{url}"
        result = fetcher(url)
        if not result.ok:
            failures.append({"competitor": competitor["name"], "source": url, "type": "blog", "error": result.error or f"HTTP {result.status}"})
            continue
        digest = content_hash(result.text)
        title = page_title(result.text, result.final_url)
        previous = state["sources"].get(key, {})
        if previous and previous.get("hash") != digest and contains_release_signal(clean_text(result.text)):
            events.append(event(competitor, "Blog/release page", title, result.final_url, None, url))
        state["sources"][key] = {"hash": digest, "title": title, "checked_at": checked_at(), "source": url, "final_url": result.final_url}
    return events


def event(competitor: dict, source_type: str, title: str, url: str, published_at: str | None, source: str) -> dict:
    return {
        "competitor_id": competitor["id"],
        "competitor": competitor["name"],
        "source_type": source_type,
        "title": title,
        "url": url,
        "published_at": published_at,
        "source": source,
    }


def checked_at() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def run(
    sources_path: Path = DEFAULT_SOURCES,
    state_path: Path = DEFAULT_STATE,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    competitor_filter: set[str] | None = None,
    fetcher: Callable[[str], FetchResult] = fetch_url,
    now: dt.datetime | None = None,
    write_state: bool = True,
) -> Path:
    now = now or dt.datetime.now(dt.timezone.utc).astimezone()
    competitors = load_sources(sources_path)
    if competitor_filter:
        competitors = [c for c in competitors if c["id"] in competitor_filter]

    state = load_json(state_path, {"version": 1, "sources": {}})
    state.setdefault("sources", {})
    github_token = os.environ.get("GITHUB_TOKEN")
    x_bearer_token = os.environ.get("X_BEARER_TOKEN")

    releases: list[dict] = []
    failures: list[dict] = []
    for competitor in competitors:
        releases.extend(check_github(competitor, state, github_token, failures))
        releases.extend(check_x(competitor, state, x_bearer_token, failures))
        releases.extend(check_blogs(competitor, state, fetcher, failures))

    state["last_run_at"] = now.isoformat(timespec="seconds")
    state["competitor_count"] = len(competitors)
    if write_state:
        save_json(state_path, state)

    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{now.date().isoformat()}-wallet-releases.md"
    report_path.write_text(render_report(now, competitors, releases, failures))
    return report_path


def render_report(now: dt.datetime, competitors: list[dict], releases: list[dict], failures: list[dict]) -> str:
    lines = [
        f"# Self-Custody Wallet Competitor Releases - {now.date().isoformat()}",
        "",
        "## Summary",
        "",
        f"- Competitors checked: {len(competitors)}",
        f"- New releases detected: {len(releases)}",
        f"- Source check failures: {len(failures)}",
        "",
        "## New Releases",
        "",
    ]
    if not releases:
        lines += ["None detected.", ""]
    else:
        for item in sorted(releases, key=lambda r: (r["competitor"].lower(), r["source_type"], r["title"].lower())):
            date = f" ({item['published_at']})" if item.get("published_at") else ""
            lines += [
                f"### {item['competitor']}",
                "",
                f"- Type: {item['source_type']}",
                f"- Release: [{item['title']}]({item['url']}){date}",
                f"- Source monitored: {item['source']}",
                "",
            ]

    lines += ["## Source Check Failures", ""]
    if not failures:
        lines += ["None.", ""]
    else:
        for failure in failures:
            lines.append(f"- {failure['competitor']} `{failure['type']}` [{failure['source']}]({failure['source']}): {failure['error']}")
        lines.append("")

    lines += [
        "## Notes",
        "",
        "- First run establishes a baseline and normally reports no releases.",
        "- Hermes records releases only; it does not summarize or analyze release notes.",
        "- X checks require `X_BEARER_TOKEN`; GitHub checks can use optional `GITHUB_TOKEN` for higher rate limits.",
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect and report competitor wallet releases.")
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES, help="Path to competitor source config JSON.")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="Path to local state JSON.")
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR, help="Directory for Markdown reports.")
    parser.add_argument("--competitor", action="append", help="Competitor id to check. May be repeated.")
    parser.add_argument("--no-state-write", action="store_true", help="Write a report without updating state.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = run(
        sources_path=args.sources,
        state_path=args.state,
        reports_dir=args.reports_dir,
        competitor_filter=set(args.competitor) if args.competitor else None,
        write_state=not args.no_state_write,
    )
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
