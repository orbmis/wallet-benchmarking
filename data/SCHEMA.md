# Wallet data — property tree

Merged across all 32 files in `data/wallets/*.json`. Each record is `{id, source, export, data}`.

**Legend** — `<type>` leaf · `[]` array · `(n/32)` = key present in *n* of 32 wallets (no count = all).
`‹val›` = DSL-encoded value (`$ref`/`$call`/bool) · `⟐cited` = carries a `ref` citation.
The repeated citation plumbing (`$ref`/`$call`/`ref`) is collapsed into those two markers; `args[ ]`
(extra detail attached to a value) is expanded.

```
wallet
├── data
│   ├── features
│   │   ├── accountSupport
│   │   │   ├── defaultAccountType <string>  (22/32)
│   │   │   ├── eip7702 ‹val›  (22/32)
│   │   │   │   └── args[ ]  (9/22)
│   │   │   │       └── contract ‹val›  (6/9)
│   │   │   ├── eoa ‹val›  (22/32)
│   │   │   │   └── args[ ]  (19/22)
│   │   │   │       ├── canExportPrivateKey <bool>  (17/19)
│   │   │   │       ├── canExportSeedPhrase <bool>  (3/19)
│   │   │   │       └── keyDerivation
│   │   │   │           ├── canExportSeedPhrase <bool>  (17/19)
│   │   │   │           ├── derivationPath <string>  (17/19)
│   │   │   │           ├── seedPhrase <string>
│   │   │   │           └── type <string>  (17/19)
│   │   │   ├── mpc ‹val›  (22/32)
│   │   │   │   └── args[ ]  (2/22)
│   │   │   ├── rawErc4337 ‹val›  (22/32)
│   │   │   │   └── args[ ]  (7/22)
│   │   │   │       ├── contract ‹val›  (5/7)
│   │   │   │       ├── controllingSharesInSelfCustodyByDefault <string>  (5/7)
│   │   │   │       ├── keyRotationTransactionGeneration <string>  (5/7)
│   │   │   │       └── tokenTransferTransactionGeneration <string>  (5/7)
│   │   │   └── safe ‹val›  (22/32)
│   │   │       └── args[ ]  (5/22)
│   │   │           ├── canDeployNew <bool>  (3/5)
│   │   │           ├── controllingSharesInSelfCustodyByDefault <string>  (3/5)
│   │   │           ├── keyRotationTransactionGeneration <string>  (3/5)
│   │   │           ├── supportedOwners <string>  (3/5)
│   │   │           ├── supportsAddingOrRemovingSigners <bool>  (3/5)
│   │   │           ├── supportsKeyRotationWithoutModules <bool>  (3/5)
│   │   │           └── tokenTransferTransactionGeneration <string>  (3/5)
│   │   ├── addressResolution ⟐cited  (21/32)
│   │   │   ├── chainSpecificAddressing
│   │   │   │   ├── erc7828 ‹val›
│   │   │   │   └── erc7831 ‹val›
│   │   │   └── nonChainSpecificEnsResolution ‹val›
│   │   │       └── args[ ]  (19/21)
│   │   │           └── medium <string>  (16/19)
│   │   ├── appConnectionSupport ‹val›  (11/32)
│   │   │   └── args[ ]  (9/11)
│   │   │       ├── requiresManufacturerConsent ⟐cited
│   │   │       │   └── type <string>  (1/9)
│   │   │       └── supportedConnections
│   │   │           ├── AMBIRE <bool>  (2/9)
│   │   │           ├── FRAME <bool>  (3/9)
│   │   │           ├── METAMASK <bool>  (7/9)
│   │   │           ├── OTHER <bool>  (6/9)
│   │   │           ├── RABBY <bool>  (8/9)
│   │   │           └── VENDOR_OPEN_SOURCE_APP <bool>  (5/9)
│   │   ├── chainAbstraction  (21/32)
│   │   │   ├── bridging
│   │   │   │   ├── bridgingViaTransactionGeneration <null>  (1/21)
│   │   │   │   ├── builtInBridging ‹val›
│   │   │   │   │   └── args[ ]
│   │   │   │   │       ├── feesLargerThan1bps ‹val›  (8/21)
│   │   │   │   │       │   ├── afterSingleAction <string>  (6/8)
│   │   │   │   │       │   ├── byDefault <string>  (6/8)
│   │   │   │   │       │   └── fullySponsored <bool>  (6/8)
│   │   │   │   │       ├── fromChainGas <string>  (2/21)
│   │   │   │   │       ├── liquidityProvider <string>  (2/21)
│   │   │   │   │       └── risksExplained <string>  (8/21)
│   │   │   │   ├── suggestedBridging ‹val›  (20/21)
│   │   │   │   └── trustMinimizedBridging <null>  (1/21)
│   │   │   ├── crossChainBalances ⟐cited
│   │   │   │   ├── ether ‹val›  (11/21)
│   │   │   │   │   ├── crossChainSumView ‹val›  (6/11)
│   │   │   │   │   ├── perChainBalanceViewAcrossMultipleChains ‹val›  (6/11)
│   │   │   │   │   └── args[ ]  (3/11)
│   │   │   │   │       ├── crossChainSumView ‹val›
│   │   │   │   │       └── perChainBalanceViewAcrossMultipleChains ‹val›
│   │   │   │   ├── globalAccountValue ‹val›
│   │   │   │   │   └── args[ ]  (3/21)
│   │   │   │   ├── perChainAccountValue ‹val›
│   │   │   │   └── usdc ‹val›  (11/21)
│   │   │   │       ├── crossChainSumView ‹val›  (6/11)
│   │   │   │       ├── perChainBalanceViewAcrossMultipleChains ‹val›  (6/11)
│   │   │   │       └── args[ ]  (3/11)
│   │   │   │           ├── crossChainSumView ‹val›
│   │   │   │           └── perChainBalanceViewAcrossMultipleChains ‹val›
│   │   │   └── gasSubsidies  (1/21)
│   │   │       ├── l1GasRelay <null>
│   │   │       ├── l1GasTank <null>
│   │   │       └── l2GasRelay <null>
│   │   ├── chainConfigurability ‹val› ⟐cited  (21/32)
│   │   │   ├── BROWSER ‹val›  (1/21)
│   │   │   │   └── args[ ]
│   │   │   │       ├── customChainRpcEndpoint ‹val›
│   │   │   │       ├── l1 ‹val›
│   │   │   │       │   └── args[ ]
│   │   │   │       │       ├── rpcEndpointConfiguration <string>
│   │   │   │       │       └── withNoConnectivityExceptL1RPCEndpoint
│   │   │   │       │           ├── accountCreation ‹val›
│   │   │   │       │           ├── accountImport ‹val›
│   │   │   │       │           ├── erc20BalanceLookup ‹val›
│   │   │   │       │           ├── erc20TokenSend ‹val›
│   │   │   │       │           └── etherBalanceLookup ‹val›
│   │   │   │       └── nonL1 ‹val›
│   │   │   │           └── args[ ]
│   │   │   │               └── rpcEndpointConfiguration <string>
│   │   │   ├── customNetworks ‹val›  (1/21)
│   │   │   ├── MOBILE <null>  (1/21)
│   │   │   └── args[ ]  (13/21)
│   │   │       ├── customChainRpcEndpoint ‹val›
│   │   │       │   └── args[ ]  (2/13)
│   │   │       ├── l1 ‹val›
│   │   │       │   └── args[ ]  (12/13)
│   │   │       │       ├── rpcEndpointConfiguration <string>  (11/12)
│   │   │       │       └── withNoConnectivityExceptL1RPCEndpoint  (5/12)
│   │   │       │           ├── accountCreation ‹val›
│   │   │       │           ├── accountImport ‹val›
│   │   │       │           ├── erc20BalanceLookup ‹val›
│   │   │       │           ├── erc20TokenSend ‹val›
│   │   │       │           └── etherBalanceLookup ‹val›
│   │   │       └── nonL1 ‹val›  (6/13)
│   │   │           └── args[ ]
│   │   │               └── rpcEndpointConfiguration <string>
│   │   ├── ecosystem  (21/32)
│   │   │   └── delegation
│   │   │       ├── duringEOACreation <string>  (3/21)
│   │   │       ├── duringEOAImport <string>  (3/21)
│   │   │       ├── duringFirst7702Operation ‹val›  (3/21)
│   │   │       │   └── args[ ]
│   │   │       │       ├── nonDelegationTransactionDetailsIdenticalToNormalFlow <bool>
│   │   │       │       └── type <string>
│   │   │       └── fee  (3/21)
│   │   │           ├── crossChainGas ‹val›
│   │   │           └── walletSponsored ‹val›
│   │   ├── integration  (21/32)
│   │   │   ├── browser ⟐cited
│   │   │   │   ├── 1193 ‹val›  (17/21)
│   │   │   │   │   └── args[ ]  (3/17)
│   │   │   │   ├── 2700 ‹val›  (17/21)
│   │   │   │   └── 6963 ‹val›  (17/21)
│   │   │   │       └── args[ ]  (2/17)
│   │   │   └── walletCall ‹val›
│   │   │       └── args[ ]  (6/21)
│   │   │           └── atomicMultiTransactions ‹val›  (5/6)
│   │   ├── licensing ‹val›
│   │   │   ├── coreLicense ⟐cited  (5/32)
│   │   │   │   └── license <string>
│   │   │   ├── type <string>  (27/32)
│   │   │   └── walletAppLicense ⟐cited  (27/32)
│   │   │       ├── BROWSER ⟐cited  (3/27)
│   │   │       │   └── license <string>
│   │   │       ├── DESKTOP ⟐cited  (1/27)
│   │   │       │   └── license <string>
│   │   │       ├── HARDWARE ⟐cited  (1/27)
│   │   │       │   └── license <string>
│   │   │       ├── license <string>  (22/27)
│   │   │       └── MOBILE ⟐cited  (4/27)
│   │   │           └── license <string>  (3/4)
│   │   ├── monetization ⟐cited
│   │   │   ├── revenueBreakdownIsPublic <bool>
│   │   │   └── strategies
│   │   │       ├── donations <bool|null>
│   │   │       ├── ecosystemGrants <bool|null>
│   │   │       ├── governanceTokenLowFloat <bool|null>
│   │   │       ├── governanceTokenMostlyDistributed <bool|null>
│   │   │       ├── hiddenConvenienceFees <bool|null>
│   │   │       ├── publicOffering <bool|null>
│   │   │       ├── selfFunded <bool|null>
│   │   │       ├── transparentConvenienceFees <bool|null>
│   │   │       └── ventureCapital <bool|null>
│   │   ├── multiAddress ‹val›
│   │   │   └── args[ ]  (8/32)
│   │   ├── privacy
│   │   │   ├── analytics
│   │   │   │   ├── crashReports ‹val›
│   │   │   │   │   └── args[ ]  (21/32)
│   │   │   │   │       ├── entity ‹val›  (2/21)
│   │   │   │   │       └── policy <string>  (2/21)
│   │   │   │   └── usage ‹val›
│   │   │   │       ├── BROWSER ‹val›  (1/32)
│   │   │   │       │   └── args[ ]
│   │   │   │       │       ├── entity ‹val›
│   │   │   │       │       └── policy <string>
│   │   │   │       ├── DESKTOP <null>  (1/32)
│   │   │   │       ├── MOBILE <null>  (1/32)
│   │   │   │       └── args[ ]  (19/32)
│   │   │   │           ├── entity ‹val›  (1/19)
│   │   │   │           └── policy <string>  (1/19)
│   │   │   ├── appIsolation ‹val›  (21/32)
│   │   │   │   ├── BROWSER  (2/21)
│   │   │   │   │   ├── createInAppConnectionFlow ‹val›
│   │   │   │   │   ├── erc7846WalletConnect ‹val›
│   │   │   │   │   ├── ethAccounts ‹val›
│   │   │   │   │   │   └── args[ ]
│   │   │   │   │   │       └── defaultBehavior <string>
│   │   │   │   │   └── useAppSpecificLastConnectedAddresses ‹val›
│   │   │   │   ├── createInAppConnectionFlow ‹val›  (1/21)
│   │   │   │   │   └── args[ ]
│   │   │   │   ├── DESKTOP  (3/21)
│   │   │   │   │   ├── createInAppConnectionFlow ‹val›  (1/3)
│   │   │   │   │   ├── erc7846WalletConnect ‹val›  (1/3)
│   │   │   │   │   ├── ethAccounts ‹val›  (1/3)
│   │   │   │   │   │   └── args[ ]
│   │   │   │   │   │       └── defaultBehavior <string>
│   │   │   │   │   └── useAppSpecificLastConnectedAddresses ‹val›  (1/3)
│   │   │   │   ├── erc7846WalletConnect ‹val›  (1/21)
│   │   │   │   ├── ethAccounts ‹val›  (1/21)
│   │   │   │   │   └── args[ ]
│   │   │   │   │       └── defaultBehavior <string>
│   │   │   │   ├── MOBILE <null>  (3/21)
│   │   │   │   └── useAppSpecificLastConnectedAddresses ‹val›  (1/21)
│   │   │   ├── dataCollection
│   │   │   │   ├── APP_CONNECTION  (4/32)
│   │   │   │   │   └── collected  (2/4)
│   │   │   │   ├── BROWSER  (1/32)
│   │   │   │   │   ├── APP_CONNECTION
│   │   │   │   │   │   └── collected
│   │   │   │   │   │       ├── byEntity ‹val›
│   │   │   │   │   │       ├── dataCollection
│   │   │   │   │   │       │   ├── ACCOUNT_ADDRESS <string>
│   │   │   │   │   │       │   ├── endpoint ‹val›
│   │   │   │   │   │       │   ├── IP_ADDRESS <string>
│   │   │   │   │   │       │   ├── multiAddress
│   │   │   │   │   │       │   │   └── type <string>
│   │   │   │   │   │       │   ├── TRACKING_IDENTIFIER <string>
│   │   │   │   │   │       │   └── WALLET_CONNECTED_DOMAINS <string>
│   │   │   │   │   │       └── purposes
│   │   │   │   │   ├── INSTALL <null>
│   │   │   │   │   ├── MAKE_TRANSACTION
│   │   │   │   │   │   └── collected
│   │   │   │   │   ├── NATIVE_SWAP
│   │   │   │   │   │   └── collected
│   │   │   │   │   ├── ONBOARDING_IMPORT <null>
│   │   │   │   │   ├── ONBOARDING_NEW
│   │   │   │   │   │   ├── collected
│   │   │   │   │   │   └── publishedOnchain <string>
│   │   │   │   │   ├── SEND_ETHER
│   │   │   │   │   │   └── collected
│   │   │   │   │   ├── SEND_USDC <null>
│   │   │   │   │   └── UNCLASSIFIED
│   │   │   │   │       └── collected
│   │   │   │   │           ├── byEntity ‹val›
│   │   │   │   │           ├── dataCollection
│   │   │   │   │           │   ├── ACCOUNT_ADDRESS <string>
│   │   │   │   │           │   ├── CEX_ACCOUNT <string>
│   │   │   │   │           │   ├── endpoint ‹val›
│   │   │   │   │           │   ├── IP_ADDRESS <string>
│   │   │   │   │           │   ├── MEMPOOL_TRANSACTIONS <string>
│   │   │   │   │           │   ├── multiAddress
│   │   │   │   │           │   │   └── type <string>
│   │   │   │   │           │   ├── TRACKING_IDENTIFIER <string>
│   │   │   │   │           │   └── USER_ACTIONS <string>
│   │   │   │   │           └── purposes
│   │   │   │   ├── DESKTOP <null>  (1/32)
│   │   │   │   ├── INSTALL  (4/32)
│   │   │   │   │   └── collected  (1/4)
│   │   │   │   ├── MAKE_TRANSACTION  (4/32)
│   │   │   │   │   └── collected
│   │   │   │   │       ├── byEntity ‹val›
│   │   │   │   │       ├── dataCollection
│   │   │   │   │       │   ├── ACCOUNT_ADDRESS <string>
│   │   │   │   │       │   ├── endpoint ‹val›
│   │   │   │   │       │   ├── IP_ADDRESS <string>  (4/5)
│   │   │   │   │       │   ├── MEMPOOL_TRANSACTIONS <string>  (4/5)
│   │   │   │   │       │   └── multiAddress
│   │   │   │   │       │       └── type <string>
│   │   │   │   │       └── purposes
│   │   │   │   ├── MOBILE <null>  (1/32)
│   │   │   │   ├── NATIVE_SWAP  (4/32)
│   │   │   │   │   └── collected  (2/4)
│   │   │   │   │       ├── byEntity ‹val›
│   │   │   │   │       ├── dataCollection
│   │   │   │   │       │   ├── endpoint ‹val›
│   │   │   │   │       │   └── IP_ADDRESS <string>
│   │   │   │   │       └── purposes
│   │   │   │   ├── ONBOARDING_IMPORT  (4/32)
│   │   │   │   │   ├── collected  (1/4)
│   │   │   │   │   │   ├── byEntity ‹val›
│   │   │   │   │   │   ├── dataCollection
│   │   │   │   │   │   │   ├── ACCOUNT_ADDRESS <string>
│   │   │   │   │   │   │   ├── ASSETS <string>  (1/3)
│   │   │   │   │   │   │   ├── BALANCE <string>  (1/3)
│   │   │   │   │   │   │   ├── endpoint ‹val›
│   │   │   │   │   │   │   ├── IP_ADDRESS <string>
│   │   │   │   │   │   │   └── multiAddress
│   │   │   │   │   │   │       └── type <string>
│   │   │   │   │   │   └── purposes
│   │   │   │   │   └── publishedOnchain <string>  (1/4)
│   │   │   │   ├── ONBOARDING_NEW  (4/32)
│   │   │   │   │   ├── collected
│   │   │   │   │   │   ├── byEntity ‹val›
│   │   │   │   │   │   ├── dataCollection
│   │   │   │   │   │   │   ├── ACCOUNT_ADDRESS <string>
│   │   │   │   │   │   │   ├── ASSETS <string>  (1/6)
│   │   │   │   │   │   │   ├── BALANCE <string>  (1/6)
│   │   │   │   │   │   │   ├── CEX_ACCOUNT <string>  (1/6)
│   │   │   │   │   │   │   ├── endpoint ‹val›
│   │   │   │   │   │   │   ├── FARCASTER_ACCOUNT <string>  (2/6)
│   │   │   │   │   │   │   ├── IP_ADDRESS <string>
│   │   │   │   │   │   │   └── multiAddress  (4/6)
│   │   │   │   │   │   │       └── type <string>
│   │   │   │   │   │   └── purposes
│   │   │   │   │   └── publishedOnchain ⟐cited
│   │   │   │   │       ├── PSEUDONYM <string>  (1/4)
│   │   │   │   │       └── purposes  (1/4)
│   │   │   │   ├── SEND_ETHER  (4/32)
│   │   │   │   │   └── collected
│   │   │   │   ├── SEND_USDC  (4/32)
│   │   │   │   │   └── collected  (1/4)
│   │   │   │   │       ├── byEntity ‹val›
│   │   │   │   │       ├── dataCollection
│   │   │   │   │       │   ├── ACCOUNT_ADDRESS <string>
│   │   │   │   │       │   ├── ASSETS <string>
│   │   │   │   │       │   ├── BALANCE <string>
│   │   │   │   │       │   ├── endpoint ‹val›
│   │   │   │   │       │   ├── IP_ADDRESS <string>
│   │   │   │   │       │   └── multiAddress
│   │   │   │   │       │       └── type <string>
│   │   │   │   │       └── purposes
│   │   │   │   └── UNCLASSIFIED  (3/32)
│   │   │   │       └── collected
│   │   │   │           ├── byEntity ‹val›
│   │   │   │           ├── dataCollection
│   │   │   │           │   ├── ACCOUNT_ADDRESS <string>  (4/6)
│   │   │   │           │   ├── BALANCE <string>  (1/6)
│   │   │   │           │   ├── endpoint ‹val›
│   │   │   │           │   ├── IP_ADDRESS <string>
│   │   │   │           │   ├── MEMPOOL_TRANSACTIONS <string>  (1/6)
│   │   │   │           │   ├── multiAddress  (2/6)
│   │   │   │           │   │   └── type <string>
│   │   │   │           │   ├── PSEUDONYM <string>  (2/6)
│   │   │   │           │   └── USER_ACTIONS <string>  (1/6)
│   │   │   │           └── purposes
│   │   │   ├── hardwarePrivacy ‹val›  (11/32)
│   │   │   │   ├── details <string>  (2/11)
│   │   │   │   ├── inspectableRemoteCalls <string>  (2/11)
│   │   │   │   ├── phoningHome <string>  (2/11)
│   │   │   │   ├── type <string>  (2/11)
│   │   │   │   ├── url <string>  (1/11)
│   │   │   │   ├── wirelessPrivacy <string>  (2/11)
│   │   │   │   └── args[ ]  (1/11)
│   │   │   │       ├── inspectableRemoteCalls <string>
│   │   │   │       ├── phoningHome <string>
│   │   │   │       ├── type <string>
│   │   │   │       └── wirelessPrivacy <string>
│   │   │   ├── privacyPolicy <string|null>
│   │   │   └── transactionPrivacy
│   │   │       ├── defaultFungibleTokenTransferMode <string>  (21/32)
│   │   │       ├── PRIVACY_POOLS ‹val›  (21/32)
│   │   │       │   └── args[ ]  (1/21)
│   │   │       ├── RAILGUN ‹val›  (21/32)
│   │   │       ├── STEALTH_ADDRESSES ‹val›  (21/32)
│   │   │       │   └── args[ ]  (1/21)
│   │   │       └── TORNADO_CASH_NOVA ‹val›  (21/32)
│   │   ├── profile <string>
│   │   ├── security
│   │   │   ├── accountRecovery ‹val›
│   │   │   │   ├── guardianRecovery ‹val›  (7/32)
│   │   │   │   │   └── args[ ]  (2/7)
│   │   │   │   │       └── minimumGuardianPolicy
│   │   │   │   │           ├── descriptionMarkdown <string>
│   │   │   │   │           ├── optionalGuardians
│   │   │   │   │           │   ├── description <string>
│   │   │   │   │           │   ├── entity ‹val›
│   │   │   │   │           │   └── type <string>
│   │   │   │   │           ├── optionalGuardiansMinimumConfigurable <number>
│   │   │   │   │           ├── optionalGuardiansMinimumNeededForRecovery <number>
│   │   │   │   │           ├── requiredGuardians
│   │   │   │   │           │   ├── description <string>  (1/3)
│   │   │   │   │           │   ├── entity ‹val›  (1/3)
│   │   │   │   │           │   └── type <string>
│   │   │   │   │           ├── secretReconstitution <string>
│   │   │   │   │           └── type <string>
│   │   │   │   └── args[ ]  (1/32)
│   │   │   │       └── guardianRecovery ‹val›
│   │   │   ├── bugBountyProgram ‹val›
│   │   │   │   └── args[ ]  (27/32)
│   │   │   │       ├── availability <string>  (21/27)
│   │   │   │       ├── coverageBreadth <string>  (21/27)
│   │   │   │       ├── dateStarted <string>  (19/27)
│   │   │   │       ├── disclosure ‹val›  (21/27)
│   │   │   │       │   └── args[ ]  (2/21)
│   │   │   │       │       └── numberOfDays <number>
│   │   │   │       ├── legalProtections ‹val›  (23/27)
│   │   │   │       │   └── args[ ]  (9/23)
│   │   │   │       │       └── type <string>
│   │   │   │       ├── platform <string|null>  (23/27)
│   │   │   │       ├── rewards ‹val›  (23/27)
│   │   │   │       │   └── args[ ]  (16/23)
│   │   │   │       │       ├── currency <string>
│   │   │   │       │       ├── maximum <number>
│   │   │   │       │       └── minimum <number>
│   │   │   │       └── upgradePathAvailable <bool>  (23/27)
│   │   │   ├── duressResistance
│   │   │   │   ├── basicUnlock ⟐cited  (20/32)
│   │   │   │   │   └── mechanisms  (19/20)
│   │   │   │   │       ├── BIOMETRIC <bool>
│   │   │   │   │       ├── PASSWORD <bool>
│   │   │   │   │       ├── PATTERN <bool>
│   │   │   │   │       └── PIN <bool>
│   │   │   │   └── duressMode ‹val›  (22/32)
│   │   │   │       └── args[ ]  (3/22)
│   │   │   │           └── actions  (1/3)
│   │   │   │               ├── DECOY_WALLET <bool>
│   │   │   │               ├── ONCHAIN_LOCKDOWN <bool>
│   │   │   │               ├── SELF_DESTRUCT <bool>
│   │   │   │               └── WIPE_AND_FORWARD <bool>
│   │   │   ├── firmware  (11/32)
│   │   │   │   ├── customFirmware <string|null>  (7/11)
│   │   │   │   ├── details <string>  (3/11)
│   │   │   │   ├── firmwareOpenSource <string>  (7/11)
│   │   │   │   ├── reproducibleBuilds <string>  (7/11)
│   │   │   │   ├── silentUpdateProtection <string|null>  (7/11)
│   │   │   │   ├── type <string>  (7/11)
│   │   │   │   └── url <string>  (2/11)
│   │   │   ├── hardwareWalletSupport ‹val› ⟐cited  (21/32)
│   │   │   │   ├── BROWSER ⟐cited  (1/21)
│   │   │   │   │   └── wallets
│   │   │   │   │       ├── GRIDPLUS ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       ├── IMKEY ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       ├── KEYSTONE ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       ├── LEDGER ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       ├── ONEKEY ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       └── TREZOR ‹val›
│   │   │   │   │           └── args[ ]
│   │   │   │   │               └── connectionTypes
│   │   │   │   ├── DESKTOP ⟐cited  (1/21)
│   │   │   │   │   └── wallets
│   │   │   │   │       ├── GRIDPLUS ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       ├── KEYSTONE ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       ├── LEDGER ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       ├── OTHER ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       └── TREZOR ‹val›
│   │   │   │   │           └── args[ ]
│   │   │   │   │               └── connectionTypes
│   │   │   │   ├── MOBILE ⟐cited  (2/21)
│   │   │   │   │   └── wallets  (1/2)
│   │   │   │   │       ├── IMKEY ‹val›
│   │   │   │   │       │   └── args[ ]
│   │   │   │   │       │       └── connectionTypes
│   │   │   │   │       └── KEYSTONE ‹val›
│   │   │   │   │           └── args[ ]
│   │   │   │   │               └── connectionTypes
│   │   │   │   ├── wallets  (17/21)
│   │   │   │   │   ├── BITBOX ‹val›  (1/17)
│   │   │   │   │   │   └── args[ ]
│   │   │   │   │   │       └── connectionTypes
│   │   │   │   │   ├── GRIDPLUS ‹val›  (6/17)
│   │   │   │   │   │   └── args[ ]
│   │   │   │   │   │       └── connectionTypes
│   │   │   │   │   ├── KEYSTONE ‹val›  (8/17)
│   │   │   │   │   │   └── args[ ]  (7/8)
│   │   │   │   │   │       └── connectionTypes
│   │   │   │   │   ├── LEDGER ‹val›  (9/17)
│   │   │   │   │   │   └── args[ ]
│   │   │   │   │   │       └── connectionTypes
│   │   │   │   │   ├── ONEKEY ‹val›  (1/17)
│   │   │   │   │   │   └── args[ ]
│   │   │   │   │   │       └── connectionTypes
│   │   │   │   │   ├── OTHER ‹val›  (1/17)
│   │   │   │   │   │   └── args[ ]
│   │   │   │   │   │       └── connectionTypes
│   │   │   │   │   └── TREZOR ‹val›  (7/17)
│   │   │   │   │       └── args[ ]
│   │   │   │   │           └── connectionTypes
│   │   │   │   └── args[ ]  (2/21)
│   │   │   ├── keysHandling ⟐cited
│   │   │   │   ├── keyGeneration <string>  (10/32)
│   │   │   │   └── multipartyKeyReconstruction <string>  (10/32)
│   │   │   ├── lightClient
│   │   │   │   └── ethereumL1 ‹val›
│   │   │   │       └── args[ ]  (10/32)
│   │   │   ├── passkeyVerification ‹val›  (21/32)
│   │   │   │   └── args[ ]  (6/21)
│   │   │   │       ├── details <string>  (4/6)
│   │   │   │       ├── library <string>  (4/6)
│   │   │   │       └── libraryUrl <string>  (4/6)
│   │   │   ├── publicSecurityAudits
│   │   │   │   ├── auditDate <string>
│   │   │   │   ├── auditor ‹val›  (37/43)
│   │   │   │   ├── codeSnapshot  (29/43)
│   │   │   │   │   ├── commit <string>  (13/29)
│   │   │   │   │   ├── date <string>  (19/29)
│   │   │   │   │   └── tag <string>  (3/29)
│   │   │   │   ├── unpatchedFlaws
│   │   │   │   │   ├── name <string>
│   │   │   │   │   ├── presentStatus <string>
│   │   │   │   │   └── severityAtAuditPublication <string>
│   │   │   │   └── variantsScope
│   │   │   │       ├── BROWSER <bool>  (2/43)
│   │   │   │       ├── DESKTOP <bool>  (1/43)
│   │   │   │       ├── HARDWARE <bool>  (4/43)
│   │   │   │       └── MOBILE <bool>  (9/43)
│   │   │   ├── scamAlerts  (21/32)
│   │   │   │   ├── contractTransactionWarning ‹val›
│   │   │   │   │   └── args[ ]  (19/21)
│   │   │   │   │       ├── contractRegistry <bool|null>  (14/19)
│   │   │   │   │       ├── leaksContractAddress <bool>  (9/19)
│   │   │   │   │       ├── leaksUserAddress <bool>  (9/19)
│   │   │   │   │       ├── leaksUserIp <bool>  (9/19)
│   │   │   │   │       ├── previousContractInteractionWarning <bool|null>  (14/19)
│   │   │   │   │       └── recentContractWarning <bool|null>  (14/19)
│   │   │   │   ├── scamUrlWarning ‹val›
│   │   │   │   │   └── args[ ]  (17/21)
│   │   │   │   │       ├── leaksDomain <bool>  (2/17)
│   │   │   │   │       ├── leaksIp <bool|null>  (7/17)
│   │   │   │   │       ├── leaksUserAddress <bool|null>  (7/17)
│   │   │   │   │       ├── leaksUserIp <bool|null>  (2/17)
│   │   │   │   │       └── leaksVisitedUrl <string|null>  (7/17)
│   │   │   │   └── sendTransactionWarning ‹val›
│   │   │   │       └── args[ ]  (19/21)
│   │   │   │           ├── leaksRecipient <bool>  (8/19)
│   │   │   │           ├── leaksUserAddress <bool>  (8/19)
│   │   │   │           ├── leaksUserIp <bool>  (8/19)
│   │   │   │           ├── newRecipientWarning <bool|null>  (15/19)
│   │   │   │           └── userWhitelist <bool|null>  (15/19)
│   │   │   ├── secureElement ‹val›  (11/32)
│   │   │   │   └── args[ ]  (8/11)
│   │   │   │       └── secureElementType <string>
│   │   │   ├── securityBestPractices
│   │   │   │   ├── browser ⟐cited  (2/32)
│   │   │   │   │   ├── browserExtensionHardening ‹val›
│   │   │   │   │   │   └── args[ ]
│   │   │   │   │   ├── keyStorageMechanism <string>
│   │   │   │   │   └── secureRng <string>
│   │   │   │   ├── desktop <string>  (2/32)
│   │   │   │   └── mobile ⟐cited  (2/32)
│   │   │   │       ├── keyStorageMechanism <string>  (1/2)
│   │   │   │       ├── mobileAppHardening ‹val›  (1/2)
│   │   │   │       │   └── args[ ]
│   │   │   │       └── secureRng <string>  (1/2)
│   │   │   ├── supplyChainDIY  (11/32)
│   │   │   │   ├── componentSourcingComplexity <string>  (1/11)
│   │   │   │   ├── details <string>  (1/11)
│   │   │   │   ├── diyNoNda <string>  (1/11)
│   │   │   │   ├── type <string>  (1/11)
│   │   │   │   └── url <string>  (1/11)
│   │   │   ├── supplyChainFactory  (11/32)
│   │   │   │   ├── details <string>  (1/11)
│   │   │   │   ├── factoryOpsecAudit <string>  (1/11)
│   │   │   │   ├── factoryOpsecDocs <string>  (1/11)
│   │   │   │   ├── genuineCheck <string>  (1/11)
│   │   │   │   ├── hardwareVerification <string>  (1/11)
│   │   │   │   ├── tamperEvidence <string>  (1/11)
│   │   │   │   ├── tamperResistance <string>  (1/11)
│   │   │   │   ├── type <string>  (1/11)
│   │   │   │   └── url <string>  (1/11)
│   │   │   ├── transactionLegibility ⟐cited
│   │   │   │   ├── dataExtraction ‹val›  (11/32)
│   │   │   │   │   ├── EYES <bool>  (9/11)
│   │   │   │   │   ├── HASHES <bool>  (9/11)
│   │   │   │   │   └── QRCODE <bool>  (9/11)
│   │   │   │   ├── detailsDisplayed ‹val›  (11/32)
│   │   │   │   │   ├── $spread:displaysFullTransactionDetails ‹val›  (4/11)
│   │   │   │   │   ├── chain <string>  (6/11)
│   │   │   │   │   ├── from <string>  (4/11)
│   │   │   │   │   ├── gas <string>  (4/11)
│   │   │   │   │   ├── nonce <string>  (8/11)
│   │   │   │   │   ├── to <string>  (4/11)
│   │   │   │   │   └── value <string>  (4/11)
│   │   │   │   ├── erc7730 ‹val›  (26/32)
│   │   │   │   │   └── args[ ]  (7/26)
│   │   │   │   │       ├── AAVE_SUPPLY
│   │   │   │   │       │   └── decoded <string>  (4/7)
│   │   │   │   │       ├── AAVE_USDC_APPROVE_SUPPLY_BATCH_NESTED_MULTISEND
│   │   │   │   │       │   └── decoded <string>  (1/7)
│   │   │   │   │       ├── SAFEWALLET_AAVE_SUPPLY_NESTED
│   │   │   │   │       │   └── decoded <string>  (4/7)
│   │   │   │   │       ├── SAFEWALLET_AAVE_USDC_APPROVE_SUPPLY_BATCH_NESTED_MULTISEND
│   │   │   │   │       │   └── decoded <string>  (4/7)
│   │   │   │   │       └── USDC_APPROVAL
│   │   │   │   │           └── decoded <string>  (4/7)
│   │   │   │   ├── erc8213 ‹val›  (26/32)
│   │   │   │   │   └── args[ ]  (8/26)
│   │   │   │   │       ├── calldataDisplay
│   │   │   │   │       │   ├── CALLDATA_DIGEST <string>  (7/8)
│   │   │   │   │       │   ├── COPY_HEX_TO_CLIPBOARD <string>  (7/8)
│   │   │   │   │       │   ├── FORMATTED <string>  (7/8)
│   │   │   │   │       │   └── RAW_HEX <string>  (7/8)
│   │   │   │   │       └── messageSigningLegibility
│   │   │   │   │           ├── DOMAIN_HASH <string>  (7/8)
│   │   │   │   │           ├── EIP712_DIGEST <string>  (7/8)
│   │   │   │   │           ├── EIP712_STRUCT <string>  (7/8)
│   │   │   │   │           └── MESSAGE_HASH <string>  (7/8)
│   │   │   │   ├── transactionDetailsDisplay ‹val›  (20/32)
│   │   │   │   │   ├── chain <string>  (9/20)
│   │   │   │   │   ├── contractInteraction <null>  (1/20)
│   │   │   │   │   ├── erc20Approve <null>  (1/20)
│   │   │   │   │   ├── erc20Transfer <null>  (1/20)
│   │   │   │   │   ├── from <string>  (9/20)
│   │   │   │   │   ├── gas <string>  (9/20)
│   │   │   │   │   ├── nftMint <null>  (1/20)
│   │   │   │   │   ├── nftTransfer <null>  (1/20)
│   │   │   │   │   ├── nonce <string|null>  (9/20)
│   │   │   │   │   ├── rawMessageSigning <null>  (1/20)
│   │   │   │   │   ├── to <string>  (9/20)
│   │   │   │   │   ├── value <string>  (9/20)
│   │   │   │   │   └── args[ ]  (3/20)
│   │   │   │   │       ├── calldata <string>  (2/3)
│   │   │   │   │       ├── chain <null>  (1/3)
│   │   │   │   │       ├── from <null>  (2/3)
│   │   │   │   │       ├── gas <null>  (1/3)
│   │   │   │   │       ├── nonce <null>  (1/3)
│   │   │   │   │       ├── to <null>  (2/3)
│   │   │   │   │       └── value <null>  (2/3)
│   │   │   │   ├── transactionRiskDetection <null>  (1/32)
│   │   │   │   └── transactionSimulations ‹val›  (21/32)
│   │   │   │       └── args[ ]
│   │   │   │           ├── AAVE_SUPPLY  (13/21)
│   │   │   │           │   └── transactionOutcome <string>  (4/13)
│   │   │   │           ├── AAVE_USDC_APPROVE_SUPPLY_BATCH_NESTED_MULTISEND  (12/21)
│   │   │   │           │   └── transactionOutcome <string>  (1/12)
│   │   │   │           ├── ERC_1155_TRANSFER  (13/21)
│   │   │   │           │   └── transactionOutcome <string>  (4/13)
│   │   │   │           ├── ERC_20_TRANSFER  (13/21)
│   │   │   │           │   └── transactionOutcome <string>  (11/13)
│   │   │   │           ├── ERC_721_TRANSFER  (13/21)
│   │   │   │           │   └── transactionOutcome <string>  (9/13)
│   │   │   │           ├── ETH_TRANSFER  (13/21)
│   │   │   │           │   └── transactionOutcome <string>  (8/13)
│   │   │   │           ├── FAILED_TRANSACTION  (12/21)
│   │   │   │           │   ├── failure <string>  (5/12)
│   │   │   │           │   └── transactionOutcome <string>  (1/12)
│   │   │   │           ├── insights <string>  (3/21)
│   │   │   │           ├── NONDETERMINISTIC_TRANSACTION  (12/21)
│   │   │   │           │   └── nondeterminism <string>  (4/12)
│   │   │   │           ├── SAFEWALLET_AAVE_SUPPLY_NESTED  (13/21)
│   │   │   │           │   └── transactionOutcome <string>  (4/13)
│   │   │   │           ├── SAFEWALLET_AAVE_USDC_APPROVE_SUPPLY_BATCH_NESTED_MULTISEND  (13/21)
│   │   │   │           │   └── transactionOutcome <string>  (4/13)
│   │   │   │           ├── USDC_APPROVAL  (13/21)
│   │   │   │           │   └── transactionOutcome <string>  (11/13)
│   │   │   │           └── ZKSYNC_USDC_TRANSFER  (12/21)
│   │   │   │               └── transactionOutcome <string>  (1/12)
│   │   │   └── userSafety <null>  (11/32)
│   │   ├── selfSovereignty
│   │   │   ├── interoperability  (11/32)
│   │   │   │   ├── details <string>  (2/11)
│   │   │   │   ├── interoperability <string>  (2/11)
│   │   │   │   ├── noSupplierLinkage <string>  (2/11)
│   │   │   │   ├── type <string>  (2/11)
│   │   │   │   └── url <string>  (2/11)
│   │   │   ├── permissionsManagement ‹val› ⟐cited  (21/32)
│   │   │   │   ├── BROWSER ‹val›  (1/21)
│   │   │   │   │   └── args[ ]
│   │   │   │   │       ├── erc1155Approvals <string>
│   │   │   │   │       ├── erc20Approvals <string>
│   │   │   │   │       └── erc721Approvals <string>
│   │   │   │   ├── canRevokeApprovals ‹val›  (1/21)
│   │   │   │   ├── DESKTOP <null>  (1/21)
│   │   │   │   ├── inWalletApprovalManagement ‹val›  (1/21)
│   │   │   │   ├── MOBILE <null>  (1/21)
│   │   │   │   └── args[ ]  (16/21)
│   │   │   │       ├── erc1155Approvals <string|null>  (5/16)
│   │   │   │       ├── erc20Approvals <string|null>  (5/16)
│   │   │   │       └── erc721Approvals <string|null>  (5/16)
│   │   │   └── transactionSubmission  (21/32)
│   │   │       ├── l1 ⟐cited
│   │   │       │   ├── selfBroadcastViaDirectGossip ‹val›
│   │   │       │   └── selfBroadcastViaSelfHostedNode ‹val›
│   │   │       │       └── args[ ]  (7/21)
│   │   │       └── l2 ⟐cited
│   │   │           ├── arbitrum <string|null>
│   │   │           └── opStack <string|null>
│   │   └── transparency
│   │       ├── maintenance <null>  (11/32)
│   │       ├── operationFees
│   │       │   ├── builtInErc20Swap ‹val›  (8/32)
│   │       │   │   └── args[ ]  (7/8)
│   │       │   │       ├── afterSingleAction <string>  (4/7)
│   │       │   │       ├── byDefault <string>  (4/7)
│   │       │   │       └── fullySponsored <string|bool>  (4/7)
│   │       │   ├── erc20L1Transfer ‹val›  (8/32)
│   │       │   │   └── args[ ]  (7/8)
│   │       │   │       ├── afterSingleAction <string>  (3/7)
│   │       │   │       ├── byDefault <string>  (3/7)
│   │       │   │       └── fullySponsored <string|bool>  (3/7)
│   │       │   ├── ethL1Transfer ‹val›  (8/32)
│   │       │   │   └── args[ ]  (7/8)
│   │       │   │       ├── afterSingleAction <string>  (3/7)
│   │       │   │       ├── byDefault <string>  (3/7)
│   │       │   │       └── fullySponsored <string|bool>  (3/7)
│   │       │   └── uniswapUSDCToEtherSwap ‹val›  (8/32)
│   │       │       └── args[ ]  (6/8)
│   │       │           ├── afterSingleAction <string>  (2/6)
│   │       │           ├── byDefault <string>  (2/6)
│   │       │           └── fullySponsored <string|bool>  (2/6)
│   │       ├── releaseTransparency
│   │       │   ├── artifactSigning ‹val›
│   │       │   │   └── args[ ]  (21/32)
│   │       │   │       ├── publication <string>  (2/21)
│   │       │   │       └── signer <string>  (2/21)
│   │       │   ├── dependencyLocking ‹val›
│   │       │   │   └── args[ ]  (7/32)
│   │       │   ├── dependencyVulnerabilityScanning ‹val›
│   │       │   ├── hasPublicChangelog ‹val›
│   │       │   │   └── args[ ]  (21/32)
│   │       │   ├── hermeticBuilds ‹val›
│   │       │   │   └── args[ ]  (1/32)
│   │       │   ├── repositoryChangeControls <null>
│   │       │   └── reproducibleBuilds ‹val› ⟐cited
│   │       │       ├── notes <string>  (1/32)
│   │       │       ├── scope  (1/32)
│   │       │       │   ├── ANDROID <bool>
│   │       │       │   └── IOS <null>
│   │       │       ├── status <string>  (1/32)
│   │       │       └── args[ ]  (20/32)
│   │       └── reputation <null>  (11/32)
│   ├── metadata ‹val›
│   │   ├── blurb <string>  (31/32)
│   │   ├── contributors  (31/32)
│   │   ├── displayName <string>  (31/32)
│   │   ├── hardwareWalletManufactureType <string>  (10/32)
│   │   ├── hardwareWalletModels  (10/32)
│   │   │   ├── id <string>
│   │   │   ├── isFlagship <bool>
│   │   │   ├── name <string>
│   │   │   └── url <string>
│   │   ├── iconExtension <string>  (31/32)
│   │   ├── id <string>  (31/32)
│   │   ├── lastUpdated <string>  (31/32)
│   │   ├── pseudonymType  (1/32)
│   │   │   ├── plural <string>
│   │   │   └── singular <string>
│   │   ├── tableName <string>  (31/32)
│   │   └── urls  (31/32)
│   │       ├── androidManifestXml <string>  (1/31)
│   │       ├── docs  (24/31)
│   │       ├── extensions  (12/31)
│   │       ├── iosInfoPlist <string>  (1/31)
│   │       ├── repositories  (25/31)
│   │       ├── socials  (26/31)
│   │       │   ├── discord <string>  (11/26)
│   │       │   ├── facebook <string>  (6/26)
│   │       │   ├── farcaster <string>  (7/26)
│   │       │   ├── instagram <string>  (7/26)
│   │       │   ├── linkedin <string>  (11/26)
│   │       │   ├── reddit <string>  (8/26)
│   │       │   ├── telegram <string>  (5/26)
│   │       │   ├── tiktok <string>  (2/26)
│   │       │   ├── x <string>
│   │       │   └── youtube <string>  (7/26)
│   │       └── websites
│   ├── overrides  (2/32)
│   │   └── attributes
│   │       ├── privacy  (1/2)
│   │       │   └── addressCorrelation
│   │       │       └── note <string>
│   │       └── security  (1/2)
│   │           └── scamPrevention
│   │               └── note <string>
│   └── variants
│       ├── BROWSER <bool>  (14/32)
│       ├── DESKTOP <bool>  (3/32)
│       ├── HARDWARE <bool>  (11/32)
│       └── MOBILE <bool>  (17/32)
├── export <string>
├── id <string>
└── source <string>
```

