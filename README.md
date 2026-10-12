# tariff-rush

**Borrowed or Real: Forecasting Import Surges Around U.S. Tariffs**

Rahul Reddy Mandadi, Raunaksingh Khalsa
DS 5500 Data Science Capstone, Northeastern University, Fall 2026

## The problem

When a U.S. tariff is announced with a start date, importers rush goods in before the deadline,
and imports then fall below normal afterward. Ports, trucking and warehousing firms, lenders and
forecasters see only total volume. They can't tell a timing effect from real growth or real
decline, so they over-hire, overbuy capacity or misjudge demand.

On the day a tariff is announced, using only information available that day, we predict for each
product × country:

1. **Will it rush at all?** Classification, the first step of a hurdle model.
2. **How big is the rush, month by month until the deadline?** Multi-horizon regression with
   prediction ranges.
3. **What comes after the deadline?** The monthly path below normal, and whether the shortfall is
   temporary payback (stockpiles being used up) or a lasting drop (the tariff reduced demand).

Every target is a deviation from a counterfactual "normal": what imports would have been without
the tariff, forecast from pre-announcement trend and seasonality.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export CENSUS_API_KEY=...        # free: https://api.census.gov/data/key_signup.html

python src/harvest.py            # Census API -> data/raw/census_hs2/
python src/assemble.py           # -> data/interim/imports_hs2_panel.csv
python src/decomp.py             # -> data/interim/anomalies_kg.csv
```

`harvest.py` makes one API call per month and caches each one, so an interrupted run picks up
where it stopped. It ends at the first month Census has not published yet.

## Layout

```
src/
  paths.py       repo paths shared by every step
  harvest.py     monthly HS2 x partner imports from the Census API, 2015 onward
  assemble.py    flatten raw months into a tidy panel, with sanity checks
  decomp.py      provisional counterfactual baseline and anomalies
data/
  raw/           cached API responses (not tracked)
  interim/       tidy tables built from raw (not tracked)
  reference/     hand-curated tables such as the tariff event table (planned, tracked)
```

The panel has one row per month × HS2 chapter × partner country: `year`, `month`, `cty_code`,
`cty_name`, `chapter`, `value_usd` (general imports), `air_kg`, `ves_kg` and `cnt_kg`
(containerized, a subset of vessel). `assemble.py` keeps single-country rows only, dropping
country groupings and the all-countries total.

## Data sources

| Source | Role | Level |
| --- | --- | --- |
| [Census international trade API](https://api.census.gov/data/timeseries/intltrade/imports/hs) | Outcome: monthly imports | HS2/4/6/10 × country |
| [Global Trade Alert](https://globaltradealert.org) | Tariff events: announcement date, effective date, HS codes | HS codes |
| [WTO–IMF Tariff Tracker](https://ttd.wto.org) | Cross-check of tariff changes and dates | HS chapter × partner |
| BTS TransBorder Freight Data | Canada/Mexico truck and rail imports, with weight | HS2 only |
| IMF PortWatch | Daily port calls, for rush timing within a month (later phase) | port × day |

Notes on the Census data:

- **Volume is measured in weight** (air + vessel kg), not dollars, because prices move with tariffs.
- **Census only reports weight for air and vessel shipments.** Land shipments from Canada and
  Mexico have none, which is what TransBorder is for.
- **Monthly data comes out about five weeks after month end**, and later after government
  shutdowns. That lag is why we forecast on announcement day.
- **Census revises past months**, so the download date of each pull matters.

## Method

**Baseline.** `decomp.py` fits a robust STL decomposition to log weight, using only data up to the
cutoff. It extrapolates the trend from its slope over the last 36 months and adds a seasonal
profile averaged over the last three cycles. The anomaly is actual ÷ counterfactual − 1. The band
is ±1.96 standard deviations of the pre-period residuals.

The cutoff is currently fixed at 2024-12 for every series. Fitting each series up to its own
event's announcement date needs the tariff event table.

**Rules for the model:**

- **No look-ahead.** Every feature must be known on announcement day.
- **Rushes can start before the announcement.** Aluminum was +12% in January 2025, before the
  February 10 announcement. Anticipation is measured, not assumed away.
- **We don't predict whether a tariff survives.** Durability clues known on the day (legal
  authority, pending court cases) are features, and results are reported separately for tariffs
  that lasted and tariffs that were removed.
- **Validation holds out whole tariff events**, because products hit by the same announcement
  are correlated. We also train on 2018–2024 events and test on 2025–26.

## Status

Week 1 of 10: data collection.

- **Done:** the pull → panel → baseline pipeline. A full HS2 pull (2015-01 to 2026-07) was run
  with the earlier flat-script layout. The current `src/` scripts produce identical output on
  synthetic data but have not yet been rerun against the live API.
- **Not yet verified:** the aluminum (HS 76) figures from the pitch. These are +12.7% in Jan 2025,
  +45.2% in Feb and +48.8% in Mar, then eight months below normal. They come from `decomp.py` at
  commit `e9db4d6` (`git show e9db4d6:anomalies_kg.csv`) and have not been checked independently.

Next:

- Pull `CON_VAL_MO`, `DUT_VAL_MO` and `CAL_DUT_MO` to get the effective duty rate
  (`CAL_DUT_MO / CON_VAL_MO`), and check it jumps for aluminum in Mar and Jun 2025.
- Record the download date of each month's pull.
- Confirm `(month, chapter, cty_code)` is unique, since Census can split rows by district or rate
  provision.
- Add a validation script: missing months, monthly totals against the FT-900 release, and aluminum
  against a simple same-month three-year average.
- Build the tariff event table in `data/reference/`, with a source for every date. Then do the
  HS4 pull and TransBorder.
