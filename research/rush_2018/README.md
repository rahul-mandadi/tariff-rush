# Can published import trends flag a rush before a tariff?

This exploratory study replays the April 3, June 15 and July 10 proposals for the first three 2018 U.S. Section 301 tariff lists on Chinese goods. It uses the products proposed at the time. Final lists would give the analyst information unavailable on announcement day.

| Proposal | Proposed tariff lines | Last available trade month | Whole months between proposal and duty | Duty starts |
|---|---:|---|---|---|
| April 3 | 1,333 | January | May, June | July 6 |
| June 15 | 284 | April | July | August 23 |
| July 10 | 6,031 | May | August | September 24 |

The Census release calendar in the repository supplies the information cutoffs. Trade values come from the current historical series restricted by those cutoffs. Historical first-release values could differ. Product lists come from the [April notice](https://public-inspection.federalregister.gov/2018-07119.pdf), [June notice, Annex C](https://ustr.gov/sites/default/files/enforcement/301Investigations/301FRN.pdf), and [July notice](https://ustr.gov/sites/default/files/enforcement/301Investigations/2018-0026%20China%20FRN%207-10-2018_0.pdf).

## Forecast and comparison

For each proposed Chinese product, calculate import value over the three latest published months divided by value in the same three months a year earlier. Select the highest fifth. A hit is a target-month value more than 25% above the same month a year earlier. A product needs positive imports in both historical denominators. This excludes new or previously inactive trade lines. The quantity check scores the same selection wherever prior and current physical units agree and quantity is usable, counting absence of current trade as zero. Eligible sample sizes therefore differ across measures and target months.

Repeat the exercise one year earlier using the same product lists. For magnitude, compare a last-year forecast with that forecast multiplied by recent growth, measuring total absolute error divided by total actual value. A sensitivity check restricts analysis to products with at least $100,000 of trade in the earlier target month.

A separate comparison pairs each proposed product with the closest eligible Chinese product in its four-digit product group outside all three proposals announced up to that point. Matching uses prior three-month value and recent growth. The maximum size difference is a factor of two and the maximum difference in one plus the growth ratio is a factor of 1.25. Controls may be reused. Chapters 72, 73 and 76 are excluded from matching because other metals tariffs complicate the comparison. Intervals resample matched four-digit product groups 3,000 times. They describe uncertainty within that sample, which contains just three related policy waves. Limited overlap, other policies, mix, and preexisting demand trends constrain interpretation.

## Results

| Target | Eligible products | Dollar jumps across list | Dollar jumps among flagged | Quantity jumps across usable lines | Quantity jumps among usable flagged lines |
|---|---:|---:|---:|---:|---:|
| May | 905 | 39.6% | 48.1% | 37.0% | 39.3% |
| June | 933 | 37.9% | 42.8% | 37.2% | 44.7% |
| July | 234 | 53.4% | 80.9% | 45.4% | 70.5% |
| August | 3,707 | 41.1% | 54.4% | 37.8% | 49.3% |

Prior-year dollar ranking advantages were 8.3, 5.9, 23.2 and 16.2 percentage points. Corresponding 2018 advantages were 8.5, 4.9, 27.5 and 13.3 points. Ordinary momentum predicts jumps outside the announcement year too. The unmatched forecast and the matched comparison answer different questions.

August has the clearest descriptive tariff-specific lead. Among 125 matches, proposed lines had a 23.2-point higher incidence of a value jump (95% interval 10.8 to 34.4). Among 81 quantity matches, the difference was 14.8 points (−2.6 to 28.4). The 125 matches cover only 3.4% of 3,707 eligible proposed lines. The other 2018 matched physical-quantity intervals include zero too. These results cannot identify how much inventory buyers pulled forward or whether any accumulation was followed by payback.

The simple trend forecast of dollar magnitude beat the seasonal baseline in only one of four target months. All results are historical and exploratory. This supports a short section about predictive limits in the capstone. Independent policy episodes, broader credible comparison groups, and finer shipment or inventory data would be needed for a general claim about tariff-driven front-loading.

## Reproduction

Run `python3.13 research/rush_2018/evaluate_rush.py` from the repository root with numpy, pandas, pyarrow, and the project's monthly HS8 parquet panel. The script prints counts, precision, weighted absolute percentage errors, matched gaps and intervals. The recorded run is in `results.txt`.
