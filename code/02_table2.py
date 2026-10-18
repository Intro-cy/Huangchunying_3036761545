"""02_table2.py — Replicate Table 2 (Means of Key Variables) of Card & Krueger (1994).

Output: outputs/tables/table2.csv + console table.
Conventions: means over nonmissing responses; wave-2 FTE = 0 for permanently
closed stores, missing for temporarily closed / renovation / refusal stores.
t statistic = two-sample t (unequal variances) for equality of means NJ vs PA.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from ck94_utils import load_clean_data, se_mean, tstat_two_sample

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "outputs" / "tables" / "table2.csv"

df = load_clean_data()

# ---- construct indicators used in Table 2 ----
df["pct_ft1"] = 100 * df["EMPFT"] / df["FTE1"]
df["pct_ft2"] = 100 * df["EMPFT2"] / df["FTE2"]
df["wage_425"] = 100 * (df["WAGE_ST"] == 4.25).astype(float)
df["wage_425_2"] = 100 * (df["WAGE_ST2"] == 4.25).astype(float)
df["wage_505_2"] = 100 * (df["WAGE_ST2"] == 5.05).astype(float)
df["meal_price"] = df["PSODA"] + df["PFRY"] + df["PENTREE"]
df["meal_price2"] = df["PSODA2"] + df["PFRY2"] + df["PENTREE2"]
df["bonus1"] = 100 * df["BONUS"].astype(float)

rows = []

def add_row(label, col):
    g1 = df.loc[(df.STATE == 1) & df[col].notna(), col]
    g0 = df.loc[(df.STATE == 0) & df[col].notna(), col]
    rows.append({"Variable": label,
                 "NJ_mean": g1.mean(), "NJ_se": se_mean(g1),
                 "PA_mean": g0.mean(), "PA_se": se_mean(g0),
                 "t": tstat_two_sample(g1, g0), "n_NJ": len(g1), "n_PA": len(g0)})

# --- 1. Distribution of store types (percentages WITHIN state) ---
N_NJ, N_PA = (df.STATE == 1).sum(), (df.STATE == 0).sum()

def prop_z(n1, n2, N1, N2):
    p1, p2 = n1 / N1, n2 / N2
    pp = (n1 + n2) / (N1 + N2)
    return (p1 - p2) / np.sqrt(pp * (1 - pp) * (1 / N1 + 1 / N2))

for chain, name in [(1, "a. Burger King"), (2, "b. KFC"), (3, "c. Roy Rogers"), (4, "d. Wendy's")]:
    n_nj = ((df["chain"] == chain) & (df.STATE == 1)).sum()
    n_pa = ((df["chain"] == chain) & (df.STATE == 0)).sum()
    pct_nj, pct_pa = 100 * n_nj / N_NJ, 100 * n_pa / N_PA
    se_pa = np.sqrt(pct_pa * (100 - pct_pa) / N_PA)
    rows.append({"Variable": name, "NJ_mean": pct_nj, "NJ_se": np.nan,
                 "PA_mean": pct_pa, "PA_se": se_pa, "t": prop_z(n_nj, n_pa, N_NJ, N_PA),
                 "n_NJ": n_nj, "n_PA": n_pa})
n_nj = ((df.CO_OWNED == 1) & (df.STATE == 1)).sum()
n_pa = ((df.CO_OWNED == 1) & (df.STATE == 0)).sum()
pct_nj, pct_pa = 100 * n_nj / N_NJ, 100 * n_pa / N_PA
se_pa = np.sqrt(pct_pa * (100 - pct_pa) / N_PA)
rows.append({"Variable": "e. Company-owned", "NJ_mean": pct_nj, "NJ_se": np.nan,
             "PA_mean": pct_pa, "PA_se": se_pa, "t": prop_z(n_nj, n_pa, N_NJ, N_PA),
             "n_NJ": n_nj, "n_PA": n_pa})

# --- 2 / 3. Means in waves 1 and 2 ---
add_row("2a. FTE employment", "FTE1")
add_row("2b. Percentage full-time", "pct_ft1")
add_row("2c. Starting wage", "WAGE_ST")
add_row("2d. Wage = $4.25 (percentage)", "wage_425")
add_row("2e. Price of full meal", "meal_price")
add_row("2f. Hours open (weekday)", "HRSOPEN")
add_row("2g. Recruiting bonus (percentage)", "bonus1")
add_row("3a. FTE employment", "FTE2")
add_row("3b. Percentage full-time", "pct_ft2")
add_row("3c. Starting wage", "WAGE_ST2")
add_row("3d. Wage = $4.25 (percentage)", "wage_425_2")
add_row("3e. Wage = $5.05 (percentage)", "wage_505_2")
add_row("3f. Price of full meal", "meal_price2")
add_row("3g. Hours open (weekday)", "HRSOPEN2")

t2 = pd.DataFrame(rows)
t2.to_csv(OUT, index=False)

print("\n================ TABLE 2 (replication) ================")
print(f"{'Variable':<32s} {'NJ':>8s} {'SE':>6s} {'n':>4s} | {'PA':>8s} {'SE':>6s} {'n':>4s} | {'t':>5s}")
for _, r in t2.iterrows():
    nj = f"{r['NJ_mean']:.2f}" if pd.notna(r['NJ_mean']) else "  --  "
    sej = f"({r['NJ_se']:.2f})" if pd.notna(r['NJ_se']) else ""
    pa = f"{r['PA_mean']:.2f}" if pd.notna(r['PA_mean']) else "  --  "
    sep = f"({r['PA_se']:.2f})" if pd.notna(r['PA_se']) else ""
    t = f"{r['t']:.1f}" if pd.notna(r['t']) else "--"
    print(f"{r['Variable']:<32s} {nj:>7s} {sej:>6s} {r['n_NJ']:>4.0f} | {pa:>7s} {sep:>6s} {r['n_PA']:>4.0f} | {t:>5s}")
print(f"\nSaved: {OUT}")

# quick check vs paper
print("\nPaper values: NJ FTE1 20.4 (0.51) / PA 23.3 (1.35);  NJ W1 4.61 (0.02) / PA 4.63 (0.04);")
print("w2: NJ 21.0 (0.52) / PA 21.2 (0.94);  NJ wage2 5.08 (0.01) / PA 4.62 (0.04);")
print("NJ $5.05 share 85.2 (2.0) / PA 1.3 (1.3);  meal price NJ 3.35 / PA 3.04")
