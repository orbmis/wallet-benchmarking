#!/usr/bin/env python3
"""Weekly competitor tracker for software wallet product changes.

Hermes is intentionally small: it reads wallet metadata from data/wallets/*.json,
checks official URLs, compares source snapshots with local state, and writes a
dated Markdown report. It never edits wallet data.
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
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "wallets"
DEFAULT_STATE = ROOT / "hermes" / "state.json"
DEFAULT_REPORTS = ROOT / "reports" / "hermes"

USER_AGENT = "HermesWalletTracker/1.0 (+https://github.com; report-only)"

SHIPPED_TERMS = [
    "launch",
    "launched",
    "released",
    "release",
    "new",
    "now available",
    "available now",
    "ships",
    "shipped",
    "introducing",
    "added",
    "supports",
    "support for",
]
ROADMAP_TERMS = [
    "roadmap",
    "coming soon",
    "planned",
    "plan to",
    "beta",
    "waitlist",
    "preview",
    "deprecated",
    "deprecation",
    "sunset",
    "will support",
    "coming",
]
FEATURE_TERMS = [
    "staking",
    "passkey",
    "gas",
    "bridge",
    "bridging",
    "nft",
    "security",
    "recovery",
    "chain",
    "network",
    "walletconnect",
    "swap",
    "fiat",
    "on-ramp",
    "off-ramp",
    "notification",
    "dapp",
    "defi",
    "portfolio",
]


@dataclass(frozen=True)
class Source:
    wallet_id: str
    wallet_name: str
    url: str
    kind: str
    label: str


@dataclass(frozen=True)
class FetchResult:
    ok: bool
    status: int | None
    text: str
    final_url: str
    error: str | None = None


def load_software_wallets(data_dir: Path = DEFAULT_DATA_DIR) -> list[dict]:
    wallets = []
    for path in sorted(data_dir.glob("*.json")):
        data = json.loads(path.read_text())
        if data.get("source") == "software-wallets":
            wallets.append(data)
    return wallets


def wallet_name(wallet: dict) -> str:
    meta = wallet.get("data", {}).get("metadata", {})
    return meta.get("displayName") or meta.get("tableName") or wallet["id"]


def iter_urls(node) -> Iterable[str]:
    if isinstance(node, str):
        if node.startswith(("http://", "https://")):
            yield node
    elif isinstance(node, list):
        for item in node:
            yield from iter_urls(item)
    elif isinstance(node, dict):
        if "url" in node:
            yield from iter_urls(node["url"])
        for value in node.values():
            yield from iter_urls(value)


def source_kind(category: str, url: str) -> str:
    host = re.sub(r"^https?://", "", url).split("/", 1)[0].lower()
    if category == "socials" or any(h in host for h in ("x.com", "twitter.com", "farcaster.xyz", "discord.com", "t.me", "reddit.com", "youtube.com")):
        return "social"
    if "github.com" in host:
        return "github"
    if "chromewebstore.google.com" in host or "apps.apple.com" in host or "play.google.com" in host:
        return "app-listing"
    if any(word in url.lower() for word in ("release", "changelog", "version")):
        return "release"
    if any(word in host for word in ("support.", "help.", "docs.")) or "/docs" in url.lower():
        return "docs"
    return "official"


def resolve_sources(wallets: list[dict]) -> list[Source]:
    out: list[Source] = []
    seen: set[tuple[str, str]] = set()
    for wallet in wallets:
        wid = wallet["id"]
        name = wallet_name(wallet)
        meta_urls = wallet.get("data", {}).get("metadata", {}).get("urls", {})
        for category, value in meta_urls.items():
            if isinstance(value, dict):
                pairs = value.items()
            else:
                pairs = [(category, value)]
            for label, nested in pairs:
                for url in iter_urls(nested):
                    key = (wid, url)
                    if key not in seen:
                        seen.add(key)
                        out.append(Source(wid, name, url, source_kind(category, url), str(label)))
                    if "github.com" in url and re.match(r"https://github\.com/[^/]+/[^/]+/?$", url.rstrip("/")):
                        releases = url.rstrip("/") + "/releases"
                        rkey = (wid, releases)
                        if rkey not in seen:
                            seen.add(rkey)
                            out.append(Source(wid, name, releases, "release", "github-releases"))

        feature_tree = wallet.get("data", {}).get("features", {})
        for url in iter_urls(
            {
                "releaseVelocity": feature_tree.get("product", {}).get("releaseVelocity"),
                "releaseTransparency": feature_tree.get("releaseTransparency"),
            }
        ):
            key = (wid, url)
            if key not in seen:
                seen.add(key)
                out.append(Source(wid, name, url, source_kind("release", url), "feature-citation"))
    return out


def fetch_url(url: str, timeout: int = 20) -> FetchResult:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/json,text/plain;q=0.9,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(2_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(charset, errors="replace")
            return FetchResult(True, response.status, text, response.geturl())
    except urllib.error.HTTPError as exc:
        body = exc.read(50_000).decode("utf-8", errors="replace")
        return FetchResult(False, exc.code, body, url, f"HTTP {exc.code}")
    except Exception as exc:  # network, TLS, timeout, robots, dynamic blocks
        return FetchResult(False, None, "", url, str(exc))


def clean_text(text: str) -> str:
    text = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def page_title(raw: str, cleaned: str) -> str | None:
    match = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
    if match:
        return clean_text(match.group(1))[:140]
    return cleaned[:100] if cleaned else None


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def snippets(text: str, terms: list[str], window: int = 180, limit: int = 3) -> list[str]:
    low = text.lower()
    hits = []
    for term in terms:
        start = 0
        while len(hits) < limit:
            idx = low.find(term.lower(), start)
            if idx == -1:
                break
            lo = max(0, idx - window)
            hi = min(len(text), idx + len(term) + window)
            snippet = text[lo:hi].strip()
            if snippet and snippet not in hits:
                hits.append(snippet)
            start = idx + len(term)
        if len(hits) >= limit:
            break
    return hits


def classify_change(source: Source, previous: dict | None, current: dict, text: str) -> dict | None:
    if previous is None:
        return None
    if previous.get("hash") == current["hash"]:
        return None

    social = source.kind == "social"
    roadmap_hits = snippets(text, ROADMAP_TERMS)
    shipped_hits = snippets(text, SHIPPED_TERMS + FEATURE_TERMS)

    if social and (roadmap_hits or shipped_hits):
        return {
            "classification": "Weak signal",
            "wallet": source.wallet_name,
            "wallet_id": source.wallet_id,
            "source": source.url,
            "source_kind": source.kind,
            "title": current.get("title"),
            "evidence": (roadmap_hits or shipped_hits)[:2],
        }
    if roadmap_hits:
        return {
            "classification": "Roadmap update",
            "wallet": source.wallet_name,
            "wallet_id": source.wallet_id,
            "source": source.url,
            "source_kind": source.kind,
            "title": current.get("title"),
            "evidence": roadmap_hits[:2],
        }
    if shipped_hits:
        return {
            "classification": "Shipped feature",
            "wallet": source.wallet_name,
            "wallet_id": source.wallet_id,
            "source": source.url,
            "source_kind": source.kind,
            "title": current.get("title"),
            "evidence": shipped_hits[:2],
        }
    return None


def dedupe_findings(findings: list[dict]) -> list[dict]:
    seen: set[tuple[str, str, str]] = set()
    out: list[dict] = []
    for finding in findings:
        evidence = finding.get("evidence") or [""]
        key = (finding["wallet_id"], finding["classification"], evidence[0])
        if key in seen:
            continue
        seen.add(key)
        out.append(finding)
    return out


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"version": 1, "sources": {}}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def source_key(source: Source) -> str:
    return f"{source.wallet_id}|{source.url}"


def run(
    data_dir: Path,
    state_path: Path,
    reports_dir: Path,
    wallet_filter: set[str] | None = None,
    fetcher: Callable[[str], FetchResult] = fetch_url,
    now: dt.datetime | None = None,
    write_state: bool = True,
) -> Path:
    now = now or dt.datetime.now(dt.timezone.utc).astimezone()
    wallets = load_software_wallets(data_dir)
    if wallet_filter:
        wallets = [w for w in wallets if w["id"] in wallet_filter]
    sources = resolve_sources(wallets)
    state = load_state(state_path)
    prior_sources = state.setdefault("sources", {})

    findings: list[dict] = []
    failures: list[dict] = []
    unchanged_wallets: set[str] = set()
    changed_wallets: set[str] = set()
    baseline_wallets: set[str] = set()
    checked_wallets: set[str] = set()

    for source in sources:
        checked_wallets.add(source.wallet_name)
        result = fetcher(source.url)
        if not result.ok:
            failures.append({"wallet": source.wallet_name, "url": source.url, "error": result.error or f"HTTP {result.status}"})
            continue

        cleaned = clean_text(result.text)
        current = {
            "wallet_id": source.wallet_id,
            "wallet": source.wallet_name,
            "url": source.url,
            "kind": source.kind,
            "label": source.label,
            "checked_at": now.isoformat(timespec="seconds"),
            "status": result.status,
            "final_url": result.final_url,
            "title": page_title(result.text, cleaned),
            "hash": source_hash(cleaned),
        }
        key = source_key(source)
        previous = prior_sources.get(key)
        finding = classify_change(source, previous, current, cleaned)
        if finding:
            findings.append(finding)
            changed_wallets.add(source.wallet_name)
        elif previous is None:
            baseline_wallets.add(source.wallet_name)
        else:
            unchanged_wallets.add(source.wallet_name)
        prior_sources[key] = current

    state["last_run_at"] = now.isoformat(timespec="seconds")
    state["wallet_count"] = len(wallets)
    state["source_count"] = len(sources)
    if write_state:
        save_state(state_path, state)

    findings = dedupe_findings(findings)
    report = render_report(now, wallets, sources, findings, failures, unchanged_wallets, changed_wallets, baseline_wallets)
    reports_dir.mkdir(parents=True, exist_ok=True)
    out = reports_dir / f"{now.date().isoformat()}-wallet-tracking.md"
    out.write_text(report)
    return out


def render_report(
    now: dt.datetime,
    wallets: list[dict],
    sources: list[Source],
    findings: list[dict],
    failures: list[dict],
    unchanged_wallets: set[str],
    changed_wallets: set[str],
    baseline_wallets: set[str],
) -> str:
    grouped = {
        "Shipped feature": [f for f in findings if f["classification"] == "Shipped feature"],
        "Roadmap update": [f for f in findings if f["classification"] == "Roadmap update"],
        "Weak signal": [f for f in findings if f["classification"] == "Weak signal"],
    }
    lines = [
        f"# Hermes Wallet Tracking - {now.date().isoformat()}",
        "",
        "## Executive Summary",
        "",
        f"- Wallets checked: {len(wallets)}",
        f"- Sources checked: {len(sources)}",
        f"- High-confidence shipped features: {len(grouped['Shipped feature'])}",
        f"- Roadmap/beta/deprecation updates: {len(grouped['Roadmap update'])}",
        f"- Weak social/marketing signals: {len(grouped['Weak signal'])}",
        f"- Source check failures: {len(failures)}",
        "",
    ]
    if baseline_wallets and not findings:
        lines += [
            "This run established the initial baseline for source snapshots. Future runs will compare against this state.",
            "",
        ]

    for heading, items in grouped.items():
        lines += [f"## {heading}s" if heading != "Weak signal" else "## Weak Signals", ""]
        if not items:
            lines += ["None.", ""]
            continue
        for item in items:
            lines += [
                f"### {item['wallet']}",
                "",
                f"- Source: [{item.get('title') or item['source']}]({item['source']})",
                f"- Source type: `{item['source_kind']}`",
                "- Evidence:",
            ]
            for evidence in item["evidence"]:
                lines.append(f"  - {evidence}")
            lines += ["- Suggested dataset review: inspect `features.product` for affected PM datapoints before editing wallet JSON.", ""]

    lines += ["## Wallets Checked With No Meaningful Change", ""]
    quiet = sorted((unchanged_wallets | baseline_wallets) - changed_wallets)
    lines += [", ".join(quiet) if quiet else "None.", ""]

    lines += ["## Source Check Failures", ""]
    if not failures:
        lines += ["None.", ""]
    else:
        for failure in failures:
            lines.append(f"- {failure['wallet']}: [{failure['url']}]({failure['url']}) - {failure['error']}")
        lines.append("")

    lines += [
        "## Notes",
        "",
        "- Hermes is report-only and did not edit wallet JSON files.",
        "- Social-source findings are weak signals unless corroborated by official docs, releases, or app listings.",
        "- Dynamic pages, blocked socials, and inaccessible sources are reported as failures rather than scraped with browser automation.",
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Hermes software-wallet competitor tracking.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    parser.add_argument("--wallet", action="append", help="Wallet id to check. May be repeated.")
    parser.add_argument("--no-state-write", action="store_true", help="Write report but do not update state.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = run(
        args.data_dir,
        args.state,
        args.reports_dir,
        set(args.wallet) if args.wallet else None,
        write_state=not args.no_state_write,
    )
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
