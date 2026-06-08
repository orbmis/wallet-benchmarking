#!/usr/bin/env python3
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

import hermes


def wallet(path: Path, wallet_id: str, urls: dict) -> None:
    path.write_text(
        json.dumps(
            {
                "id": wallet_id,
                "source": "software-wallets",
                "data": {
                    "metadata": {
                        "displayName": wallet_id.title(),
                        "urls": urls,
                    },
                    "features": {},
                },
            }
        )
    )


class HermesTests(unittest.TestCase):
    def test_resolves_software_wallets_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            wallet(data / "metamask.json", "metamask", {"websites": ["https://metamask.io/"]})
            (data / "ledger.json").write_text(json.dumps({"id": "ledger", "source": "hardware-wallets", "data": {}}))
            wallets = hermes.load_software_wallets(data)
            self.assertEqual([w["id"] for w in wallets], ["metamask"])

    def test_unchanged_source_has_no_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "wallets"
            data.mkdir()
            wallet(data / "phantom.json", "phantom", {"websites": ["https://phantom.com/"]})
            state = root / "state.json"
            reports = root / "reports"

            text = "<title>Phantom</title><p>No product update here.</p>"

            def fetch(_url):
                return hermes.FetchResult(True, 200, text, _url)

            hermes.run(data, state, reports, fetcher=fetch, now=dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc))
            report = hermes.run(data, state, reports, fetcher=fetch, now=dt.datetime(2026, 6, 8, tzinfo=dt.timezone.utc))
            body = report.read_text()
            self.assertIn("High-confidence shipped features: 0", body)
            self.assertIn("Roadmap/beta/deprecation updates: 0", body)

    def test_changed_release_creates_shipped_feature(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "wallets"
            data.mkdir()
            wallet(data / "rabby.json", "rabby", {"repositories": ["https://github.com/RabbyHub/Rabby"]})
            state = root / "state.json"
            reports = root / "reports"
            responses = {
                "old": "<title>Releases</title><p>Maintenance update.</p>",
                "new": "<title>Releases</title><p>Released new passkey recovery and bridge security feature.</p>",
            }

            current = {"body": responses["old"]}

            def fetch(_url):
                return hermes.FetchResult(True, 200, current["body"], _url)

            hermes.run(data, state, reports, fetcher=fetch, now=dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc))
            current["body"] = responses["new"]
            report = hermes.run(data, state, reports, fetcher=fetch, now=dt.datetime(2026, 6, 8, tzinfo=dt.timezone.utc))
            body = report.read_text()
            self.assertIn("High-confidence shipped features: 1", body)
            self.assertIn("Released new passkey recovery", body)

    def test_roadmap_and_social_classification(self):
        official = hermes.Source("safe", "Safe", "https://safe.global/roadmap", "official", "site")
        social = hermes.Source("safe", "Safe", "https://x.com/safe", "social", "x")
        previous = {"hash": "old"}
        current = {"hash": "new", "title": "Safe"}
        roadmap = hermes.classify_change(
            official,
            previous,
            current,
            "Coming soon: beta support for gas sponsorship and passkey recovery.",
        )
        weak = hermes.classify_change(
            social,
            previous,
            current,
            "We are launching new staking support next week.",
        )
        self.assertEqual(roadmap["classification"], "Roadmap update")
        self.assertEqual(weak["classification"], "Weak signal")


if __name__ == "__main__":
    unittest.main()
