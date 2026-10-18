"""00_check.py — Lock down replication conventions (SE formulas, wage classification)."""
import pandas as pd
import numpy as np

DATA = "/home/user/Doubao/chats/38447780988890626/data/input/public.csv"
df = pd.read_csv(DATA)

# FTE
df["FTE1"] = df["EMPFT"] + 0.5 * df["EMPPT"] + df["NMGRS"]
df["FTE2_raw"] = df["EMPFT2"] + 0.5 * df["EMPPT2"] + df["NMGRS2"]
# closed (STATUS2==3) -> 0; temp closed/renov (2,4,5) & refusal (0) -> missing
df["FTE2"] = df["FTE2_raw"].where(df["STATUS2"].isin([1]), np.nan)
df.loc[df["STATUS2"] == 3, "FTE2"] = 0.0
df["FTE2_zerotemp"] = df["FTE2"].copy()
df.loc[df["STATUS2"].isin([2, 4, 5]), "FTE2_zerotemp"] = 0.0  # row-5 convention

print("=== Wave-1 wage data of non-open stores ===")
print(df.loc[df["STATUS2"] != 1, ["SHEET", "STATE", "STATUS2", "WAGE_ST"]].to_string())

print("\n=== NJ wage classification (wave 1, nonmissing) ===")
nj = df[(df["STATE"] == 1) & df["WAGE_ST"].notna()]
print("N total NJ with wage:", len(nj))
print("Wage=4.25:", (nj["WAGE_ST"] == 4.25).sum())
print("4.26-4.99:", ((nj["WAGE_ST"] > 4.25) & (nj["WAGE_ST"] < 5.00)).sum())
print(">=5.00:", (nj["WAGE_ST"] >= 5.00).sum())
print("NJ wave-1 wage distribution (top):")
print(nj["WAGE_ST"].value_counts().sort_index().head(20))
print("...max:", nj["WAGE_ST"].max(), "min:", nj["WAGE_ST"].min())

print("\n=== Table 3, rows 1-5 (means) ===")
def se(x): return x.std(ddof=1) / np.sqrt(x.count()) if x.count() > 1 else np.nan

r1 = df.groupby("STATE")["FTE1"].agg(["mean", se, "count"])
r2 = df.groupby("STATE")["FTE2"].agg(["mean", se, "count"])
print("Row1 FTE before:\n", r1)
print("Row2 FTE after:\n", r2)

# Row 3 = row2 - row1
for st, lab in [(0, "PA"), (1, "NJ")]:
    m1 = r1.loc[st, "mean"]; m2 = r2.loc[st, "mean"]
    print(f"{lab} row3 change = {m2 - m1:.2f}")

# Row 4 balanced (both FTE1 and FTE2 nonmissing)
bal = df[df["FTE1"].notna() & df["FTE2"].notna()].copy()
bal["dFTE"] = bal["FTE2"] - bal["FTE1"]
r4 = bal.groupby("STATE")["dFTE"].agg(["mean", se, "count"])
print("Row4 balanced:\n", r4)

# Row 5 (temp/renov set to 0, so only STATUS2==0 refusal excluded)
bal5 = df[df["FTE1"].notna() & df["FTE2_zerotemp"].notna()].copy()
bal5["dFTE"] = bal5["FTE2_zerotemp"] - bal5["FTE1"]
r5 = bal5.groupby("STATE")["dFTE"].agg(["mean", se, "count"])
print("Row5 (temp=0):\n", r5)

# Candidate SE formulas for row 3
print("\n=== Row-3 SE candidates ===")
for st, lab in [(0, "PA"), (1, "NJ")]:
    s1 = df.loc[df.STATE == st, "FTE1"]; s2 = df.loc[df.STATE == st, "FTE2"]
    n1, n2 = s1.count(), s2.count()
    v1, v2 = s1.var(ddof=1), s2.var(ddof=1)
    # unpaired
    unpaired = np.sqrt(v1 / n1 + v2 / n2)
    # balanced
    d = bal.loc[bal.STATE == st, "dFTE"]
    bal_se = d.std(ddof=1) / np.sqrt(d.count())
    print(f"{lab}: unpaired SE={unpaired:.3f} | balanced SE={bal_se:.3f} | paper row3 SE: {'1.25' if st==0 else '0.54'}")

# DID SE candidates (NJ-PA)
d_nj = bal.loc[bal.STATE == 1, "dFTE"]; d_pa = bal.loc[bal.STATE == 0, "dFTE"]
did_se = np.sqrt(d_nj.var(ddof=1) / d_nj.count() + d_pa.var(ddof=1) / d_pa.count())
print(f"\nRow4 DID = {d_nj.mean() - d_pa.mean():.2f}, SE(two-sample) = {did_se:.3f}  [paper 2.75 (1.34)]")

# Row3 DID SE candidates
s1_nj = df.loc[df.STATE == 1, "FTE1"]; s2_nj = df.loc[df.STATE == 1, "FTE2"]
s1_pa = df.loc[df.STATE == 0, "FTE1"]; s2_pa = df.loc[df.STATE == 0, "FTE2"]
v = lambda x: x.var(ddof=1); n = lambda x: x.count()
se_row3 = np.sqrt(v(s1_nj)/n(s1_nj) + v(s2_nj)/n(s2_nj) + v(s1_pa)/n(s1_pa) + v(s2_pa)/n(s2_pa))
print(f"Row3 DID SE (4-term unpaired) = {se_row3:.3f}  [paper 1.56]")

print("\n=== Row5 DID ===")
d5_nj = bal5.loc[bal5.STATE == 1, "dFTE"]; d5_pa = bal5.loc[bal5.STATE == 0, "dFTE"]
did5 = d5_nj.mean() - d5_pa.mean()
did5_se = np.sqrt(d5_nj.var(ddof=1)/d5_nj.count() + d5_pa.var(ddof=1)/d5_pa.count())
print(f"Row5 DID = {did5:.2f}, SE = {did5_se:.3f}  [paper 2.51 (1.35)]")
