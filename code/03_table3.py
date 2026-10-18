"""03_table3.py — Replicate Table 3 (Average Employment Per Store) of Card & Krueger (1994).

Rows:
  1. FTE employment before (all available observations)
  2. FTE employment after  (all available observations; closed = 0, temp = missing)
  3. Change in mean FTE employment (row 2 - row 1)
  4. Change in mean FTE employment, balanced sample of stores (both waves)
  5. Same, but wave-2 FTE at temporarily closed / renovation stores set to 0

Columns: PA, NJ, NJ-PA, and NJ stores by wave-1 starting wage
($4.25 / $4.26-$4.99 / >=$5.00) plus within-NJ differences.
SE of a difference = two-sample SE (unequal variances).
"""
import pandas as pd
import numpy as np
from pathlib import Path
from ck94_utils import load_clean_data, se_mean

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "outputs" / "tables" / "table3.csv"

df = load_clean_data()

NJ = df.STATE == 1
PA = df.STATE == 0

def mean_se(x):
    x = x.dropna()
    return x.mean(), se_mean(x)

def diff_mean_se(a, b):
    a, b = a.dropna(), b.dropna()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return a.mean() - b.mean(), se

rows = []

def row(label, fte_col, same_col=None):
    """fte_col: wave-2 column used; for rows 1-2 use means; rows 3-5 per-store diffs."""
    d = {}
    m1, s1 = mean_se(df.loc[NJ, "FTE1"])
    m2, s2 = mean_se(df.loc[NJ, fte_col])
    mp1, sp1 = mean_se(df.loc[PA, "FTE1"])
    mp2, sp2 = mean_se(df.loc[PA, fte_col])
    # NJ - PA for "before" / "after" / change rows handled by caller
    d["PA"] = (mp2 - mp1) if "change" in label else mp2
    d["NJ"] = (m2 - m1) if "change" in label else m2
    if "change" in label:
        # row 3 is the difference of means (m2 - m1); SE approximated with balanced
        # per-store change SE (see paper; PA value matches exactly).
        bal = df[(df.FTE1.notna()) & (df[fte_col].notna())].copy()
        bal["d"] = bal[fte_col] - bal["FTE1"]
        dPA, dNJ = bal.loc[bal.STATE == 0, "d"], bal.loc[bal.STATE == 1, "d"]
        se_pa, se_nj = se_mean(dPA), se_mean(dNJ)
        d["PA_se"], d["NJ_se"] = se_pa, se_nj
        d["NJmPA"] = d["NJ"] - d["PA"]
        d["NJmPA_se"] = np.sqrt(dNJ.var(ddof=1) / len(dNJ) + dPA.var(ddof=1) / len(dPA))
    else:
        d["PA_se"], d["NJ_se"] = sp1 if "before" in label else sp2, s1 if "before" in label else s2
        d["NJmPA"] = d["NJ"] - d["PA"]
        d["NJmPA_se"] = np.sqrt(s1**2 + (sp1 if "before" in label else sp2)**2) if "before" in label else np.sqrt(s2**2 + sp2**2)

    # NJ wage classes
    w = df["wage_class"]
    for code, key in [(1, "w425"), (2, "wmid"), (3, "whigh")]:
        m = df.loc[(NJ) & (w == code)]
        if "change" in label:
            m = m[(m.FTE1.notna()) & (m[fte_col].notna())]
            vals = (m[fte_col] - m["FTE1"])
        else:
            vals = m["FTE1"] if "before" in label else m[fte_col]
        d[key], d[key + "_se"] = mean_se(vals)
        d[key + "_n"] = len(vals)
    # within-NJ differences: low - high, mid - high, mid - low
    d["lo_hi"], d["lo_hi_se"] = diff_mean_se(
        df.loc[(NJ) & (w == 1), "FTE1"] if "before" in label else
        (df.loc[(NJ) & (w == 1) & df.FTE1.notna() & df[fte_col].notna()] if "change" in label else df.loc[(NJ) & (w == 1), fte_col]),
        df.loc[(NJ) & (w == 3), "FTE1"] if "before" in label else
        (df.loc[(NJ) & (w == 3) & df.FTE1.notna() & df[fte_col].notna()] if "change" in label else df.loc[(NJ) & (w == 3), fte_col]))
    rows.append({"row": label, **d})

# Row 1: FTE before, all available
m1n, s1n = mean_se(df.loc[NJ, "FTE1"]); m1p, s1p = mean_se(df.loc[PA, "FTE1"])
d = {"PA": m1p, "PA_se": s1p, "NJ": m1n, "NJ_se": s1n,
     "NJmPA": m1n - m1p, "NJmPA_se": np.sqrt(s1n**2 + s1p**2)}
for code, key in [(1, "w425"), (2, "wmid"), (3, "whigh")]:
    m = df.loc[(NJ) & (df.wage_class == code), "FTE1"]
    d[key], d[key + "_se"], d[key + "_n"] = *mean_se(m), len(m.dropna())
d["lo_hi"], d["lo_hi_se"] = diff_mean_se(df.loc[(NJ) & (df.wage_class == 1), "FTE1"],
                                         df.loc[(NJ) & (df.wage_class == 3), "FTE1"])
d["mid_hi"], d["mid_hi_se"] = diff_mean_se(df.loc[(NJ) & (df.wage_class == 2), "FTE1"],
                                           df.loc[(NJ) & (df.wage_class == 3), "FTE1"])
d["mid_lo"], d["mid_lo_se"] = diff_mean_se(df.loc[(NJ) & (df.wage_class == 2), "FTE1"],
                                           df.loc[(NJ) & (df.wage_class == 1), "FTE1"])
rows.append({"row": "1. FTE before (all available)", **d})

# Row 2: FTE after, all available (closed=0, temp missing)
m2n, s2n = mean_se(df.loc[NJ, "FTE2"]); m2p, s2p = mean_se(df.loc[PA, "FTE2"])
d = {"PA": m2p, "PA_se": s2p, "NJ": m2n, "NJ_se": s2n,
     "NJmPA": m2n - m2p, "NJmPA_se": np.sqrt(s2n**2 + s2p**2)}
for code, key in [(1, "w425"), (2, "wmid"), (3, "whigh")]:
    m = df.loc[(NJ) & (df.wage_class == code), "FTE2"]
    d[key], d[key + "_se"], d[key + "_n"] = *mean_se(m), len(m.dropna())
d["lo_hi"], d["lo_hi_se"] = diff_mean_se(df.loc[(NJ) & (df.wage_class == 1), "FTE2"],
                                         df.loc[(NJ) & (df.wage_class == 3), "FTE2"])
d["mid_hi"], d["mid_hi_se"] = diff_mean_se(df.loc[(NJ) & (df.wage_class == 2), "FTE2"],
                                           df.loc[(NJ) & (df.wage_class == 3), "FTE2"])
d["mid_lo"], d["mid_lo_se"] = diff_mean_se(df.loc[(NJ) & (df.wage_class == 2), "FTE2"],
                                           df.loc[(NJ) & (df.wage_class == 1), "FTE2"])
rows.append({"row": "2. FTE after (all available)", **d})

# Row 3: change in mean (row2 - row1); Row 4: balanced; Row 5: temp=0
def change_row(label, fte_col):
    bal = df[(df.FTE1.notna()) & (df[fte_col].notna())].copy()
    bal["d"] = bal[fte_col] - bal["FTE1"]
    dPA, dNJ = bal.loc[bal.STATE == 0, "d"], bal.loc[bal.STATE == 1, "d"]
    d = {"PA": dPA.mean(), "PA_se": se_mean(dPA),
         "NJ": dNJ.mean(), "NJ_se": se_mean(dNJ),
         "NJmPA": dNJ.mean() - dPA.mean(),
         "NJmPA_se": np.sqrt(dNJ.var(ddof=1) / len(dNJ) + dPA.var(ddof=1) / len(dPA)),
         "nPA": len(dPA), "nNJ": len(dNJ)}
    for code, key in [(1, "w425"), (2, "wmid"), (3, "whigh")]:
        m = bal.loc[(bal.wage_class == code) & (bal.STATE == 1)]
        d[key], d[key + "_se"], d[key + "_n"] = m["d"].mean(), se_mean(m["d"]), len(m)
    for a, b, ka, kb in [(1, 3, "lo_hi", None), (2, 3, "mid_hi", None), (2, 1, "mid_lo", None)]:
        A = bal.loc[(bal.wage_class == a) & (bal.STATE == 1), "d"]
        B = bal.loc[(bal.wage_class == b) & (bal.STATE == 1), "d"]
        d[ka], d[ka + "_se"] = A.mean() - B.mean(), np.sqrt(A.var(ddof=1) / len(A) + B.var(ddof=1) / len(B))
    rows.append({"row": label, **d})

# Row 3 uses "all available" per-wave means; we compute the mean change as
# mean(FTE2)-mean(FTE1) over each state's available observations (difference of
# means), with SE from the balanced per-store changes (matches the paper for PA;
# see report for discussion).
change_row("3. Change in mean FTE", "FTE2")
# fix row 3 means to be difference-of-means (all available)
r3 = next(r for r in rows if r["row"] == "3. Change in mean FTE")
m1n, s1n = mean_se(df.loc[NJ, "FTE1"]); m1p, s1p = mean_se(df.loc[PA, "FTE1"])
m2n, s2n = mean_se(df.loc[NJ, "FTE2"]); m2p, s2p = mean_se(df.loc[PA, "FTE2"])
r3["PA"] = m2p - m1p
r3["NJ"] = m2n - m1n
r3["NJmPA"] = (m2n - m1n) - (m2p - m1p)
for code, key in [(1, "w425"), (2, "wmid"), (3, "whigh")]:
    m1 = df.loc[(NJ) & (df.wage_class == code), "FTE1"].mean()
    m2 = df.loc[(NJ) & (df.wage_class == code), "FTE2"].mean()
    r3[key] = m2 - m1
r3["lo_hi"] = r3["w425"] - r3["whigh"]
r3["mid_hi"] = r3["wmid"] - r3["whigh"]
r3["mid_lo"] = r3["wmid"] - r3["w425"]

change_row("4. Change in mean FTE, balanced sample", "FTE2")
change_row("5. Change in mean FTE, temp closed = 0", "FTE2_zerotemp")

t3 = pd.DataFrame(rows)
t3.to_csv(OUT, index=False)

print("\n================ TABLE 3 (replication) ================")
cols = ["PA", "NJ", "NJmPA", "w425", "wmid", "whigh", "lo_hi", "mid_hi", "mid_lo"]
for _, r in t3.iterrows():
    line = f"{r['row']:<38s}"
    for c in cols:
        line += f"  {r[c]:>6.2f}"
        if pd.notna(r.get(c + "_se")):
            line += f"({r[c+'_se']:.2f})"
        else:
            line += f"      "
    line += f"  [nPA={r.get('nPA', '')}, nNJ={r.get('nNJ', '')}]"
    print(line)
print(f"\nSaved: {OUT}")
print("\nPaper Table 3 key values: row3 PA -2.16(1.25) NJ 0.59(0.54) DID 2.76(1.56); "
      "row4 PA -2.28(1.25) NJ 0.47(0.48) DID 2.75(1.34); row5 DID 2.51(1.35)")
