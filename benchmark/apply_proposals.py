#!/usr/bin/env python3
"""Apply researched gap fills to the wallet data.

Reads data/gaps-proposals.json (produced by the fill workflow) and writes each
verdict into the target per-wallet JSON at its dotted feature path, using the
same $ref / $call DSL that build.py resolves. Then regenerates the aggregated
data/wallets.json from the per-wallet files (the two are kept in lockstep).

Proposal shape (one object per gap):
  {
    "walletId":   "brave-wallet",
    "metricKey":  "feeSwap",              # for logging only
    "path":       "product.pricingFeeModel.swapFees",
    "decision":   "yes" | "no" | "value" | "unknown",
    "valueString":"MIT",                  # required when decision == "value"
    "citationUrl":"https://…",            # required for yes / value
    "explanation":"Swap fee disclosed in the in-app review screen."
  }

Guardrails (a fill is only as good as its source):
  - decision "unknown"  -> skipped, the gap stays a gap.
  - "yes"/"value" without a citationUrl -> skipped (never assert unsourced).
  - never emits refTodo.

Default is a DRY RUN. Pass --apply to write files.
"""
import json, os, sys

from build import DATA

WDIR = os.path.join(DATA, "wallets")
PROPOSALS = os.path.join(DATA, "gaps-proposals.json")


def wallet_file_index():
    """Map wallet id -> filename (id may differ from filename)."""
    idx = {}
    for fn in os.listdir(WDIR):
        if not fn.endswith(".json") or fn == "manifest.json":
            continue
        rec = json.load(open(os.path.join(WDIR, fn)))
        idx[rec["id"]] = fn
    return idx


def ref_obj(p):
    return {"url": p["citationUrl"], "explanation": p.get("explanation", "")}


def dsl_for(p):
    """Translate a proposal into a DSL node, or None to skip it."""
    d = p.get("decision")
    if d == "unknown":
        return None, "skip: unknown (no reliable source)"
    if d == "na":
        # feature categorically doesn't apply to this wallet -> renders "N/A"
        return {"$ref": "notApplicable"}, None
    if d == "yes":
        if not p.get("citationUrl"):
            return None, "skip: 'yes' without citation"
        return {"$call": "supported", "args": [{"ref": ref_obj(p)}]}, None
    if d == "no":
        # a "no" may or may not carry a source; keep the source when present
        if p.get("citationUrl"):
            return {"$call": "notSupported", "args": [{"ref": ref_obj(p)}]}, None
        return {"$ref": "notSupported"}, None
    if d == "value":
        if not p.get("citationUrl"):
            return None, "skip: 'value' without citation"
        if not p.get("valueString"):
            return None, "skip: 'value' without valueString"
        # the license metric resolves a {"license": ...} object, not a bare string
        # (see license_value() in build.py); other value metrics take a plain string.
        if p.get("path", "").endswith("walletAppLicense"):
            return {"license": p["valueString"], "ref": ref_obj(p)}, None
        return p["valueString"], None
    return None, f"skip: unknown decision {d!r}"


def set_path(features, dotted, node):
    cur = features
    parts = dotted.split(".")
    for k in parts[:-1]:
        nxt = cur.get(k)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[k] = nxt
        cur = nxt
    cur[parts[-1]] = node


def regenerate_aggregate(idx):
    """Rebuild data/wallets.json from the per-wallet files, preserving the
    existing record order to keep the git diff minimal."""
    agg_path = os.path.join(DATA, "wallets.json")
    existing = json.load(open(agg_path))
    order = [rec["id"] for rec in existing]
    for wid in idx:
        if wid not in order:
            order.append(wid)
    records = [json.load(open(os.path.join(WDIR, idx[wid]))) for wid in order if wid in idx]
    with open(agg_path, "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    return len(records)


def main():
    apply = "--apply" in sys.argv
    if not os.path.exists(PROPOSALS):
        sys.exit(f"no proposals file at {PROPOSALS}")
    proposals = json.load(open(PROPOSALS))
    if isinstance(proposals, dict):
        proposals = proposals.get("proposals", [])
    idx = wallet_file_index()

    # group proposals by wallet so each file is read/written once
    by_wallet = {}
    skipped = []
    for p in proposals:
        node, why = dsl_for(p)
        if node is None:
            skipped.append((p, why))
            continue
        by_wallet.setdefault(p["walletId"], []).append((p, node))

    applied = 0
    for wid, items in by_wallet.items():
        fn = idx.get(wid)
        if not fn:
            for p, _ in items:
                skipped.append((p, f"skip: unknown walletId {wid!r}"))
            continue
        path = os.path.join(WDIR, fn)
        rec = json.load(open(path))
        feats = rec["data"]["features"]
        for p, node in items:
            set_path(feats, p["path"], node)
            applied += 1
            print(f"  {wid:20s} {p['path']:55s} <- {p['decision']}")
        if apply:
            with open(path, "w") as f:
                json.dump(rec, f, indent=2, ensure_ascii=False)

    print(f"\napplied: {applied}   skipped: {len(skipped)}")
    for p, why in skipped[:40]:
        print(f"  {why}: {p.get('walletId')} {p.get('path')}")
    if len(skipped) > 40:
        print(f"  … and {len(skipped)-40} more")

    if apply:
        n = regenerate_aggregate(idx)
        print(f"\nregenerated data/wallets.json ({n} records)")
        print("now run: python3 build.py   (refresh index.html + manifest)")
    else:
        print("\nDRY RUN — no files written. Re-run with --apply to write.")


if __name__ == "__main__":
    main()
