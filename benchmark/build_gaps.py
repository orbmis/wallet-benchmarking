#!/usr/bin/env python3
"""Generate the self-contained "Where you lose" gap-report page.

Reuses the normalized matrix model from build.py (build_payload) — the same
{wallets, metrics, cats} payload that drives index.html — and inlines it into
benchmark/gaps.html. All gap logic (who-beats-whom, win/lose ranking) lives in
the page's JS so it shares one source of truth for colour polarity with the
matrix view; this script only wires the data in.
"""
import json, os

from build import build_payload

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    payload = build_payload()
    template = open(os.path.join(HERE, "template_gaps.html")).read()
    out = template.replace("/*__DATA__*/", json.dumps(payload))
    open(os.path.join(HERE, "gaps.html"), "w").write(out)
    # rankable = state/support/count metrics (value/license can't be ordered)
    rankable = [m for m in payload["metrics"] if m["type"] != "value" and m["type"] != "license"]
    print("wallets:", len(payload["wallets"]),
          "metrics:", len(payload["metrics"]),
          "rankable:", len(rankable))
    print("wrote benchmark/gaps.html")


if __name__ == "__main__":
    main()
