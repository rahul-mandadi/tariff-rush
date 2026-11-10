"""Ordinal aftermath bands for surge episodes.

The reversal ratio is cumulative excess over the H months after an episode divided
by the excess during it. It is continuous and heavy-tailed (sd 1.93, observed range
-14 to +39), so it is unusable as a raw regression target. We bin it into four
ordinal bands at economically meaningful cut points rather than at quantiles:

    < 0.0   nothing came back, imports stayed elevated
    0.0-0.5 less than half came back
    0.5-1.0 more than half came back
    >= 1.0  all of it came back, or more

Above 1.0 the series gave back more than it borrowed, which is demand falling
rather than inventory being worked off. Binary payback labels have nowhere to put
those; the top band does.

Thresholding happens here, at label construction, only because an ordinal model
needs discrete classes. Any collapse to a yes/no for reporting should happen at
decision time, on the predicted distribution, not earlier.
"""
import numpy as np, pandas as pd

CUTS   = [-np.inf, 0.0, 0.5, 1.0, np.inf]
BANDS  = ["kept", "mostly_kept", "mostly_returned", "fully_returned_or_more"]
ORDER  = {b: i for i, b in enumerate(BANDS)}

def assign(reversal):
    """Map a reversal ratio series to ordered categorical bands."""
    return pd.cut(reversal, bins=CUTS, labels=BANDS, right=False, ordered=True)

if __name__ == "__main__":
    e = pd.read_csv("surge_events.csv", parse_dates=["date"])
    e["band"] = assign(e.reversal)
    e["band_ord"] = e.band.map(ORDER)
    e.to_csv("surge_labels.csv", index=False)

    n = len(e)
    print(f"episodes labelled: {n:,}\n")
    print(f"{'band':<24}{'n':>8}{'share':>8}{'median ratio':>14}{'median surge':>14}")
    for b in BANDS:
        s = e[e.band == b]
        print(f"{b:<24}{len(s):>8,}{len(s)/n:>7.0%}"
              f"{s.reversal.median():>+14.2f}{s.excess_ln.median():>14.2f}")

    # Does a bigger surge get paid back more? The accounting argument says it should.
    q = pd.qcut(e.excess_ln, 5, labels=["smallest","small","mid","large","largest"])
    print("\npayback rate by surge size (accounting argument predicts this rises):")
    for lab, s in e.groupby(q, observed=True):
        print(f"  {str(lab):<10} n={len(s):>6,}  median ratio {s.reversal.median():>+6.2f}"
              f"   fully returned or more {(s.band=='fully_returned_or_more').mean():>5.0%}")

    print("\nwritten: surge_labels.csv")
