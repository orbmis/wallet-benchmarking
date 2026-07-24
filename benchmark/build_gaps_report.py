#!/usr/bin/env python3
"""Inventory every *genuine* data gap in the matrix — the cells that render "—".

Reuses the normalized model from build.py (build_payload) so the definition of a
gap here is identical to what index.html shows. A gap is a cell whose resolved
state is "unknown". Cells that are "na" (Not Applicable — e.g. product.* metrics
on hardware-only wallets) are NOT gaps and are reported separately.

Outputs:
  - data/gaps.json : machine-readable worklist, one row per gap, with the dotted
                     data path so it can be filled directly (input to the fill
                     workflow / apply_proposals.py).
  - stdout         : completeness summary (per category / worst wallets / metrics).
"""
import json, os

from build import build_payload, DATA

HERE = os.path.dirname(os.path.abspath(__file__))


def collect():
    payload = build_payload()
    metrics = {m["key"]: m for m in payload["metrics"]}
    gaps = []
    na_count = 0
    for w in payload["wallets"]:
        for key, cell in w["cells"].items():
            if cell["state"] == "na":
                na_count += 1
                continue
            if cell["state"] != "unknown":
                continue
            m = metrics[key]
            ref = cell.get("ref")
            gaps.append({
                "walletId": w["id"],
                "walletName": w["name"],
                "metricKey": key,
                "label": m["label"],
                "category": m["cat"],
                "type": m["type"],
                "path": m["path"],
                # a gap can still carry an unsourced ref (e.g. refTodo) worth surfacing
                "hasUnsourcedRef": bool(ref and not ref.get("sourced")),
            })
    return payload, gaps, na_count


def summarize(payload, gaps, na_count):
    wallets, metrics = payload["wallets"], payload["metrics"]
    total = len(wallets) * len(metrics)
    filled = total - len(gaps) - na_count

    per_cat_gap, per_cat_tot = {}, {}
    mcat = {m["key"]: m["cat"] for m in metrics}
    for m in metrics:
        per_cat_tot[m["cat"]] = per_cat_tot.get(m["cat"], 0) + len(wallets)
    per_wallet, per_metric = {}, {}
    mlabel = {m["key"]: m["label"] for m in metrics}
    for g in gaps:
        per_cat_gap[g["category"]] = per_cat_gap.get(g["category"], 0) + 1
        per_wallet[g["walletName"]] = per_wallet.get(g["walletName"], 0) + 1
        per_metric[g["metricKey"]] = per_metric.get(g["metricKey"], 0) + 1

    print(f"cells: {total}  filled: {filled}  gaps: {len(gaps)}  n/a: {na_count}")
    print(f"completeness (excl. n/a): {100*filled/(total-na_count):.1f}%\n")

    print("gaps by category (worst first):")
    for cat, n in sorted(per_cat_gap.items(), key=lambda x: -x[1]):
        tot = per_cat_tot[cat]
        print(f"  {n:4d}/{tot:<4d}  {cat}")
    print("\ntop 15 wallets by gaps:")
    for name, n in sorted(per_wallet.items(), key=lambda x: -x[1])[:15]:
        print(f"  {n:4d}  {name}")
    print("\ntop 15 metrics by gaps:")
    for key, n in sorted(per_metric.items(), key=lambda x: -x[1])[:15]:
        print(f"  {n:4d}  {mlabel[key]}  ({key})")


def main():
    payload, gaps, na_count = collect()
    out = os.path.join(DATA, "gaps.json")
    with open(out, "w") as f:
        json.dump({"generated": True, "gapCount": len(gaps),
                   "naCount": na_count, "gaps": gaps}, f, indent=2)
    summarize(payload, gaps, na_count)
    print(f"\nwrote data/gaps.json ({len(gaps)} gaps)")


if __name__ == "__main__":
    main()
