"""00_explore.py — Inspect the Card & Krueger (1994) public data.

Purpose: verify variable coding, sample structure, and the FTE definition
against the published Tables 2-3 before building the replication pipeline.
"""
import pandas as pd
import numpy as np

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 60)

DATA = "/home/user/Doubao/chats/38447780988890626/data/raw/public.csv"
df = pd.read_csv(DATA)

print("Shape:", df.shape)
print("\nDtypes:\n", df.dtypes)

# --- Sample composition ---
print("\n=== STATE composition ===")
print(df["STATE"].value_counts().sort_index())
print("\n=== Region dummies ===")
for c in ["SOUTHJ", "CENTRALJ", "NORTHJ", "PA1", "PA2", "SHORE"]:
    print(c, df[c].value_counts().sort_index().to_dict())

print("\n=== CHAIN ===")
print(df["CHAIN"].value_counts().sort_index())
print("\n=== CO_OWNED ===")
print(df["CO_OWNED"].value_counts().sort_index())

# --- Wave-2 status / type ---
print("\n=== TYPE2 (wave-2 interview type) ===")
print(df["TYPE2"].value_counts(dropna=False).sort_index())
print("\n=== STATUS2 (wave-2 status) ===")
print(df["STATUS2"].value_counts(dropna=False).sort_index())
print("\n=== NCALLS ===")
print(df["NCALLS"].value_counts(dropna=False).sort_index())
print("\n=== OPEN (wave1 opening time) / MEALS coding sample ===")
print(df[["MEALS", "MEALS2"]].value_counts(dropna=False).sort_index())

# --- Missing patterns in key vars ---
print("\n=== Nonmissing counts (wave 1) ===")
for c in ["EMPFT", "EMPPT", "NMGRS", "WAGE_ST", "HRSOPEN", "PSODA", "PFRY", "PENTREE", "BONUS"]:
    print(c, int(df[c].notna().sum()), "/", len(df))
print("\n=== Nonmissing counts (wave 2) ===")
for c in ["EMPFT2", "EMPPT2", "NMGRS2", "WAGE_ST2", "HRSOPEN2", "PSODA2", "PFRY2", "PENTREE2"]:
    print(c, int(df[c].notna().sum()), "/", len(df))

# --- How many stores lack wave-1 starting wage (NJ classification N=320) ---
print("\nNJ stores with missing WAGE_ST:", ((df.STATE == 1) & (df.WAGE_ST.isna())).sum())
print("NJ stores with WAGE_ST nonmissing:", ((df.STATE == 1) & (df.WAGE_ST.notna())).sum())
print("PA stores with WAGE_ST nonmissing:", ((df.STATE == 0) & (df.WAGE_ST.notna())).sum())

# --- STATUS2 coding exploration: look at rows with STATUS2 != 1 ---
print("\n=== Rows where STATUS2 != 1 ===")
sub = df[df.STATUS2 != 1]
print(sub[["SHEET", "STATE", "STATUS2", "TYPE2", "DATE2", "EMPFT2", "EMPPT2", "NMGRS2", "WAGE_ST2"]].to_string())
print("\n=== Rows where STATUS2 == 1 but wave-2 employment all missing ===")
mask = (df.STATUS2 == 1) & df[["EMPFT2", "EMPPT2", "NMGRS2"]].isna().all(axis=1)
print(df[mask][["SHEET", "STATE", "STATUS2", "TYPE2", "DATE2", "EMPFT2", "EMPPT2", "NMGRS2", "WAGE_ST2"]].to_string())

# --- FTE definition test ---
for fte_name, fte in [
    ("empft + 0.5*emppt + nmgrs", df["EMPFT"] + 0.5 * df["EMPPT"] + df["NMGRS"]),
    ("empft + 0.5*emppt", df["EMPFT"] + 0.5 * df["EMPPT"]),
]:
    fte1 = fte.rename(fte_name)
    t = pd.DataFrame({"FTE": fte1, "STATE": df["STATE"]})
    g = t.groupby("STATE")["FTE"].agg(["mean", "std", "count"])
    print(f"\n--- FTE = {fte_name} (wave 1) ---")
    print(g)
