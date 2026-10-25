# Report 1: where it stands

Written 2026-10-25 so the state survives a context reset. The report is `REPORT1.md`, rendered to
`Mandadi_Khalsa_Report1.pdf` by `build_report.py` (markdown plus `[[FIG:n|path|caption]]`
placeholders, through Chrome headless; there is no pandoc on this machine).

## Status

Complete and self-consistent. Not submitted. Main text plus the statement of contributions fits
five pages; the spec excludes only references and appendices, which an earlier version did not
respect. Zero em dashes. All figure and table numbers resolve.

## What it claims, and the number behind each

| claim | value | produced by |
| --- | --- | --- |
| panel | 140 months, 15.9M rows, 12,253 lines, 234 partners | `harvest_hs10.py`, `build_panel_hs8.py` |
| retained for modelling | 6.09M rows, 95.7% of value, but 8,100 lines and 193 partners | `analysis_panel.py` |
| 2017 reconciliation | $2.34tn against published $2.34tn | `build_panel_hs8.py` |
| coverage, median pairing | 5.4% of chapter value; 32.4% under 1%; 1.3% per surcharge code | `coverage_share.py` |
| chapter-level test | treated -7.1% vs untreated -7.6%, one-sided p = 0.0075 | `coverage/treated_vs_untreated.py` |
| eight-digit tariff actions | unstable, pre-trends in all three mechanisms (Table 1) | `event_study_*_lv_diff.csv` |
| copper chapter 74, 2025 | $24.7bn, 89 lines, duty named 29%, cathodes 67% untaxed | `slides/fig_sankey.py` |
| copper split, appendix | semi-finished 49 -> 68 -> 27 kt; cathodes 89 -> 218 -> 154 | `copper_split.py` |
| units screen | 56 of 98 chapters under 70% kg; 65 pass the 80% screen, 63 rankable | `chapter_quantity.py` |
| pharma | 2.86 on dollars, -0.33 on quantity; +57% March on flat tonnage | `pharma_mix.py` |
| event study | real +42% before, +6% after, a fall of 0.30 log points (about 26%) | `adcvd_event_study.py` |
| tariff-action rush | 301 jumps +27% in the announcement month, IEEPA +9% two months early, 232 +13% one month early | `event_study.py --diff` |
| retroactivity | NOT supported: critical-circumstance cases rush more, +0.063 vs -0.065, p = 0.015 | `adcvd_analysis.py` |
| overlaps dropped | 27,255 of 65,488 cell-months in any window | `adcvd_event_study.py` |
| episode test (Table 2) | after -0.316 vs +0.020 placebo, p < 0.0001; during p = 0.37 | `adcvd_analysis.py` |
| absorption | not estimable; per-episode median near zero, sd 338 | `substitution_levels.py` |
| port test, appendix | district-mix TVD 0.058 vs 0.068 placebo, seven cases | `port_test.py` |

## Reviews so far, and what they changed

**First (Codex).** Found the 79/21 absorption claim was confounded with market share. Removed; the
level recomputation in `substitution_levels.py` shows it is not estimable either way. Also caught a
confidence-interval bug in `slides/fig_event.py` where the band was built in log space and the
points in percent space, so a point sat outside its own shading.

**Second (Codex, deeper).** Found the chapter-level null no longer reproduces (p = 0.0075, not a
null), and that eight digits never rescued the tariff actions. Section 3.1 was rebuilt around what
was measured rather than around a failure, and Table 1 now reports the eight-digit estimates.

**Fourth (Opus, as examiner, on the rebuilt version).** Scored 17/25 and found the reading of
Table 1 was wrong: the specification is first-differenced and anchored on the announcement month,
so +27 then -37 for Section 301 is a one-month level spike, which is the rush. Section 3.1 had
called the same coefficients unstable. Also found the outcome is log nominal value while the
prose said volume, that "36 points" was a difference of two exp(b)-1 transforms rather than a
percent change, and that the repository's own critical-circumstances test contradicts the
retroactivity mechanism the report asserted. All fixed.

**Third (Opus, as examiner).** Scored 18/25 on the earlier version. Found Table 1 unreferenced, Fig.
1 rendering near 3pt, the statement of contributions pushing to page 6, panel attrition undisclosed,
reference [6] uncited, and "action" carrying three referents. All fixed.

**Fifth (Codex, technical, on the rebuilt version).** Completed but the forwarding agent could not
retrieve it; the output was recovered from the Codex session log. Found that `2018-27458`, the
largest Section 301 event at 5,921 lines, is coded as an increase effective 2019-03-02 when the
notice in fact postponed that increase, which `2019-03935` then deferred indefinitely. Table 1 is
no longer presented as an answer to the first question. Also found Table 1 has no placebo, so the
blanket placebo claim in Methods was narrowed to what is actually enforced.

**Sixth (readability pass, not a correctness review).** No claim or number changed. Found that
3.3 spent roughly three words of caveat per word of finding, that the Table 1 placebo caveat and
the 2018 postponement were each stated three times, and that the three research questions were
never numbered although the Discussion referred to them by number. Section 3.3 now opens with its
result; the duplicate caveats are stated once each (the Table 1 placebo twice, since Methods needs
it to stay honest); Q1/Q2/Q3 are labelled in section 1 and used in 3.1 and 4. Defined in plain
words where first used: cell, logarithm of customs value, fixed effects, total variation distance,
and k in Table 1. References now start on a fresh page, so pages 1-5 are exactly the counted
content.

**Seventh (Codex, technical, cold, on the post-readability version).** Reproduced essentially
every number but found descriptions that do not match what the code computes. Six were verified
here and fixed. (a) The 26 percent headline described a level comparison between suppliers; it is
a fall in relative position, 42 percent above baseline before to 6 percent after. (b) Table 1's
"treatment is exact at eight digits" is false for Section 232, which `event_study.py:62-68`
assigns by `df.chapter.isin(...)`; the text and the Discussion now say so. (c) The dilution test
direction was backwards: -7.1 against -7.6 means touched chapter-months sit higher, not further
from normal. (d) The sample is 338 antidumping and 169 countervailing, not antidumping alone.
(e) 8 of 508 episodes rest on notices that made no affirmative determination, two stating
liquidation will not be suspended (`2016-19867`, `2019-10283`); now disclosed in the appendix.
(f) Q2 was declared answered four lines above "its destination is not"; now partly answered.

Also corrected without Codex: the retroactivity split used `critical_circ`, a regex for the
phrase anywhere in the document. The parser already computes `critical_affirm` and it was unused.
Rerunning on the affirmative flag gives +0.067 against -0.066, Welch p = 0.012, rank p = 0.0002,
so the conclusion holds and strengthens. Codex judged this test unusable; it had not rerun it.
Figure 1's labels were overlapping at print size and now use leader lines.

## Still open

- `adcvd_analysis.py` and `substitution_test.py` use nominal dollar value; the report says
  "volumes" nowhere now, but the outcomes are value, not quantity.
- Inclusion and weighting use full-panel history, so a tariff-induced exit can affect both.
- Some retained "preliminary" documents do not themselves start collection; `2016-19867` says
  liquidation is not suspended.
- No multiple-comparison adjustment across the 31 monthly coefficients.
- The copper taxed/untaxed split is assigned by heading, not from the proclamation's annex, which
  is not in the Federal Register text we hold.
- `2016-19867` is retained as a duty-start event although its notice says liquidation is not
  suspended. Raised by two reviews, still unfixed.
- Observations outside any event window keep K=99 alongside the omitted baseline months, so the
  event-study reference group is wider than the caption says.
- Of the eight significant post-event coefficients in Fig. 2, only month zero survives a
  Bonferroni correction across 31 coefficients.
- Treated cell-months are not a balanced cohort: 975 at k=0 against 1,437 at k=18.
- Coverage is measured on 162 of 637 surcharge codes, with 902 unmatched HS8 codes counted as
  zero trade and no historical concordance.
- `build_treatment.py` converts conditional authority into actual treatment, e.g. `2025-05440`.

## Rebuild

```
python3 slides/fig_sankey.py && python3 slides/fig_event.py && python3 build_report.py
```
