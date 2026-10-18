# Data dictionary — `data/raw/public.csv` → analysis variables

Raw file: `public.csv`, 410 rows × 46 columns (Card & Krueger 1994 public
replication data, Princeton). All analysis variables are constructed by
`code/ck94_utils.py` (single source of definitions).

| Raw variable | Meaning | Analysis variable |
|---|---|---|
| `STATE` | 1 = New Jersey (treated), 0 = Pennsylvania (control) | `NJ` |
| `CHAIN` | 1 = Burger King, 2 = KFC, 3 = Roy Rogers, 4 = Wendy's | chain dummies (Wendy's = base) |
| `CO_OWNED` | 1 = company-owned, 0 = franchise | `COOWNED` |
| `SOUTHJ, CENTRALJ, NORTHJ, SHORE` | NJ region dummies | used in Table 4 (v) |
| `PA1, PA2` | PA regions (Allentown–Easton; Philadelphia suburbs) | placebo DID split |
| `NCALLS` | call-backs needed for wave-1 interview | Table 5 row 8 (exclude >2) |
| `EMPFT, EMPPT, NMGRS` | wave-1 full-time, part-time, managers | `FTE = EMPFT + 0.5·EMPPT + NMGRS` |
| `WAGE_ST` | wave-1 starting wage | wage classes, `GAP` |
| `BONUS` | recruiting bonus offered | Table 2 row |
| `HRSOPEN` | weekday hours open | Table 2 row |
| `PSODA, PFRY, PENTREE` | prices: medium soda, small fries, entrée | full meal price = sum |
| `STATUS2` | wave-2 status: 1 open, 3 permanently closed, 2 temporarily closed, 4/5 under renovation, 0 refusal | FTE2 handling |
| `EMPFT2, EMPPT2, NMGRS2, WAGE_ST2` | wave-2 counterparts | FTE2, wave-2 wage |
| — | — | `GAP = (5.05 − W1)/W1` for NJ, W1 < 5.05, else 0 |

## Sample conventions (all verified against the paper)

- Balanced sample (per-store ΔFTE): 384 stores (309 NJ, 75 PA).
- Table-4 regression sample: FTE in both waves + wave-1 wage + (wave-2 wage
  or permanent closure) → **N = 357**, exactly as in the paper.
- Wave-2 employment: `STATUS2==3` → 0; `STATUS2 in {2,4,5}` and `0` → missing
  (baseline), 0 in the temp-closed-alternate series.
