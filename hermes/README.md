# Hermes Wallet Tracker

Hermes is a report-only competitor tracker for software wallets. It reads the
existing wallet metadata in `data/wallets/*.json`, checks official sources plus
listed official socials, compares them with local source snapshots, and writes a
dated Markdown report.

It never edits wallet JSON files.

## Run

```sh
python3 hermes/hermes.py
```

Defaults:

- State: `hermes/state.json`
- Reports: `reports/hermes/YYYY-MM-DD-wallet-tracking.md`
- Scope: every wallet where `source == "software-wallets"`

Useful development runs:

```sh
python3 hermes/hermes.py --wallet metamask --wallet phantom --wallet rabby
python3 hermes/hermes.py --no-state-write
```

The first run establishes a baseline. Later runs classify changed source pages
as shipped features, roadmap updates, or weak social/marketing signals.

## Weekly Operation

Run Hermes once a week, preferably Monday morning. Review the generated Markdown
report and decide manually whether any finding should update `features.product`
in the wallet dataset.

Dynamic pages or blocked socials are recorded as source check failures rather
than scraped through browser automation.
