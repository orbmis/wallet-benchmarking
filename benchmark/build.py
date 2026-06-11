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
    # --- Product datapoints (product.*) -----------------------------------
    # Platforms
    ("pMobile", "Mobile app", "Platforms", "product.platformCoverage.mobileApp", "state", "yes",
     "Ships a native mobile app."),
    ("pExtension", "Browser extension", "Platforms", "product.platformCoverage.browserExtension", "state", "yes",
     "Ships a browser extension."),
    ("pDesktop", "Desktop app", "Platforms", "product.platformCoverage.desktopApp", "state", "yes",
     "Ships a standalone desktop app."),
    ("pWeb", "Web app", "Platforms", "product.platformCoverage.webApp", "state", "yes",
     "Offers a browser-based web app."),
    ("pBrowserNative", "Browser-native", "Platforms", "product.platformCoverage.browserNative", "state", "yes",
     "Built directly into a browser."),
    # Ecosystems
    ("ecoEvm", "EVM", "Ecosystems", "product.supportedEcosystems.evm", "state", "yes",
     "Supports EVM chains."),
    ("ecoBitcoin", "Bitcoin", "Ecosystems", "product.supportedEcosystems.bitcoin", "state", "yes",
     "Supports Bitcoin."),
    ("ecoSolana", "Solana", "Ecosystems", "product.supportedEcosystems.solana", "state", "yes",
     "Supports Solana."),
    ("ecoCosmos", "Cosmos", "Ecosystems", "product.supportedEcosystems.cosmos", "state", "yes",
     "Supports the Cosmos ecosystem."),
    ("ecoTon", "TON", "Ecosystems", "product.supportedEcosystems.ton", "state", "yes",
     "Supports TON."),
    ("ecoSui", "Sui", "Ecosystems", "product.supportedEcosystems.sui", "state", "yes",
     "Supports Sui."),
    ("ecoAptos", "Aptos", "Ecosystems", "product.supportedEcosystems.aptos", "state", "yes",
     "Supports Aptos."),
    ("ecoCardano", "Cardano", "Ecosystems", "product.supportedEcosystems.cardano", "state", "yes",
     "Supports Cardano."),
    ("ecoXrp", "XRP Ledger", "Ecosystems", "product.supportedEcosystems.xrp", "state", "yes",
     "Supports the XRP Ledger."),
    # Onboarding
    ("obSpeed", "Time to first wallet", "Onboarding", "product.onboardingFriction.timeToFirstWallet", "value", None,
     "How fast a new user reaches a usable wallet."),
    ("obSeed", "Seed phrase at signup", "Onboarding", "product.onboardingFriction.seedPhraseRequiredAtSignup", "state", "no",
     "Forces seed-phrase handling during signup."),
    ("obPasskey", "Passkey signup", "Onboarding", "product.onboardingFriction.passkeySignup", "state", "yes",
     "Supports passkey-based signup."),
    ("obEmail", "Email signup", "Onboarding", "product.onboardingFriction.emailSignup", "state", "yes",
     "Supports email-based signup."),
    ("obGuest", "Guest mode", "Onboarding", "product.onboardingFriction.guestMode", "state", "yes",
     "Lets users try the app without setup."),
    ("obKyc", "KYC required for wallet", "Onboarding", "product.onboardingFriction.kycRequiredForWallet", "state", "no",
     "Requires identity verification to create a wallet."),
    ("obEmbedded", "Embedded wallet mode", "Onboarding", "product.onboardingFriction.embeddedWalletMode", "state", "yes",
     "Offers a no-seed embedded wallet."),
    # Fiat ramps
    ("rampBuy", "Buy crypto", "Fiat ramps", "product.fiatRamps.buyCrypto", "state", "yes",
     "In-app fiat-to-crypto purchases."),
    ("rampSell", "Sell crypto", "Fiat ramps", "product.fiatRamps.sellCrypto", "state", "yes",
     "In-app crypto-to-fiat off-ramp."),
    ("rampCard", "Card payments", "Fiat ramps", "product.fiatRamps.card", "state", "yes",
     "Card-based ramp payments."),
    ("rampApple", "Apple Pay", "Fiat ramps", "product.fiatRamps.applePay", "state", "yes",
     "Apple Pay ramp support."),
    ("rampGoogle", "Google Pay", "Fiat ramps", "product.fiatRamps.googlePay", "state", "yes",
     "Google Pay ramp support."),
    ("rampBank", "Bank transfer", "Fiat ramps", "product.fiatRamps.bankTransfer", "state", "yes",
     "Bank-transfer ramp support."),
    ("rampKyc", "Ramp KYC dependency", "Fiat ramps", "product.fiatRamps.kycDependency", "value", None,
     "Whether ramps require KYC."),
    # Portfolio
    ("pfNetWorth", "Net worth view", "Portfolio", "product.portfolioManagement.netWorth", "state", "yes",
     "Shows aggregate net worth."),
    ("pfPnl", "Profit & loss", "Portfolio", "product.portfolioManagement.pnl", "state", "yes",
     "Tracks profit and loss."),
    ("pfCostBasis", "Cost basis", "Portfolio", "product.portfolioManagement.costBasis", "state", "yes",
     "Tracks acquisition cost basis."),
    ("pfMultiWallet", "Multi-wallet aggregation", "Portfolio", "product.portfolioManagement.multiWalletAggregation", "state", "yes",
     "Aggregates multiple wallets in one view."),
    ("pfWatchOnly", "Watch-only wallets", "Portfolio", "product.portfolioManagement.watchOnlyWallets", "state", "yes",
     "Track addresses without keys."),
    ("pfNft", "NFT portfolio", "Portfolio", "product.portfolioManagement.nftSupport", "state", "yes",
     "Includes NFTs in the portfolio."),
    # DeFi positions
    ("defiStaking", "Staking positions", "DeFi positions", "product.defiPositionAwareness.stakingPositions", "state", "yes",
     "Surfaces staking positions."),
    ("defiLending", "Lending positions", "DeFi positions", "product.defiPositionAwareness.lendingPositions", "state", "yes",
     "Surfaces lending positions."),
    ("defiLp", "LP positions", "DeFi positions", "product.defiPositionAwareness.lpPositions", "state", "yes",
     "Surfaces liquidity-pool positions."),
    ("defiVault", "Vault positions", "DeFi positions", "product.defiPositionAwareness.vaultPositions", "state", "yes",
     "Surfaces vault positions."),
    ("defiRewards", "Claimable rewards", "DeFi positions", "product.defiPositionAwareness.claimableRewards", "state", "yes",
     "Surfaces claimable rewards."),
    ("defiLiq", "Liquidation warnings", "DeFi positions", "product.defiPositionAwareness.liquidationWarnings", "state", "yes",
     "Warns about liquidation risk."),
    # Staking & earn
    ("stakeNative", "Native staking", "Staking & earn", "product.stakingEarn.nativeStaking", "state", "yes",
     "In-app native staking."),
    ("stakeLiquid", "Liquid staking", "Staking & earn", "product.stakingEarn.liquidStaking", "state", "yes",
     "In-app liquid staking."),
    ("stakeApy", "APY display", "Staking & earn", "product.stakingEarn.apyDisplay", "state", "yes",
     "Displays staking APY."),
    ("stakeClaim", "Rewards claiming", "Staking & earn", "product.stakingEarn.rewardsClaiming", "state", "yes",
     "Claim staking rewards in-app."),
    ("stakeValidator", "Validator choice", "Staking & earn", "product.stakingEarn.validatorChoice", "state", "yes",
     "Lets users pick a validator."),
    # NFTs
    ("nftDisplay", "NFT display", "NFTs", "product.nftCapabilities.display", "state", "yes",
     "Displays NFTs."),
    ("nftSend", "NFT send", "NFTs", "product.nftCapabilities.send", "state", "yes",
     "Send NFTs."),
    ("nftMint", "NFT mint", "NFTs", "product.nftCapabilities.mint", "state", "yes",
     "Mint NFTs in-app."),
    ("nftMarket", "Marketplace integration", "NFTs", "product.nftCapabilities.marketplaceIntegration", "state", "yes",
     "Integrates an NFT marketplace."),
    ("nftSpam", "Spam NFT hiding", "NFTs", "product.nftCapabilities.spamNftHiding", "state", "yes",
     "Hides spam NFTs."),
    # Gas UX
    ("gasAbstraction", "Gas abstraction", "Gas UX", "product.gasUx.gasAbstraction", "state", "yes",
     "Abstracts gas away from the user."),
    ("gasSponsorship", "Gas sponsorship", "Gas UX", "product.gasUx.gasSponsorship", "state", "yes",
     "Sponsors gas for users."),
    ("gasCustom", "Gas customization", "Gas UX", "product.gasUx.gasCustomization", "state", "yes",
     "Lets users tune gas settings."),
    ("gasPresets", "Speed presets", "Gas UX", "product.gasUx.speedPresets", "state", "yes",
     "Offers fee/speed presets."),
    ("gasStables", "Pay gas in stablecoins", "Gas UX", "product.gasUx.payGasInStablecoins", "state", "yes",
     "Pay gas using stablecoins."),
    ("gasStuck", "Stuck-tx recovery", "Gas UX", "product.gasUx.stuckTransactionRecovery", "state", "yes",
     "Helps recover stuck transactions."),
    # dApp experience
    ("dappBrowser", "In-app dApp browser", "dApp experience", "product.dappExperience.inAppBrowser", "state", "yes",
     "Built-in dApp browser."),
    ("dappDirectory", "Curated dApp directory", "dApp experience", "product.dappExperience.curatedDappDirectory", "state", "yes",
     "Curated directory of dApps."),
    ("dappSearch", "dApp search", "dApp experience", "product.dappExperience.dappSearch", "state", "yes",
     "Search for dApps."),
    ("dappRisk", "Risk-rated discovery", "dApp experience", "product.dappExperience.riskRatedDiscovery", "state", "yes",
     "Risk ratings in dApp discovery."),
    # Notifications
    ("notifSendRecv", "Send/receive alerts", "Notifications", "product.notifications.sendReceive", "state", "yes",
     "Notifies on send/receive."),
    ("notifPrice", "Price alerts", "Notifications", "product.notifications.priceAlerts", "state", "yes",
     "Price movement alerts."),
    ("notifSecurity", "Security alerts", "Notifications", "product.notifications.securityAlerts", "state", "yes",
     "Security-related alerts."),
    ("notifApproval", "Approval alerts", "Notifications", "product.notifications.approvalAlerts", "state", "yes",
     "Alerts on token approvals."),
    # Recovery UX
    ("recSocial", "Social recovery", "Recovery UX", "product.recoveryUx.socialRecovery", "state", "yes",
     "Social recovery support."),
    ("recGuardian", "Guardian recovery", "Recovery UX", "product.recoveryUx.guardianRecovery", "state", "yes",
     "Guardian-based recovery."),
    ("recCloud", "Cloud backup", "Recovery UX", "product.recoveryUx.cloudBackup", "state", "yes",
     "Cloud-based backup."),
    ("recPasskey", "Passkey recovery", "Recovery UX", "product.recoveryUx.passkeyRecovery", "state", "yes",
     "Passkey-based recovery."),
    # Device sync
    ("syncDesktopMobile", "Desktop⇄mobile sync", "Device sync", "product.deviceSync.desktopMobileSync", "state", "yes",
     "Syncs between desktop and mobile."),
    ("syncCloud", "Cloud-backed sync", "Device sync", "product.deviceSync.cloudBackedSync", "state", "yes",
     "Cloud-backed sync."),
    ("syncAccounts", "Syncs accounts", "Device sync", "product.deviceSync.syncsAccounts", "state", "yes",
     "Syncs accounts across devices."),
    ("syncSettings", "Syncs settings", "Device sync", "product.deviceSync.syncsSettings", "state", "yes",
     "Syncs settings across devices."),
    # Customer support
    ("supLiveChat", "Live chat", "Customer support", "product.customerSupport.liveChat", "state", "yes",
     "Offers live chat support."),
    ("supEmail", "Email support", "Customer support", "product.customerSupport.emailSupport", "state", "yes",
     "Offers email support."),
    ("supAi", "AI support", "Customer support", "product.customerSupport.aiSupport", "state", "yes",
     "AI-assisted support."),
    ("supHelp", "In-app help center", "Customer support", "product.customerSupport.inAppHelpCenter", "state", "yes",
     "In-app help center."),
    ("supScam", "Scam recovery guidance", "Customer support", "product.customerSupport.scamRecoveryGuidance", "state", "yes",
     "Guidance for scam recovery."),
    # Developer offering
    ("devWalletConnect", "WalletConnect", "Developer offering", "product.developerOffering.walletConnectSupport", "state", "yes",
     "Supports WalletConnect."),
    ("devEip6963", "EIP-6963", "Developer offering", "product.developerOffering.eip6963", "state", "yes",
     "Implements EIP-6963 provider discovery."),
    ("devEip5792", "EIP-5792", "Developer offering", "product.developerOffering.eip5792", "state", "yes",
     "Implements EIP-5792 wallet calls."),
    ("devSdk", "Embedded wallet SDK", "Developer offering", "product.developerOffering.embeddedWalletSdk", "state", "yes",
     "Offers an embedded-wallet SDK."),
    ("devWhiteLabel", "White-label offering", "Developer offering", "product.developerOffering.whiteLabelOffering", "state", "yes",
     "Offers a white-label product."),
    # Release velocity
    ("relFreq", "Release frequency", "Release velocity", "product.releaseVelocity.releaseFrequency", "value", None,
     "How often the product ships releases."),
    ("relChangelog", "Changelog detail", "Release velocity", "product.releaseVelocity.changelogDetail", "value", None,
     "Level of detail in release notes."),
    ("relLatest", "Latest release date", "Release velocity", "product.releaseVelocity.latestReleaseDate", "value", None,
     "Date of the most recent release."),
    # Pricing & fees
    ("feeSwap", "Swap fees disclosed", "Pricing & fees", "product.pricingFeeModel.swapFees", "state", "yes",
     "Discloses swap fees."),
    ("feeBridge", "Bridge fees disclosed", "Pricing & fees", "product.pricingFeeModel.bridgeFees", "state", "yes",
     "Discloses bridge fees."),
    ("feeSpread", "Spread disclosure", "Pricing & fees", "product.pricingFeeModel.spreadDisclosure", "state", "yes",
     "Discloses pricing spread."),
    ("feeHidden", "Hidden partner revenue", "Pricing & fees", "product.pricingFeeModel.hiddenPartnerRevenue", "state", "no",
     "Takes undisclosed partner revenue. Less is better."),
    ("feeSubscription", "Subscription features", "Pricing & fees", "product.pricingFeeModel.subscriptionFeatures", "state", "yes",
     "Offers paid subscription features."),
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

def build_payload():
    """Resolve the DSL into the normalized {wallets, metrics, cats} model.

    Shared with sibling generators (e.g. build_gaps.py) so the $ref / $call
    resolution lives in exactly one place.
    """
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

    metrics = [{"key": k, "label": l, "cat": c, "path": path, "type": typ, "good": g, "desc": d}
               for (k, l, c, path, typ, g, d) in M]

    return {"wallets": wallets, "metrics": metrics, "cats": CATS}

# --- emit HTML -------------------------------------------------------------

def write_manifest():
    """List the wallet JSON files so the dynamic page can fetch them client-side
    (no directory listing is available over http)."""
    wdir = os.path.join(DATA, "wallets")
    files = sorted(f for f in os.listdir(wdir)
                   if f.endswith(".json") and f != "manifest.json")
    path = os.path.join(wdir, "manifest.json")
    with open(path, "w") as f:
        json.dump({"wallets": files}, f, indent=2)
    return files


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    # index.html loads the wallet data dynamically at runtime and resolves the
    # $ref / $call DSL in the browser; build.py only bakes in the metric catalog
    # (the single source of truth shared with the gaps/quadrant generators) and
    # refreshes the manifest the page fetches.
    metrics = [{"key": k, "label": l, "cat": c, "path": p, "type": t, "good": g, "desc": d}
               for (k, l, c, p, t, g, d) in M]
    template = open(os.path.join(here, "template.html")).read()
    out = template.replace("/*__METRICS__*/", json.dumps(metrics, ensure_ascii=False))
    with open(os.path.join(here, "index.html"), "w") as f:
        f.write(out)
    files = write_manifest()
    print("metrics:", len(metrics), "cats:", len(CATS), "wallet files:", len(files))
    print("wrote benchmark/index.html and data/wallets/manifest.json")


if __name__ == "__main__":
    main()
