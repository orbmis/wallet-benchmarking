# Wallet Benchmark — Feature Ideas

A backlog of potential features for the benchmarking prototype in this directory.
Audience: a **wallet product manager benchmarking against rivals**.

Each idea is tagged with rough **value / effort** and whether it **reuses** scaffolding
that already exists in `build.py` (matrix) or `build_privacy.py` (Sankey).

## Already built

- **Comparison matrix + evidence drawer** — `index.html` (generated from `template.html` by `build.py`).
  Baseline vs. rivals, citation-backed cells, three-state colouring, diff/hide-unknown toggles, CSV export.
- **Privacy data-flow (Sankey)** — `privacy.html` (generated from `template_privacy.html` by `build_privacy.py`).
  Action → Recipient → Data collected, coloured by collection policy and recipient risk.
- **"Strengths & Gaps" report** — `gaps.html` (generated from `template_gaps.html` by `build_gaps.py`).
  Reuses the matrix model via `build.build_payload()`. Per baseline + peer set, auto-derives the metrics
  where ≥1 rival beats you (sorted by how many do) and the metrics where you beat every rival, with an
  evidence drawer, Markdown backlog export, and CSV. Ranks by the same better/worse polarity as the matrix;
  unknowns and descriptive values are excluded.
- **Positioning quadrant** — `quadrant.html` (generated from `template_quadrant.html` by `build_quadrant.py`).
  Reuses the matrix model via `build.build_payload()`. Scores every wallet 0–100 per category (averaging the
  rankable metrics on the matrix's better/worse polarity; counts normalised to their range, unknowns/values
  excluded) and plots them on two chosen category axes — the "magic quadrant" slide. Median or fixed 50/100
  split, baseline highlight, platform filter, decluttered labels, per-wallet score-breakdown drawer, and
  Markdown / CSV export. Wallets with no data on a chosen axis are listed below the chart.
- **Cross-links + first-run help panels** on all four pages.

---

## 1. Decision-oriented views (highest PM value)

- **"Strengths & Gaps" report** — ✅ **Built** (`gaps.html`). See "Already built" above.
- **Third-party exposure graph** — *high / medium · reuses privacy entity-resolver.*
  Force-directed node graph of wallets ↔ shared infra/brokers. Answers "which rivals all depend on
  Pimlico / the same broker?" Natural completion of the privacy work.
- **Weighted custom index + leaderboard** — *high / medium.*
  Let the PM weight categories (privacy-max vs. institutional vs. consumer) and produce a ranked
  leaderboard, so the benchmark can argue a specific thesis.
- **Positioning scatter / quadrant** — ✅ **Built** (`quadrant.html`). See "Already built" above.
- **Per-category radar overlay** — *medium / low.*
  2–3 wallets superimposed on a spider chart — the exec-summary visual.

## 2. Security & audit intelligence

- **Audit & open-flaws dashboard** — *high / low · audit data already parsed in `build.py`.*
  Timeline of who audited whom and when, plus a sortable "unpatched HIGH-severity flaws" tally
  (already computed: e.g. Rabby 3, MetaMask 0).
- **Auditor reuse view** — *medium / low.*
  Via `entities.json` `securityAuditor` flags: which auditors cover which wallets (e.g. SlowMist's footprint).

## 3. Trust & data-quality layer (novel — uses underused data)

- **Conflict-of-interest surfacing** — *high / low · uses `contributors.json` (currently unused).*
  That file records each contributor's `affiliation` and whether they `hasEquity`. Show who authored a
  wallet's entry and flag when a rater has equity in the wallet they rated. Makes the benchmark's own
  credibility legible.
- **Coverage & freshness dashboard** — *medium / low.*
  Per wallet: `lastUpdated`, `refTodo` count, % of cells filled. Flags stale/thin comparisons
  (the matrix is ~62% "unknown" today) and doubles as a maintenance to-do.

## 4. Entity & jurisdiction intelligence

- **Entity profile pages** — *medium / medium.*
  Click an entity (e.g. DeBank) → every wallet it touches, its type, jurisdiction, privacy policy.
  Turns entity `$ref`s into first-class objects.
- **Jurisdiction / data-residency view** — *medium / medium.*
  `entities.json` has `jurisdiction`; map where each wallet's data recipients sit
  (GDPR / data-residency angle for institutional buyers).

## 5. PM workflow glue (cheap, big quality-of-life)

- **Shareable URL state** — *high / low.*
  Encode baseline + rivals + filters in the URL hash so a comparison can be shared as a link
  (e.g. "MetaMask vs Rabby, privacy only"). High utility for a static page; near-trivial.
- **Auto-generated competitive brief** — *high / medium.*
  One button → a Markdown one-pager for a chosen rival pair (wins, losses, privacy summary,
  audit posture), ready to paste into a doc.
- **Cell annotations (localStorage)** — *medium / low.*
  PM adds internal notes per cell ("eng disputes this — verify").
- **Print / PDF one-pager layout** — *low / low.*
  A clean print stylesheet for handouts.

## 6. Feature deep-dives (topical)

- **EIP-7702 / smart-account readiness board** — *medium / low.*
  The account-abstraction data (`eip7702`, `rawErc4337`, `safe`, delegation) is rich and a hot
  competitive topic — worth its own focused screen.

---

## Top picks (best value-per-hour for this persona)

1. ~~**"Strengths & Gaps" report**~~ — ✅ built (`gaps.html`); turned the matrix into a decision to act on.
2. **Shareable URL state** — unlocks sharing.
3. **Conflict-of-interest trust layer** — uses data nothing else touches.

The **third-party exposure graph** is also the natural completion of the privacy view.

---

## Notes for implementers

- Both pages are **generated**: edit `template*.html`, then run the matching `build*.py`; never hand-edit
  `index.html` / `privacy.html` (they are overwritten).
- Output files are **self-contained** (data inlined, no server, no external libs) — keep new features the same.
- Generated files contain multibyte glyphs; use `grep -a` / `rg` when searching them (plain `grep`
  treats them as binary).
- The `$ref` / `$call` DSL resolution lives in `build.py`; the entity resolver (with humanized fallback)
  lives in `build_privacy.py` — reuse these rather than re-walking the raw JSON.
