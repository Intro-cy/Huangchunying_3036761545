"""ck94_utils.py — Shared data-cleaning helpers for the Card & Krueger (1994) replication.

All scripts import load_clean_data() so that the sample construction and variable
definitions live in exactly one place (reproducibility requirement).

Variable conventions (verified against the paper and the public data):
- STATE: 1 = New Jersey (treated), 0 = Pennsylvania (control)
- FTE  = full-time-equivalent employment = EMPFT + 0.5*EMPPT + NMGRS
- Wave-2 employment: 6 permanently closed stores (STATUS2==3) -> 0;
  2 temporarily closed (STATUS2==2) + 2 under renovation (STATUS2 in {4,5})
  + 1 refusal (STATUS2==0) -> missing in the baseline convention.
- GAP  = (5.05 - W1)/W1 for NJ stores with W1 < 5.05, else 0 (and 0 for PA).
"""
import pandas as pd
import numpy as np
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INPUT = REPO / "data" / "raw" / "public.csv"
OUT_PROCESSED = REPO / "data" / "processed" / "ck94_clean.csv"

# Status codes in the public data (verified empirically)
STATUS_CLOSED = 3        # permanently closed (6 stores)
STATUS_TEMP = {2, 4, 5}  # temporarily closed (2) + under renovation (2)
STATUS_REFUSAL = 0       # refused wave-2 interview (1 store)
STATUS_OPEN = 1

CHAIN_NAMES = {1: "Burger King", 2: "KFC", 3: "Roy Rogers", 4: "Wendy's"}
REGION_NJ = ["NORTHJ", "CENTRALJ", "SOUTHJ"]
REGION_PA = ["PA1", "PA2"]


def load_clean_data(zerotemp: bool = False) -> pd.DataFrame:
    """Load public.csv and construct the analysis variables.

    zerotemp=True additionally sets wave-2 FTE to 0 for the four temporarily
    closed / under-renovation stores (Table 3 row 5 / Table 5 row 2 convention).
    """
    df = pd.read_csv(INPUT)

    df["FTE1"] = df["EMPFT"] + 0.5 * df["EMPPT"] + df["NMGRS"]          # wave 1
    fte2 = df["EMPFT2"] + 0.5 * df["EMPPT2"] + df["NMGRS2"]              # wave 2 raw

    # baseline: closed -> 0; temp/renov/refusal -> missing
    df["FTE2"] = np.where(df["STATUS2"] == STATUS_CLOSED, 0.0, fte2)
    df.loc[df["STATUS2"].isin(STATUS_TEMP | {STATUS_REFUSAL}), "FTE2"] = np.nan

    # alternate: also set temp/renov to 0
    df["FTE2_zerotemp"] = df["FTE2"].copy()
    df.loc[df["STATUS2"].isin(STATUS_TEMP), "FTE2_zerotemp"] = 0.0

    df["dFTE"] = df["FTE2"] - df["FTE1"]                                 # baseline change
    df["dFTE_zerotemp"] = df["FTE2_zerotemp"] - df["FTE1"]

    # GAP (Table 4) : proportional wage increase needed to reach $5.05
    gap = np.where(df["STATE"] == 1, (5.05 - df["WAGE_ST"]) / df["WAGE_ST"], 0.0)
    gap = np.where(df["WAGE_ST"] >= 5.05, 0.0, gap)                      # NJ W1 >= 5.05 -> 0
    df["GAP"] = np.where(df["WAGE_ST"].isna(), np.nan, gap)

    # wave-1 wage classes (Table 3, cols iv-vi)
    df["wage_class"] = np.nan
    df.loc[(df["WAGE_ST"] == 4.25), "wage_class"] = 1                    # exactly 4.25
    df.loc[(df["WAGE_ST"] > 4.25) & (df["WAGE_ST"] < 5.00), "wage_class"] = 2
    df.loc[df["WAGE_ST"] >= 5.00, "wage_class"] = 3

    # chain dummies (3 dummies, chain 4 = base); keep original chain id too
    df["chain"] = df["CHAIN"].astype(int)
    df = pd.get_dummies(df, columns=["CHAIN"], prefix="ch", drop_first=True, dtype=float)

    # region dummies (base: SOUTHJ for NJ? -> handled by caller as needed)
    df["NJ"] = df["STATE"].astype(float)
    df["COOWNED"] = df["CO_OWNED"].astype(float)

    df.to_csv(OUT_PROCESSED, index=False)
    return df


def se_mean(x: pd.Series) -> float:
    """Standard error of the mean."""
    x = x.dropna()
    if len(x) < 2:
        return np.nan
    return x.std(ddof=1) / np.sqrt(len(x))


def tstat_two_sample(a: pd.Series, b: pd.Series) -> float:
    """Two-sample t statistic for difference of means (unequal variances)."""
    a, b = a.dropna(), b.dropna()
    if len(a) < 2 or len(b) < 2:
        return np.nan
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return (a.mean() - b.mean()) / se


def fmt_se(coef: float, se: float) -> str:
    return f"{coef:.2f}\n({se:.2f})"
