"""00_diag_row3.py — Identify the SE convention behind Table 3 row 3 (paper: PA 1.25, NJ 0.54, DID 1.56)."""
import pandas as pd
import numpy as np
from ck94_utils import load_clean_data, se_mean

df = load_clean_data()
NJ, PA = df.STATE == 1, df.STATE == 0

print("=== candidate row-3 samples & SEs ===")
# A: balanced (FTE1 & FTE2), incl closed=0
bal = df[df.FTE1.notna() & df.FTE2.notna()].copy(); bal["d"] = bal.FTE2 - bal.FTE1
for st, lab in [(0, "PA"), (1, "NJ")]:
    d = bal.loc[bal.STATE == st, "d"]
    print(f"A balanced          {lab}: mean={d.mean():.3f} sd={d.std(ddof=1):.2f} n={len(d)} SE={se_mean(d):.3f}")

# B: balanced + wage in both waves (the 357 Table-4 sample)
s4 = df[df.FTE1.notna() & df.FTE2.notna() & df.WAGE_ST.notna() & df.WAGE_ST2.notna()].copy()
s4["d"] = s4.FTE2 - s4.FTE1
print("Table-4 style sample N:", len(s4))
for st, lab in [(0, "PA"), (1, "NJ")]:
    d = s4.loc[s4.STATE == st, "d"]
    print(f"B bal+wage           {lab}: mean={d.mean():.3f} sd={d.std(ddof=1):.2f} n={len(d)} SE={se_mean(d):.3f}")
did_se_b = np.sqrt(s4.loc[s4.STATE==1,"d"].var(ddof=1)/len(s4.loc[s4.STATE==1]) +
                   s4.loc[s4.STATE==0,"d"].var(ddof=1)/len(s4.loc[s4.STATE==0]))
print("   DID (B, two-sample):", did_se_b)

# C: survivors (exclude permanently closed)
surv = df[df.FTE1.notna() & df.FTE2.notna() & (df.STATUS2 != 3)].copy()
surv["d"] = surv.FTE2 - surv.FTE1
for st, lab in [(0, "PA"), (1, "NJ")]:
    d = surv.loc[surv.STATE == st, "d"]
    print(f"C survivors          {lab}: mean={d.mean():.3f} sd={d.std(ddof=1):.2f} n={len(d)} SE={se_mean(d):.3f}")

# D: unpaired diff-of-means (all available)
for st, lab in [(0, "PA"), (1, "NJ")]:
    s1 = df.loc[df.STATE == st, "FTE1"]; s2 = df.loc[df.STATE == st, "FTE2"]
    se_u = np.sqrt(s1.var(ddof=1)/len(s1) + s2.var(ddof=1)/len(s2))
    print(f"D unpaired           {lab}: mean={s2.mean()-s1.mean():.3f} SE={se_u:.3f}")

# E: sqrt(se1_bal^2 + se2_bal^2) with balanced-sample wave SEs
for st, lab in [(0, "PA"), (1, "NJ")]:
    b = bal.loc[bal.STATE == st]
    se1 = b.FTE1.std(ddof=1)/np.sqrt(len(b)); se2 = b.FTE2.std(ddof=1)/np.sqrt(len(b))
    print(f"E bal-wave-SEs       {lab}: sqrt(se1^2+se2^2) = {np.sqrt(se1**2+se2**2):.3f} (se1={se1:.3f}, se2={se2:.3f})")

# F: balanced-sample wave SEs summed over both states for DID
bN = bal.loc[bal.STATE==1]; bP = bal.loc[bal.STATE==0]
e = lambda s: s.std(ddof=1)/np.sqrt(len(s))
did_f = np.sqrt(e(bN.FTE1)**2 + e(bN.FTE2)**2 + e(bP.FTE1)**2 + e(bP.FTE2)**2)
print(f"F DID = sqrt(sum of 4 bal-wave se^2) = {did_f:.3f}")

# G: row-3 DID SE = sqrt(SE_NJ^2 + SE_PA^2) using paper-like row-3 SEs 0.54 & 1.25
print("G sqrt(0.54^2 + 1.25^2) =", np.sqrt(0.54**2 + 1.25**2))

print("\nPaper row 3: PA -2.16 (1.25), NJ 0.59 (0.54), DID 2.76 (1.56)")
