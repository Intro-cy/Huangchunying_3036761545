"""07_spec_tests.py — Replicate a subset of Table 5 (Specification Tests) of CK (1994)
as part of core-replication validation.

Rows replicated (level models: dep var = change in FTE; proportional models:
dep var = change / average of the two waves, closed stores set to -1):
  1. Base specification (Table 4 cols ii / iv)
  2. Treat four temporarily closed stores as permanently closed (FTE2 = 0)
  3. Exclude managers from the employment count
  4. Weight part-time workers as 0.4 x full-time
  5. Weight part-time workers as 0.6 x full-time
  6. Exclude stores in the NJ shore area
  8. Exclude stores called more than twice in wave 1 (NCALLS <= 2)
  9. Weighted least squares (weight = wave-1 employment), proportional model only
 12. Pennsylvania stores only; GAP defined as if the NJ minimum applied in PA
All models include chain dummies and the company-owned indicator.
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
from ck94_utils import load_clean_data, REPO

OUT = REPO / "outputs" / "tables" / "table5_subset.csv"

df = load_clean_data()

# base FTE variants
df["FTE_nomgr"] = df["EMPFT"] + 0.5 * df["EMPPT"]
df["FTE_pt04"] = df["EMPFT"] + df["NMGRS"] + 0.4 * df["EMPPT"]
df["FTE_pt06"] = df["EMPFT"] + df["NMGRS"] + 0.6 * df["EMPPT"]

def base_sample(fte1_col, fte2_col, extra=None):
    m = (df[fte1_col].notna() & df[fte2_col].notna() & df.WAGE_ST.notna()
         & (df.WAGE_ST2.notna() | (df.STATUS2 == 3)))
    if extra is not None:
        m &= extra
    s = df[m].copy()
    return s

def run_level(s, fte1, fte2, key, dep=None, controls=("ch_2", "ch_3", "ch_4", "COOWNED")):
    """Level model: dep ~ key + controls (NJ and GAP models are separate, as in Table 5)."""
    if dep is None:
        y = s[fte2] - s[fte1]
    else:
        y = s[dep]
    X = sm.add_constant(s[[key] + list(controls)])
    m = sm.OLS(y, X).fit()
    return m.params[key], m.bse[key], m.tvalues[key], int(m.nobs), np.sqrt(m.mse_resid)

def run_prop(s, fte1, fte2, key, weights=None, controls=("ch_2", "ch_3", "ch_4", "COOWNED")):
    avg = (s[fte1] + s[fte2]) / 2
    y = (s[fte2] - s[fte1]) / avg
    y = y.where(s[fte1].notna() & s[fte2].notna())
    # closed stores -> -1 (paper footnote 18)
    y = y.fillna(-1.0)
    X = sm.add_constant(s[[key] + list(controls)])
    if weights is None:
        m = sm.OLS(y, X).fit()
    else:
        m = sm.WLS(y, X, weights=s[weights]).fit()
    return m.params[key], m.bse[key], m.tvalues[key], int(m.nobs), np.sqrt(m.mse_resid)

rows = []

# row 1: base
s = base_sample("FTE1", "FTE2")
rows.append(("1. Base specification",) + run_level(s, "FTE1", "FTE2", "NJ")
            + run_level(s, "FTE1", "FTE2", "GAP")
            + run_prop(s, "FTE1", "FTE2", "NJ")
            + run_prop(s, "FTE1", "FTE2", "GAP"))
# row 2: temp closed -> 0
s2 = df[(df.FTE1.notna() & df.FTE2_zerotemp.notna() & df.WAGE_ST.notna() & (df.WAGE_ST2.notna() | (df.STATUS2.isin([2, 3, 4, 5]))))].copy()
rows.append(("2. Temp closed as 0",) + run_level(s2, "FTE1", "FTE2_zerotemp", "NJ")
            + run_level(s2, "FTE1", "FTE2_zerotemp", "GAP")
            + run_prop(s2, "FTE1", "FTE2_zerotemp", "NJ")
            + run_prop(s2, "FTE1", "FTE2_zerotemp", "GAP"))
# row 3-5: alternative FTE measures (exclude managers; PT weights 0.4 / 0.6)
FTE_nomgr2 = df["EMPFT2"] + 0.5 * df["EMPPT2"]
FTE_pt04_2 = df["EMPFT2"] + df["NMGRS2"] + 0.4 * df["EMPPT2"]
FTE_pt06_2 = df["EMPFT2"] + df["NMGRS2"] + 0.6 * df["EMPPT2"]

def alt_sample(f1, f2):
    s = df[(df[f1].notna()) & (f2.notna()) & df.WAGE_ST.notna()
           & (df.WAGE_ST2.notna() | (df.STATUS2 == 3))].copy()
    s["f2c"] = np.where(s.STATUS2 == 3, 0.0, f2.reindex(s.index))
    return s

s_nomgr = alt_sample("FTE_nomgr", FTE_nomgr2)
rows.append(("3. Exclude managers",) + run_level(s_nomgr, "FTE_nomgr", "f2c", "NJ")
            + run_level(s_nomgr, "FTE_nomgr", "f2c", "GAP")
            + run_prop(s_nomgr, "FTE_nomgr", "f2c", "NJ")
            + run_prop(s_nomgr, "FTE_nomgr", "f2c", "GAP"))

s_pt04 = alt_sample("FTE_pt04", FTE_pt04_2)
rows.append(("4. PT weight 0.4",) + run_level(s_pt04, "FTE_pt04", "f2c", "NJ")
            + run_level(s_pt04, "FTE_pt04", "f2c", "GAP")
            + run_prop(s_pt04, "FTE_pt04", "f2c", "NJ")
            + run_prop(s_pt04, "FTE_pt04", "f2c", "GAP"))

s_pt06 = alt_sample("FTE_pt06", FTE_pt06_2)
rows.append(("5. PT weight 0.6",) + run_level(s_pt06, "FTE_pt06", "f2c", "NJ")
            + run_level(s_pt06, "FTE_pt06", "f2c", "GAP")
            + run_prop(s_pt06, "FTE_pt06", "f2c", "NJ")
            + run_prop(s_pt06, "FTE_pt06", "f2c", "GAP"))

# row 6: exclude shore
s_shore = base_sample("FTE1", "FTE2", extra=(df.SHORE == 0))
rows.append(("6. Exclude NJ shore",) + run_level(s_shore, "FTE1", "FTE2", "NJ")
            + run_level(s_shore, "FTE1", "FTE2", "GAP")
            + run_prop(s_shore, "FTE1", "FTE2", "NJ")
            + run_prop(s_shore, "FTE1", "FTE2", "GAP"))

# row 8: exclude stores called >2 times in wave 1
s_calls = base_sample("FTE1", "FTE2", extra=(df.NCALLS <= 2))
rows.append(("8. Exclude >2 calls w1",) + run_level(s_calls, "FTE1", "FTE2", "NJ")
            + run_level(s_calls, "FTE1", "FTE2", "GAP")
            + run_prop(s_calls, "FTE1", "FTE2", "NJ")
            + run_prop(s_calls, "FTE1", "FTE2", "GAP"))

# row 9: WLS proportional, weight = wave-1 employment (paper reports level columns as --)
rows.append(("9. WLS by initial emp",) + (np.nan,) * 5 + (np.nan,) * 5
            + run_prop(s, "FTE1", "FTE2", "NJ", weights="FTE1")
            + run_prop(s, "FTE1", "FTE2", "GAP", weights="FTE1"))

# row 12: PA only, GAP as if NJ minimum applied (level + proportional only)
s_pa = df[(df.STATE == 0) & df.FTE1.notna() & df.FTE2.notna() & df.WAGE_ST.notna() & (df.WAGE_ST2.notna() | (df.STATUS2 == 3))].copy()
s_pa["GAPPA"] = np.where(s_pa.WAGE_ST.isna(), np.nan, (5.05 - s_pa.WAGE_ST) / s_pa.WAGE_ST)
rows.append(("12. PA only",) + (np.nan,) * 5 + run_level(s_pa, "FTE1", "FTE2", "GAPPA")
            + (np.nan,) * 5 + run_prop(s_pa, "FTE1", "FTE2", "GAPPA"))

t5 = pd.DataFrame(rows, columns=["spec", "NJ_lvl", "NJ_se", "NJ_t", "n_lvl", "ser_lvl",
                                 "GAP_lvl", "GAP_se", "GAP_t", "n2", "ser2",
                                 "NJp", "NJp_se", "NJp_t", "n3", "ser3",
                                 "GAPp", "GAPp_se", "GAPp_t", "n4", "ser4"])
t5.to_csv(OUT, index=False)

print("\n================ TABLE 5 subset (replication vs paper) ================")
print(f"{'Specification':<24s} {'NJ(lvl)':>18s} {'GAP(lvl)':>18s} {'NJ(prop)':>16s} {'GAP(prop)':>16s}")
paper = {
 "1. Base specification": ("2.30(1.19)", "14.92(6.21)", "0.05(0.05)", "0.34(0.26)"),
 "2. Temp closed as 0": ("2.20(1.21)", "14.42(6.31)", "0.05(0.05)", "0.34(0.27)"),
 "3. Exclude managers": ("2.34(1.17)", "14.69(6.05)", "0.05(0.07)", "0.28(0.34)"),
 "4. PT weight 0.4": ("2.34(1.20)", "15.23(6.23)", "0.06(0.06)", "0.30(0.33)"),
 "5. PT weight 0.6": ("2.27(1.21)", "14.60(6.26)", "0.04(0.06)", "0.17(0.29)"),
 "6. Exclude NJ shore": ("2.58(1.19)", "16.88(6.36)", "0.06(0.05)", "0.42(0.27)"),
 "8. Exclude >2 calls w1": ("2.41(1.28)", "14.08(7.11)", "0.05(0.05)", "0.31(0.29)"),
 "9. WLS by initial emp (prop)": ("--", "--", "0.13(0.05)", "0.81(0.26)"),
 "12. PA only (level)": ("--", "-0.30(22.00)", "--", "-0.33(0.74)"),
}
for _, r in t5.iterrows():
    def f(b, se): return f"{b:.2f}({se:.2f})"
    p = paper.get(r["spec"], ("", "", "", ""))
    print(f"{r['spec']:<24s} {f(r.NJ_lvl, r.NJ_se):>18s} {f(r.GAP_lvl, r.GAP_se):>18s} "
          f"{f(r.NJp, r.NJp_se):>16s} {f(r.GAPp, r.GAPp_se):>16s}")
    print(f"{'':24s}   paper: {p[0]:>16s} {p[1]:>16s} {p[2]:>14s} {p[3]:>14s}")
print(f"\nSaved: {OUT}")
