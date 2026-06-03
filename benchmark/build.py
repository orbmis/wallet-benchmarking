#!/usr/bin/env python3
"""Generate a self-contained wallet-benchmark HTML page from the data/ JSON.

Resolves the $ref / $call DSL into a normalized {state, detail, ref} model per
(wallet, metric) cell, then inlines everything into benchmark/index.html so the
page works by double-clicking (no server required).
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

wallets_raw = json.load(open(os.path.join(DATA, "wallets.json")))

# --- DSL helpers -----------------------------------------------------------

def short_enum(s):
    """'FeeDisplayLevel.COMPREHENSIVE' -> 'COMPREHENSIVE'."""
    return s.rsplit(".", 1)[-1] if isinstance(s, str) and "." in s else s

def norm_urls(u):
    out = []
    if isinstance(u, str):
        out.append({"url": u})
    elif isinstance(u, list):
        for it in u:
            if isinstance(it, str):
                out.append({"url": it})
            elif isinstance(it, dict) and "url" in it:
                url = it["url"]
                if isinstance(url, list):
                    url = url[0] if url else ""
                out.append({"url": url, "label": it.get("label")})
    elif isinstance(u, dict) and "url" in u:
        out += norm_urls(u["url"])
    return out

def trunc(s, n=400):
    if isinstance(s, str) and len(s) > n:
        return s[: n - 1] + "…"
    return s

def extract_ref(node):
    """Return {'sourced':bool, 'citations':[{url,label,explanation}], 'named':str}."""
    if node is None:
        return None
    if isinstance(node, str):
        if node.startswith("http"):
            return {"sourced": True, "citations": [{"url": node}]}
        return {"sourced": False, "named": node}  # e.g. dataLeakReferences.lifi
    if isinstance(node, list):
        cites, sourced = [], False
        for it in node:
            r = extract_ref(it)
            if r and r.get("citations"):
                cites += r["citations"]
                sourced = True
        return {"sourced": sourced, "citations": cites} if cites else None
    if isinstance(node, dict):
        if "$ref" in node:
            return {"sourced": False, "named": node["$ref"]}  # refTodo etc.
        expl = trunc(node.get("explanation"))
        lab = node.get("label")
        urls = norm_urls(node.get("url")) if "url" in node else []
        cites = []
        for u in urls:
            cites.append({"url": u["url"], "label": u.get("label") or lab, "explanation": expl})
        if not cites and expl:
            cites.append({"explanation": expl, "label": lab})
        return {"sourced": bool(urls), "citations": cites} if cites else None
    return None

def find_ref(node, depth=0):
    """Best-effort: first ref-bearing thing in a subtree."""
    if depth > 6 or node is None:
        return None
    if isinstance(node, dict):
        if "ref" in node:
            r = extract_ref(node["ref"])
            if r:
                return r
        for v in node.values():
            r = find_ref(v, depth + 1)
            if r:
                return r
    elif isinstance(node, list):
        for v in node:
            r = find_ref(v, depth + 1)
            if r:
                return r
    return None

def has_support(node, depth=0):
    if depth > 6 or node is None:
        return False
    if isinstance(node, dict):
        if node.get("$call") in ("supported", "featureSupported"):
            return True
        if node.get("$ref") in ("featureSupported", "supported"):
            return True
        return any(has_support(v, depth + 1) for v in node.values())
    if isinstance(node, list):
        return any(has_support(v, depth + 1) for v in node)
    return False

def classify(node):
    """Return (state, detail) where state in yes|no|partial|unknown|value."""
    if node is None:
        return ("unknown", None)
    if isinstance(node, bool):
        return ("yes" if node else "no", None)
    if isinstance(node, str):
        return ("value", short_enum(node))
    if isinstance(node, dict):
        if "$ref" in node:
            r = node["$ref"]
            if r == "notSupported":
                return ("no", None)
            return ("yes", None)  # featureSupported / named configured object
        if "$call" in node:
            c = node["$call"]
            if c.startswith("not") or "notSupported" in c:
                return ("no", None)
            if c in ("supported", "featureSupported"):
                return ("yes", None)
            return ("yes", None)  # parser-style calls -> configured
        return ("partial", None)
    return ("unknown", None)

def get_path(root, dotted):
    cur = root
    for k in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur

# --- metric catalog --------------------------------------------------------
# good: which state is favorable for the end user (for color polarity)
M = [
    # Accounts
    ("eoa", "EOA support", "Accounts", "accountSupport.eoa", "state", "yes",
     "Supports standard externally-owned accounts."),
    ("erc4337", "ERC-4337 smart accounts", "Accounts", "accountSupport.rawErc4337", "state", "yes",
     "Native ERC-4337 account abstraction."),
    ("eip7702", "EIP-7702 upgraded EOAs", "Accounts", "accountSupport.eip7702", "state", "yes",
     "Lets a normal EOA act as a smart account via EIP-7702."),
    ("safe", "Safe smart accounts", "Accounts", "accountSupport.safe", "state", "yes",
     "Can manage / sign for Safe multisig accounts."),
    ("mpc", "MPC accounts", "Accounts", "accountSupport.mpc", "state", "yes",
     "Multi-party-computation key custody."),
    ("multiAddress", "Multiple accounts", "Accounts", "multiAddress", "state", "yes",
     "Manage more than one address."),
    # Privacy
    ("usageAnalytics", "Sends usage analytics", "Privacy", "privacy.analytics.usage", "state", "no",
     "Sends product/usage telemetry. Less is better for the user."),
    ("crashReports", "Sends crash reports", "Privacy", "privacy.analytics.crashReports", "state", "no",
     "Sends crash/error reports to a third party."),
    ("stealth", "Stealth addresses", "Privacy", "privacy.transactionPrivacy.STEALTH_ADDRESSES", "state", "yes",
     "Supports stealth-address receiving."),
    ("privacyPools", "Privacy Pools", "Privacy", "privacy.transactionPrivacy.PRIVACY_POOLS", "state", "yes",
     "Integrates Privacy Pools."),
    ("defaultTransfer", "Default transfer mode", "Privacy", "privacy.transactionPrivacy.defaultFungibleTokenTransferMode", "value", None,
     "Default privacy mode for token transfers."),
    # Security
    ("hwSupport", "Hardware wallet support", "Security", "security.hardwareWalletSupport", "support", "yes",
     "Can sign with at least one hardware wallet."),
    ("scamUrl", "Scam URL warnings", "Security", "security.scamAlerts.scamUrlWarning", "state", "yes",
     "Warns when connecting to known-malicious sites."),
    ("scamSend", "Risky-send warnings", "Security", "security.scamAlerts.sendTransactionWarning", "state", "yes",
     "Warns on risky transfers (new recipient, etc.)."),
    ("scamContract", "Malicious-contract warnings", "Security", "security.scamAlerts.contractTransactionWarning", "state", "yes",
     "Warns on interaction with flagged contracts."),
    ("txSim", "Transaction simulation", "Security", "security.transactionLegibility.transactionSimulations", "state", "yes",
     "Previews transaction outcome before signing."),
    ("bugBounty", "Bug bounty program", "Security", "security.bugBountyProgram", "state", "yes",
     "Runs a bug bounty program."),
    ("audits", "Public audits", "Security", "security.publicSecurityAudits", "count_high", "yes",
     "Number of public security audits."),
    ("openHigh", "Open high-sev flaws", "Security", "security.publicSecurityAudits", "count_low", "yes",
     "Unpatched HIGH-severity findings from audits. Lower is better."),
    ("duress", "Duress / decoy mode", "Security", "security.duressResistance.duressMode", "state", "yes",
     "Decoy wallet under coercion."),
    ("passkey", "Passkey verification", "Security", "security.passkeyVerification", "state", "yes",
     "Passkey-based verification."),
    ("lightClient", "L1 light client", "Security", "security.lightClient.ethereumL1", "state", "yes",
     "Trust-minimized L1 light client."),
    # Self-sovereignty
    ("approvals", "Token-approval management", "Self-sovereignty", "selfSovereignty.permissionsManagement", "support", "yes",
     "Inspect / revoke token approvals."),
    ("selfBroadcast", "Self-broadcast (own node)", "Self-sovereignty", "selfSovereignty.transactionSubmission.l1.selfBroadcastViaSelfHostedNode", "state", "yes",
     "Can broadcast via a self-hosted node."),
    # Chain abstraction
    ("bridging", "Built-in bridging", "Chain abstraction", "chainAbstraction.bridging.builtInBridging", "state", "yes",
     "Native cross-chain bridging."),
    ("globalValue", "Unified balance view", "Chain abstraction", "chainAbstraction.crossChainBalances.globalAccountValue", "state", "yes",
     "Single cross-chain account value."),
    # Transparency
    ("ens", "ENS resolution", "Transparency", "addressResolution.nonChainSpecificEnsResolution", "state", "yes",
     "Resolves ENS names."),
    ("changelog", "Public changelog", "Transparency", "transparency.releaseTransparency.hasPublicChangelog", "state", "yes",
     "Publishes a changelog."),
    ("signing", "Signed releases", "Transparency", "transparency.releaseTransparency.artifactSigning", "state", "yes",
     "Signs release artifacts."),
    ("reproducible", "Reproducible builds", "Transparency", "transparency.releaseTransparency.reproducibleBuilds", "state", "yes",
     "Builds are reproducible."),
    ("license", "App license", "Transparency", "licensing.walletAppLicense", "license", None,
     "Wallet application license."),
]

CATS = []
for m in M:
    if m[2] not in CATS:
        CATS.append(m[2])

def count_high_audits(node):
    if isinstance(node, list):
        return len(node)
    return None

def count_open_high(node):
    if not isinstance(node, list):
        return None
    n = 0
    for a in node:
        flaws = a.get("unpatchedFlaws") if isinstance(a, dict) else None
        if isinstance(flaws, list):
            for fl in flaws:
                sev = short_enum(fl.get("severityAtAuditPublication", ""))
                if sev == "HIGH" and fl.get("presentStatus") == "NOT_FIXED":
                    n += 1
    return n

def license_value(node):
    if not isinstance(node, dict):
        return None
    if "license" in node:
        return short_enum(node["license"])
    parts = set()
    for k, v in node.items():
        if isinstance(v, dict) and "license" in v:
            parts.add(short_enum(v["license"]))
    return " / ".join(sorted(parts)) if parts else None

# --- build normalized model ------------------------------------------------

wallets = []
for w in wallets_raw:
    feats = w["data"]["features"]
    meta = w["data"]["metadata"]
    cells = {}
    for key, label, cat, path, typ, good, desc in M:
        node = get_path(feats, path)
        ref = find_ref(node) if isinstance(node, (dict, list)) else None
        if typ == "state":
            state, detail = classify(node)
        elif typ == "value":
            state, detail = ("value", short_enum(node)) if isinstance(node, str) else ("unknown", None)
        elif typ == "support":
            if node is None:
                state, detail = "unknown", None
            else:
                state, detail = ("yes", None) if has_support(node) else ("no", None)
        elif typ == "count_high":
            c = count_high_audits(node)
            state, detail = ("count", c) if c is not None else ("unknown", None)
        elif typ == "count_low":
            c = count_open_high(node)
            state, detail = ("count", c) if c is not None else ("unknown", None)
        elif typ == "license":
            lv = license_value(node)
            state, detail = ("value", lv) if lv else ("unknown", None)
        else:
            state, detail = "unknown", None
        cells[key] = {"state": state, "detail": detail, "ref": ref}
    wallets.append({
        "id": w["id"],
        "name": meta.get("displayName", w["id"]),
        "blurb": meta.get("blurb", ""),
        "lastUpdated": meta.get("lastUpdated", ""),
        "variants": [k for k, v in (w["data"].get("variants") or {}).items() if v],
        "cells": cells,
    })

wallets.sort(key=lambda x: x["name"].lower())

metrics = [{"key": k, "label": l, "cat": c, "type": t, "good": g, "desc": d}
           for (k, l, c, t, p, g, d) in M]

payload = {"wallets": wallets, "metrics": metrics, "cats": CATS}

# --- emit HTML -------------------------------------------------------------
TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")).read()
out = TEMPLATE.replace("/*__DATA__*/", json.dumps(payload))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"), "w") as f:
    f.write(out)

print("wallets:", len(wallets), "metrics:", len(metrics), "cats:", len(CATS))
print("wrote benchmark/index.html")
