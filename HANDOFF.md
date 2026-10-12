# What is already built

Orientation for a new contributor. Written 2026-10-12.

The project forecasts, on the day a tariff is announced, whether the months after the effective
date are temporary payback of volume borrowed before it or a durable drop in demand. Two
supporting quantities feed that: whether a surge happens at all, and how big it is.

## The two halves

The work so far splits into an **import panel** half (complete, on main) and a **tariff event**
half (draft, not yet pushed). They have never been joined. Joining them is the next job and
everything downstream waits on it.

## Half 1: the import panel (on main)

```
harvest.py   -> panel/raw/YYYY-MM.json.gz   one Census API call per month, checkpointed
assemble.py  -> panel/imports_hs2_panel.csv tidy panel, 1,035,855 rows
decomp.py    -> panel/anomalies_kg.csv      STL counterfactual, 6 chapters
surges.py    -> panel/surge_events.csv      11,178 surge episodes with reversal ratios
```

`harvest.py` reads a Census API key from the `CK` environment variable. The panel covers 139
months (2015-01 to 2026-07), 98 HS2 chapters, 234 partners, with value in dollars and weight
split into air, vessel and containerized. It is about 47 MB and is not tracked; rebuild it with
`harvest.py` then `assemble.py`. The two derived CSVs are tracked.

### Important: there are two different baselines

This trips people up. The project uses two distinct notions of "normal" and they are not
interchangeable.

**`decomp.py` uses a fitted counterfactual.** Robust STL on log volume, fit only on data before
2024-12, trend extrapolated from its last 36 months, seasonal profile averaged over three cycles.
The tolerance band is 1.96 pre-period residual standard deviations. This produced the headline
aluminum result: +48.8 percent in March 2025 against a band of plus or minus 18 percent, eight
consecutive months below afterwards, year closing at +0.7 percent. It also produced the
six-chapter comparison where only aluminum and steel articles clear their bands.

**`surges.py` uses a rolling trailing baseline.** Expected value at month t is a trailing
12-month geometric mean times a month-of-year factor estimated only from months strictly before t.
A surge episode is a contiguous run above 0.5 SD that peaks above 2.0 SD. The reversal ratio is
the cumulative excess over the 9 months after the episode divided by the excess during it. This
produced the 11,178 episodes across 5,007 cells and the 52 / 35 / 13 split into real growth,
borrowed, and in between.

Both are leak-free. The rolling baseline is the practical choice for scanning thousands of cells,
the fitted counterfactual is the better choice for a single known event. **The proposal describes
the STL procedure and then quotes the surge thresholds from `surges.py` as though they were one
method.** They are not. Reconciling them, or stating clearly which is used where, is an open task.

## Half 2: the tariff event table (built, not yet pushed)

```
events/harvest_fr.py         -> events/fr_index.json   Federal Register search, 2,792 documents
events/fetch_text.py         -> events/raw/*.txt       full text cache, 2,792 files, 454 MB
events/build_event_table.py  -> events/tariff_events.csv and tariff_events_rejected.csv
```

Of 2,792 Federal Register documents from 2018 onward, 134 are kept as tariff actions and 2,658
are rejected with a stated reason. The script asserts those add up, so nothing is dropped
silently. The rejects are mostly trade remedy cases, proposed rules, exclusion grants and
regulatory agendas.

Of the 134, 68 are scope changes that modify an existing action rather than creating a new one.
That leaves **66 genuine tariff actions**: 47 Section 232, 30 Section 301, 27 IEEPA, 28 with
authority not yet resolved.

The 27 IEEPA events matter more than their count suggests. Those are the tariffs later struck down
and refunded, which means a dip after one of them cannot be the duty suppressing demand. They are
the comparison group the whole payback argument rests on.

## Known problems, in priority order

**1. The join keys are broken. This blocks everything.**

`hs_chapters` is frequently just `99`. Chapter 99 is where tariff surcharges live, not where
products live, so a code like 9903.85.03 says a surcharge exists but not what it sits on. The
covered product codes are in the document annexes. Only 76 of 134 rows carry any chapter at all.

`partners` is incoherent. A real value reads
`Argentina;Australia;Brazil;Canada;EXCEPT:Argentina;...` because the parser collected country
names instead of parsing an include set and an exception set separately.

Until both are fixed there is no treatment indicator, and without a treatment indicator there is
no supervised learning problem.

**2. Documents are not deduplicated into events.** One action often produces a proclamation plus
an implementing notice. 134 documents is not 134 events, and the distinct count is what justifies
choosing regularized models over gradient-boosted trees.

**3. Field coverage is thin.** `rate_pct` is filled on 26 percent of rows, `effective_date` on 69
percent, and 41 rows are flagged low confidence.

**4. Path bug.** `harvest.py`, `assemble.py`, `decomp.py` and `surges.py` all expect a `panel/`
subdirectory, but the committed CSVs sit at the repository root. Anything cloned fresh will fail
on this.

**5. The land-mode gap is open.** Census shipping weight covers air and vessel only. For aluminum
in 2024 that leaves about 69 percent of Canadian and 97 percent of Mexican tonnage unobserved, and
those two partners are 48 percent of aluminum import value. BTS TransBorder closes it and is not
yet integrated.

## Where to start

1. Resolve 9903 codes to covered product chapters. The USITC HTS API serves Chapter 99, and the
   Federal Register annexes list coverage directly.
2. Rewrite partner extraction as include set minus exception set.
3. Deduplicate documents into distinct events.
4. Build the coverage map: one row per event, chapter and partner, flagged treated or not.
5. Measure the base rate. For covered cells, how often does a surge actually occur between
   announcement and effective date? That number decides which evaluation metrics apply.

Steps 1 and 2 are the hard dependency. Step 1 has unknown difficulty and is worth attacking first.
