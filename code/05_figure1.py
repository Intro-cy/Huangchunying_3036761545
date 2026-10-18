"""05_figure1.py — Replicate Figure 1 of CK (1994): Distribution of starting wage rates,
Feb 1992 (wave 1) and Nov 1992 (wave 2), New Jersey vs Pennsylvania.

Bins: 10-cent wage ranges labelled $4.25 ... $5.55, plus a top-open bin (>= $5.55).
Y axis: percent of stores. NJ solid bars, PA hatched bars (as in the original).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from ck94_utils import load_clean_data, REPO

OUT_FIG = REPO / "outputs" / "figures" / "figure1_replication.png"
OUT_CSV = REPO / "outputs" / "tables" / "figure1_data.csv"

df = load_clean_data()
edges = np.linspace(4.25, 5.55, 14)               # 14 bins of width 0.10: 4.25..5.55
labels = [f"{e:.2f}" for e in edges]

def pct_bins(col, state):
    """Percent of stores in each bin for a given wage column and state."""
    w = df.loc[(df.STATE == state) & df[col].notna(), col]
    idx = np.clip(np.searchsorted(edges, w.values, side="right") - 1, 0, len(edges) - 1)
    c = np.zeros(len(edges))
    for i in idx:
        c[i] += 1
    return 100 * c / len(w)

fig, axes = plt.subplots(2, 1, figsize=(8.5, 9), sharex=True)
xpos = np.arange(len(labels))
width = 0.38

for ax, col, title in [(axes[0], "WAGE_ST", "February 1992"),
                       (axes[1], "WAGE_ST2", "November 1992")]:
    nj, pa = pct_bins(col, 1), pct_bins(col, 0)
    ax.bar(xpos - width / 2, nj, width, color="black", label="New Jersey")
    ax.bar(xpos + width / 2, pa, width, color="white", edgecolor="black",
           hatch="////", label="Pennsylvania")
    ax.set_title(title, fontsize=12)
    ax.set_ylabel("Percent of Stores", fontsize=10)
    ax.legend(frameon=False, fontsize=9)

axes[1].set_xticks(xpos)
axes[1].set_xticklabels(labels, rotation=45, fontsize=8)
axes[1].set_xlabel("Wage Range", fontsize=10)
fig.suptitle("FIGURE 1 — Distribution of Starting Wage Rates (replication)", fontsize=12, y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(OUT_FIG, dpi=300, bbox_inches="tight")
print("Saved:", OUT_FIG)

d = pd.DataFrame({"bin": labels,
                  "NJ_w1": pct_bins("WAGE_ST", 1), "PA_w1": pct_bins("WAGE_ST", 0),
                  "NJ_w2": pct_bins("WAGE_ST2", 1), "PA_w2": pct_bins("WAGE_ST2", 0)})
d.to_csv(OUT_CSV, index=False)
print("Saved:", OUT_CSV)
print(d.round(2).to_string(index=False))
