#!/usr/bin/env python3
"""Generate the self-contained "Positioning quadrant" page.

Reuses the normalized matrix model from build.py (build_payload) — the same
{wallets, metrics, cats} payload that drives index.html — and inlines it into
benchmark/quadrant.html. All scoring (per-category 0-100 score, axis placement,
quadrant split) lives in the page's JS so it shares one source of truth for
colour polarity with the matrix and gap report; this script only wires the data
in.
"""
import json, os

from build import build_payload

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    payload = build_payload()
    template = open(os.path.join(HERE, "template_quadrant.html")).read()
    out = template.replace("/*__DATA__*/", json.dumps(payload))
    open(os.path.join(HERE, "quadrant.html"), "w").write(out)
    # score categories = those holding at least one rankable (non value/license) metric
    rankable = [m for m in payload["metrics"] if m["type"] not in ("value", "license")]
    score_cats = [c for c in payload["cats"] if any(m["cat"] == c for m in rankable)]
    print("wallets:", len(payload["wallets"]),
          "rankable metrics:", len(rankable),
          "score categories:", len(score_cats))
    print("wrote benchmark/quadrant.html")


if __name__ == "__main__":
    main()
