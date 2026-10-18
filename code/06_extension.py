"""06_extension.py — Independent extension: heterogeneity and inference credibility.

Economic question: Are the employment effects of the NJ minimum wage different for
company-owned vs franchised stores and across chains, and is the headline DID
inference credible under placebo and randomization checks?

Contents:
  A. DID by ownership (company-owned vs franchise) and by chain (balanced sample).
  B. Interaction regressions (Table-4 sample): NJ x COOWNED, NJ x chain.
  C. Within-Pennsylvania placebo DID (PA1 vs PA2 as pseudo-treated/control).
  D. Randomization inference: permutation distribution of the DID (balanced
     sample) and of the Table-4 NJ coefficient, vs conventional t inference.
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
from ck94_utils import load_clean_data, REPO, CHAIN_NAMES

OUT_T = REPO / "outputs" / "tables"
OUT_F = REPO / "outputs" / "figures"

df = load_clean_data()
df["d"] = df["FTE2"] - df["FTE1"]

bal = df[df.FTE1.notna() & df.FTE2.notna()].copy()            # balanced, N=384
s4 = df[(df.FTE1.notna() & df.FTE2.notna() & df.WAGE_ST.notna()
         & (df.WAGE_ST2.notna() | (df.STATUS2 == 3)))].copy()  # Table-4 sample, N=357

def did_se(a, b):
    return np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))

rows = []
def add(groupname, sub):
    nj = sub.loc[sub.STATE == 1, "d"]; pa = sub.loc[sub.STATE == 0, "d"]
    rows.append({"group": groupname, "n_NJ": len(nj), "n_PA": len(pa),
                 "dNJ": nj.mean(), "dPA": pa.mean(), "DID": nj.mean() - pa.mean(),
                 "se": did_se(nj, pa), "t": (nj.mean() - pa.mean()) / did_se(nj, pa)})

# --- A. Heterogeneity (balanced sample) ---
add("All stores", bal)
for own, lab in [(1, "Company-owned"), (0, "Franchise")]:
    add(lab, bal[bal.COOWNED == own])
for ch in sorted(bal["chain"].unique()):
    add(f"Chain: {CHAIN_NAMES[ch]}", bal[bal["chain"] == ch])

het = pd.DataFrame(rows)
het.to_csv(OUT_T / "extension_heterogeneity_means.csv", index=False)
print("\n=== A. DID by ownership and chain (balanced sample) ===")
print(het.round(3).to_string(index=False))

# --- B. Interaction regressions (Table-4 sample) ---
print("\n=== B. Interaction regressions (N=357) ===")
results = []
X1 = sm.add_constant(s4[["NJ", "COOWNED"]])
X1["NJxCOOWNED"] = s4["NJ"] * s4["COOWNED"]
m1 = sm.OLS(s4["d"], X1).fit()
print("dFTE ~ NJ + COOWNED + NJxCOOWNED")
print(f"  NJ: {m1.params['NJ']:.2f} ({m1.bse['NJ']:.2f}) | "
      f"NJxCOOWNED: {m1.params['NJxCOOWNED']:.2f} ({m1.bse['NJxCOOWNED']:.2f}) | "
      f"F(p) for interaction: {m1.pvalues['NJxCOOWNED']:.3f}")
results.append({"model": "NJ x COOWNED", "coef": m1.params["NJxCOOWNED"],
                "se": m1.bse["NJxCOOWNED"], "p": m1.pvalues["NJxCOOWNED"]})

# chain interactions (NJ x chain dummies; chain 4 = base)
X2 = sm.add_constant(s4[["NJ", "ch_2", "ch_3", "ch_4", "COOWNED"]])
for c in ["ch_2", "ch_3", "ch_4"]:
    X2[f"NJx{c}"] = s4["NJ"] * s4[c]
m2 = sm.OLS(s4["d"], X2).fit()
print("dFTE ~ NJ + chain + COOWNED + NJxchain")
for c in ["ch_2", "ch_3", "ch_4"]:
    k = f"NJx{c}"
    print(f"  {k}: {m2.params[k]:.2f} ({m2.bse[k]:.2f}) p={m2.pvalues[k]:.3f}")
    results.append({"model": f"NJ x {CHAIN_NAMES[int(c[-1])]} (vs Wendy's)",
                    "coef": m2.params[k], "se": m2.bse[k], "p": m2.pvalues[k]})
pd.DataFrame(results).to_csv(OUT_T / "extension_interactions.csv", index=False)

# --- C. Within-PA placebo ---
print("\n=== C. Within-PA placebo DID (PA1 vs PA2) ===")
pa = bal[bal.STATE == 0]
add("PA placebo (PA1 vs PA2)", pa.assign(STATE=np.where(pa["PA1"] == 1, 1, 0)))
placebo = pd.DataFrame(rows[-1:])
placebo.to_csv(OUT_T / "extension_placebo.csv", index=False)
print(placebo.round(3).to_string(index=False))

# --- D. Randomization inference ---
rng = np.random.default_rng(20261018)
B = 10_000

# D1: balanced-sample DID
d = bal["d"].values
n_treat = int(bal.STATE.sum())
did_obs = d[bal.STATE == 1].mean() - d[bal.STATE == 0].mean()
did_perm = np.empty(B)
for b in range(B):
    idx = rng.permutation(len(d))[:n_treat]
    did_perm[b] = d[idx].mean() - d[np.setdiff1d(np.arange(len(d)), idx, assume_unique=True)].mean()
p_ri = (np.abs(did_perm) >= abs(did_obs)).mean()
print(f"\n=== D. Randomization inference (B={B:,}) ===")
print(f"Observed DID (balanced): {did_obs:.3f}; permutation two-sided p = {p_ri:.4f}")

# conventional t-based p
t_obs = did_obs / did_se(bal.loc[bal.STATE == 1, "d"], bal.loc[bal.STATE == 0, "d"])
from scipy import stats
p_t = 2 * (1 - stats.t.cdf(abs(t_obs), df=min(len(bal.loc[bal.STATE==1]), len(bal.loc[bal.STATE==0])) - 1))
print(f"Conventional t: t={t_obs:.2f}, two-sided p~{p_t:.4f}")

# D2: Table-4 regression coefficient
Xc = sm.add_constant(s4["NJ"])
r_obs = sm.OLS(s4["d"], Xc).fit().params["NJ"]
b_perm = np.empty(B)
for b in range(B):
    idx = rng.permutation(len(s4))[:int(s4.STATE.sum())]
    y = s4["d"].values
    treat = np.zeros(len(s4)); treat[idx] = 1
    b_perm[b] = sm.OLS(y, sm.add_constant(treat)).fit().params[1]
p_ri4 = (np.abs(b_perm) >= abs(r_obs)).mean()
print(f"Table-4 NJ coeff: {r_obs:.3f}; permutation two-sided p = {p_ri4:.4f}")
pd.DataFrame({"stat": ["DID balanced", "Table4 NJ coef"],
              "obs": [did_obs, r_obs],
              "perm_p": [p_ri, p_ri4]}).to_csv(OUT_T / "extension_ri.csv", index=False)

# --- Figures ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# heterogeneity coefficient plot
fig, ax = plt.subplots(figsize=(7.5, 5))
groups = het["group"].tolist()
dids = het["DID"].values; ses = het["se"].values
x = np.arange(len(groups))
ax.errorbar(x, dids, yerr=1.96 * ses, fmt="o", color="black", capsize=3, lw=1.2)
ax.axhline(0, color="gray", lw=0.8, ls="--")
ax.set_xticks(x); ax.set_xticklabels(groups, rotation=30, ha="right", fontsize=8)
ax.set_ylabel("DID estimate (FTE change, NJ - PA)")
ax.set_title("Extension: DID estimates by ownership and chain (with 95% CIs)")
fig.tight_layout(); fig.savefig(OUT_F / "extension_heterogeneity.png", dpi=300)
print("Saved:", OUT_F / "extension_heterogeneity.png")

# permutation distribution
fig, ax = plt.subplots(figsize=(7.5, 5))
ax.hist(did_perm, bins=60, color="lightgray", edgecolor="black")
ax.axvline(did_obs, color="red", lw=2, label=f"Observed DID = {did_obs:.2f}")
ax.axvline(-did_obs, color="red", lw=1.5, ls="--")
ax.set_xlabel("Permuted DID (FTE, NJ - PA)"); ax.set_ylabel("Frequency")
ax.set_title(f"Randomization inference (B=10,000; two-sided p = {p_ri:.3f})")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(OUT_F / "extension_ri.png", dpi=300)
print("Saved:", OUT_F / "extension_ri.png")
