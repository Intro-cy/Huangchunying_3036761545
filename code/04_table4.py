"""04_table4.py — Replicate Table 4 (Reduced-Form Models for Change in Employment) of CK (1994).

Sample (verified to reproduce the paper's N=357 and all published coefficients):
stores with FTE employment in both waves, wave-1 starting wage, and (wave-2
starting wage OR permanently closed). Permanently closed stores have wave-2 FTE = 0.
Dependent variable: change in FTE employment (dFTE).
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
from ck94_utils import load_clean_data

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "outputs" / "tables" / "table4.csv"

df = load_clean_data()

# ---- sample (N=357 in the paper) ----
sel = (df.FTE1.notna() & df.FTE2.notna() & df.WAGE_ST.notna()
       & (df.WAGE_ST2.notna() | (df.STATUS2 == 3)))
s = df[sel].copy()
print("Table-4 sample N:", len(s), " (paper: 357)")

y = s["dFTE"]
print(f"Dep var: mean={y.mean():.3f} sd={y.std(ddof=1):.3f}  (paper: 0.226 / 8.825)")

base_ctrl = ["ch_2", "ch_3", "ch_4", "COOWNED"]
regions3 = ["NORTHJ", "CENTRALJ", "SOUTHJ", "PA1", "PA2"]
regions2 = ["NORTHJ", "CENTRALJ", "PA1", "PA2"]

def run(Xnames):
    X = sm.add_constant(s[Xnames])
    return sm.OLS(y, X).fit()

def f_test_excl(full, ctrl_names):
    """Joint F test for exclusion of all control variables (RSS comparison)."""
    if not ctrl_names:
        return np.nan
    rss_full = float(full.ssr)
    Xr = sm.add_constant(s[[c for c in full.model.exog_names if c not in ctrl_names and c != 'const']])
    red = sm.OLS(y, Xr).fit()
    q = len(ctrl_names)
    F = ((red.ssr - rss_full) / q) / (rss_full / (full.df_resid))
    from scipy import stats
    return float(1 - stats.f.cdf(F, q, full.df_resid))

specs = [
    ("(i)  NJ dummy", ["NJ"], []),
    ("(ii) NJ + controls", ["NJ"] + base_ctrl, base_ctrl),
    ("(iii) GAP", ["GAP"], []),
    ("(iv) GAP + controls", ["GAP"] + base_ctrl, base_ctrl),
    ("(v)  GAP + ctrl + region (3NJ+2PA)", ["GAP"] + base_ctrl + regions3, base_ctrl + regions3),
    ("(v') GAP + ctrl + region (2NJ+2PA)", ["GAP"] + base_ctrl + regions2, base_ctrl + regions2),
]

rows = []
print("\n================ TABLE 4 (replication) ================")
print(f"{'Model':<34s} {'coef':>8s} {'se':>7s} {'t':>7s} {'SER':>6s} {'p(ctrl)':>8s} {'N':>4s}")
for label, Xnames, ctrl in specs:
    m = run(Xnames)
    key = Xnames[0]
    b, se, t = m.params[key], m.bse[key], m.tvalues[key]
    pctrl = f_test_excl(m, ctrl)
    rows.append({"model": label, "var": key, "coef": b, "se": se, "t": t,
                 "SER": np.sqrt(m.mse_resid), "p_ctrl": pctrl, "N": int(m.nobs),
                 "R2": m.rsquared})
    print(f"{label:<34s} {b:>8.2f} {se:>7.2f} {t:>7.2f} {np.sqrt(m.mse_resid):>6.2f} "
          f"{pctrl:>8.4f} {int(m.nobs):>4d}")

t4 = pd.DataFrame(rows)
t4.to_csv(OUT, index=False)

print("\nPaper Table 4: (i) NJ 2.33(1.19); (ii) 2.30(1.20) p=.34; (iii) GAP 15.65(6.08);")
print("(iv) 14.92(6.21) p=.44; (v) 11.91(7.39) p=.40 | SER 8.79/8.78/8.76/8.76/8.75")
print("Mean GAP among NJ stores (paper 0.11):",
      round(s.loc[s.NJ == 1, "GAP"].mean(), 3))
