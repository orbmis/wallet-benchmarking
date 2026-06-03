#!/usr/bin/env python3
"""Generate a self-contained privacy data-flow (Sankey) page.

Flattens each wallet's privacy.dataCollection tree into flow records
  (action -> entity -> data type, with policy + purpose)
resolving entity $refs against entities.json, and inlines them into
benchmark/privacy.html (a custom SVG Sankey, no external libs).
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
HERE = os.path.dirname(os.path.abspath(__file__))

W = json.load(open(os.path.join(DATA, "wallets.json")))
E = json.load(open(os.path.join(DATA, "entities.json")))

by_id = {e["id"].lower(): e for e in E}
by_name = {e["name"].lower(): e for e in E}

def humanize(s):
    return re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s).replace("_", " ").strip().title()

def resolve_entity(ref):
    cands = [ref.lower(), re.sub(r"[^a-z0-9]", "", ref.lower())]
    low = ref.lower()
    for suf in ("entity", "inc"):
        if low.endswith(suf):
            cands.append(low[: -len(suf)])
    for c in cands:
        if c in by_id:
            return by_id[c], False
        if c in by_name:
            return by_name[c], False
    return None, True  # unresolved

def entity_category(ent):
    """Return (label, risk) — risk: high|med|low for colouring."""
    if not ent:
        return ("Third party", "med")
    t = ent.get("type", {}) or {}
    # priority order — most privacy-relevant first
    if t.get("dataBroker"):
        return ("Data broker", "high")
    if t.get("exchange"):
        return ("Exchange", "high")
    if t.get("offchainDataProvider"):
        return ("Off-chain data", "med")
    if t.get("chainDataProvider"):
        return ("Chain data", "med")
    if t.get("transactionBroadcastProvider"):
        return ("Tx broadcast", "med")
    if t.get("securityAuditor"):
        return ("Auditor", "low")
    if t.get("walletDeveloper"):
        return ("Wallet developer", "low")
    if t.get("corporate"):
        return ("Corporate", "med")
    return ("Third party", "med")

NON_DATA_KEYS = {"endpoint", "multiAddress"}

def policy_rank(p):
    return {"ALWAYS": 2, "BY_DEFAULT": 1}.get(p, 0)

def extract_records(actions_dict, platform):
    """actions_dict: {ACTION: {collected:[...]}|null}. Yield flow records."""
    recs = []
    for action, av in (actions_dict or {}).items():
        if not isinstance(av, dict):
            continue
        for item in av.get("collected", []) or []:
            be = item.get("byEntity")
            ref = be.get("$ref") if isinstance(be, dict) else None
            if not ref:
                continue
            ent, unresolved = resolve_entity(ref)
            ename = humanize(ref) if unresolved else ent["name"]
            ecat, erisk = entity_category(ent)
            purposes = [humanize(p.split(".")[-1]) for p in (item.get("purposes") or [])]
            dc = item.get("dataCollection", {}) or {}
            for k, v in dc.items():
                if k in NON_DATA_KEYS:
                    continue
                if not isinstance(v, str):
                    continue
                pol = v.split(".")[-1]
                if pol == "NEVER":
                    continue  # explicitly not collected
                recs.append({
                    "platform": platform,
                    "action": humanize(action),
                    "entity": ename,
                    "entityCat": ecat,
                    "entityRisk": erisk,
                    "unresolved": unresolved,
                    "dataType": humanize(k),
                    "policy": pol,
                    "purposes": purposes,
                })
    return recs

wallets = []
for w in W:
    p = w["data"]["features"].get("privacy") or {}
    dc = p.get("dataCollection") if isinstance(p, dict) else None
    if not isinstance(dc, dict):
        continue
    per_platform = bool(set(dc) & {"BROWSER", "MOBILE", "DESKTOP"})
    recs = []
    platforms = []
    if per_platform:
        for plat in ("BROWSER", "MOBILE", "DESKTOP"):
            if isinstance(dc.get(plat), dict):
                pr = extract_records(dc[plat], plat)
                if pr:
                    platforms.append(plat)
                    recs += pr
    else:
        recs = extract_records(dc, "ALL")
        platforms = ["ALL"]
    if not recs:
        continue
    meta = w["data"]["metadata"]
    # summary stats (third parties = distinct entities; brokers = high-risk)
    ents = {(r["entity"], r["entityRisk"]) for r in recs}
    wallets.append({
        "id": w["id"],
        "name": meta.get("displayName", w["id"]),
        "perPlatform": per_platform,
        "platforms": platforms,
        "records": recs,
        "nEntities": len({r["entity"] for r in recs}),
        "nBrokers": len({e for e, risk in ents if risk == "high"}),
        "nActions": len({r["action"] for r in recs}),
    })

wallets.sort(key=lambda x: (-x["nBrokers"], x["name"].lower()))

payload = {"wallets": wallets}
TEMPLATE = open(os.path.join(HERE, "template_privacy.html")).read()
out = TEMPLATE.replace("/*__DATA__*/", json.dumps(payload))
open(os.path.join(HERE, "privacy.html"), "w").write(out)

print("wallets with privacy data:", len(wallets))
for w in wallets:
    print(f"  {w['name']:<10} entities={w['nEntities']} brokers={w['nBrokers']} actions={w['nActions']} records={len(w['records'])}")
print("wrote benchmark/privacy.html")
