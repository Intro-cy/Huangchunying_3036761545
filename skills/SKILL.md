---
name: ck94-replication
description: Regenerates the Card & Krueger (1994) minimum-wage DID replication — Tables 2–4, Figure 1, the Table-5 specification subset, and the independent extension — from the raw public survey data. Use when the user wants to reproduce the tables and figures of this project, rerun the analysis after a change, or verify the replication numbers against the published paper.
---

# CK94 Replication Skill

## Purpose

This skill regenerates every analysis output of the project
(*Minimum Wages and Employment: Replication and Extension of Card & Krueger,
1994*) from the single raw input `data/raw/public.csv`. It implements and
documents the sample-construction rules and variable definitions that were
empirically verified against the published paper, so that the pipeline is
auditable and the numbers reproducible.

## Inputs

- `data/raw/public.csv` — the public Card–Krueger survey data (410 restaurants:
  331 NJ, 79 eastern PA; Burger King, KFC, Roy Rogers, Wendy's; two waves:
  Feb–Mar 1992 and Nov–Dec 1992). Column layout documented in
  `references/data_dictionary.md`.
- Python ≥ 3.10 with `pandas`, `numpy`, `statsmodels`, `matplotlib`, `scipy`.

No other input is required; no manual edits to data or code are allowed
between steps.

## Steps

1. **Clean and construct variables** (`code/01_clean_data.py`): builds
   `data/processed/ck94_clean.csv` from the raw file. Key definitions
   (all verified against the paper):

   - `FTE = EMPFT + 0.5*EMPPT + NMGRS` (full-time-equivalent employment).
   - Wave-2 employment: 6 permanently closed stores (`STATUS2==3`) → 0;
     2 temporarily closed + 2 under renovation (`STATUS2 in {2,4,5}`) + 1
     refusal (`STATUS2==0`) → missing in the baseline convention.
   - `GAP = (5.05 − W1)/W1` for NJ stores with W1 < 5.05, else 0.
   - % full-time = `100*EMPFT/FTE`; wage classes: exactly $4.25 / $4.26–$4.99
     / ≥ $5.00.

2. **Tables 2–4 and Figure 1** (`code/02_table2.py`, `code/03_table3.py`,
   `code/04_table4.py`, `code/05_figure1.py`): means with SEs and t-stats,
   the five-row average-employment DID table, the reduced-form ΔFTE
   regressions (N = 357), and the two-panel starting-wage distribution figure.

3. **Independent extension** (`code/06_extension.py`): ownership/chain
   heterogeneity DID, within-PA placebo, and randomization inference
   (B = 10,000 permutations).

4. **Validation** (`code/07_spec_tests.py`): the Table-5 subset of
   specification tests (part-time weights, manager exclusion, shore-store
   exclusion, WLS, PA-only placebo).

5. **One-command end-to-end run**: `code/run_all.py` executes steps 1–4 and
   writes every output:

   ```
   python3 code/run_all.py
   ```

   or, equivalently, this skill's runner:

   ```
   bash skills/scripts/regenerate.sh
   ```

## Outputs

| Output | Path |
|---|---|
| Processed data | `data/processed/ck94_clean.csv` |
| Table 2 (means/SE/t) | `outputs/tables/table2.csv` |
| Table 3 (employment DID) | `outputs/tables/table3.csv` |
| Table 4 (ΔFTE regressions) | `outputs/tables/table4.csv` |
| Figure 1 data | `outputs/tables/figure1_data.csv` |
| Table 5 subset | `outputs/tables/table5_subset.csv` |
| Extension tables | `outputs/tables/extension_*.csv` |
| Figure 1 (PNG, 300 dpi) | `outputs/figures/figure1_replication.png` |
| Extension figures | `outputs/figures/extension_heterogeneity.png`, `outputs/figures/extension_ri.png` |
| Interactive dashboard | `outputs/figures/dashboard.html` |

## Verification (must pass before claiming success)

After a run, check the head-line numbers against the paper:

| Quantity | Expected (matches Card & Krueger 1994) |
|---|---|
| Wave-1 mean FTE | PA 23.33, NJ 20.44 |
| Balanced-sample DID (Table 3 row 4) | 2.75 (SE 1.34); temp-closed DID 2.51 (1.35) |
| Table 4, N | 357 |
| Table 4 NJ dummy, no controls | 2.33 (1.19); with controls 2.30 (1.20) |
| Table 4 GAP, no controls | 15.65 (6.08); with controls 14.92 (6.21) |
| Wave-2 NJ $5.05 share | ≈ 85.5% |
| Extension permutation p (DID) | 0.018 (B = 10,000) |

Documented data-version differences (6 fewer NJ wave-1 wages than the
authors' data; row-3 SEs; Table-4 dependent-variable mean) are discussed in
`report/empirical_report.md` §5 and are **not** to be "fixed".

## Troubleshooting

- `ModuleNotFoundError`: install dependencies (`pip install pandas numpy
  statsmodels matplotlib scipy`).
- Path errors: every script resolves paths relative to the repository root;
  run from the repository root, keep `data/raw/public.csv` in place.
- Randomized outputs: `06_extension.py` sets a fixed RNG seed; permutation
  p-values are stable to ±0.002 across runs.
