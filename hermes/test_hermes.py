#!/usr/bin/env python3
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import hermes


def write_sources(path: Path, competitors: list[dict]) -> None:
    path.write_text(json.dumps({"competitors": competitors}))


def competitor(**overrides) -> dict:
    base = {
        "id": "metamask",
        "name": "MetaMask",
        "github_repos": [],
        "x_accounts": [],
        "blog_urls": [],
    }
    base.update(overrides)
    return base


class HermesReleaseTrackerTests(unittest.TestCase):
    def test_load_sources_requires_expected_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sources.json"
            write_sources(path, [competitor(id="rabby", name="Rabby")])
            sources = hermes.load_sources(path)
            self.assertEqual(sources[0]["id"], "rabby")

    def test_github_release_reports_only_after_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources.json"
            state = root / "state.json"
            reports = root / "reports"
            write_sources(
                sources,
                [
                    competitor(
                        id="rabby",
                        name="Rabby",
                        github_repos=["https://github.com/RabbyHub/Rabby"],
                    )
                ],
            )
            latest = {"id": "1", "title": "v1", "url": "https://github.com/RabbyHub/Rabby/releases/tag/v1", "published_at": "2026-06-01T00:00:00Z", "source": "https://github.com/RabbyHub/Rabby"}

            with patch("hermes.github_latest_release", return_value=latest):
                first = hermes.run(sources, state, reports, now=dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc))
            self.assertIn("New releases detected: 0", first.read_text())

            latest2 = dict(latest, id="2", title="v2", url="https://github.com/RabbyHub/Rabby/releases/tag/v2")
            with patch("hermes.github_latest_release", return_value=latest2):
                second = hermes.run(sources, state, reports, now=dt.datetime(2026, 6, 8, tzinfo=dt.timezone.utc))
            body = second.read_text()
            self.assertIn("New releases detected: 1", body)
            self.assertIn("v2", body)

    def test_x_release_tweet_requires_token_and_reports_new_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources.json"
            state = root / "state.json"
            reports = root / "reports"
            write_sources(sources, [competitor(x_accounts=["MetaMask"])])

            with patch.dict("os.environ", {}, clear=True):
                report = hermes.run(sources, state, reports, now=dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc))
            self.assertIn("X_BEARER_TOKEN is not set", report.read_text())

            with patch.dict("os.environ", {"X_BEARER_TOKEN": "token"}, clear=True), patch(
                "hermes.x_recent_release_tweets",
                return_value=([], "10"),
            ):
                hermes.run(sources, state, reports, now=dt.datetime(2026, 6, 2, tzinfo=dt.timezone.utc))

            tweet = {
                "id": "11",
                "title": "Released wallet notifications",
                "url": "https://x.com/MetaMask/status/11",
                "published_at": "2026-06-08T00:00:00Z",
                "source": "https://x.com/MetaMask",
            }
            with patch.dict("os.environ", {"X_BEARER_TOKEN": "token"}, clear=True), patch(
                "hermes.x_recent_release_tweets",
                return_value=([tweet], "11"),
            ):
                report = hermes.run(sources, state, reports, now=dt.datetime(2026, 6, 8, tzinfo=dt.timezone.utc))
            self.assertIn("X announcement", report.read_text())
            self.assertIn("Released wallet notifications", report.read_text())

    def test_blog_change_with_release_signal_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources.json"
            state = root / "state.json"
            reports = root / "reports"
            write_sources(sources, [competitor(blog_urls=["https://metamask.io/news/"])])
            current = {"text": "<title>News</title><p>Old page</p>"}

            def fetch(url):
                return hermes.FetchResult(True, 200, current["text"], url)

            hermes.run(sources, state, reports, fetcher=fetch, now=dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc))
            current["text"] = "<title>News</title><p>Released new wallet notifications today.</p>"
            report = hermes.run(sources, state, reports, fetcher=fetch, now=dt.datetime(2026, 6, 8, tzinfo=dt.timezone.utc))
            self.assertIn("Blog/release page", report.read_text())


if __name__ == "__main__":
    unittest.main()
