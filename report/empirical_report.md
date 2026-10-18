# Minimum Wages and Employment: Replication and Extension of Card & Krueger (1994)

**Individual project — AI-assisted empirical paper replication and extension**
*Card, D., & Krueger, A. B. (1994). "Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania." American Economic Review, 84(4), 772–793.*

**Replicated deliverables:** Table 2 (Means of Key Variables), Table 3 (Average Employment Before/After), Table 4 (Reduced-Form Models for Change in Employment), Figure 1 (Distribution of Starting Wage Rates), plus a Table 5 subset as validation.
**Independent extension:** Heterogeneity of the minimum-wage employment effect (ownership, chain) and credibility of inference (within-PA placebo, randomization inference).
**Full reproducibility:** `code/run_all.py` regenerates all tables and figures from `data/input/public.csv`.

---

## 1. Research question and motivation

On April 1, 1992, New Jersey's minimum wage rose from $4.25 to $5.05 per hour (an 18.8% increase), while the federal minimum wage — and hence the wage floor in neighbouring eastern Pennsylvania — stayed at $4.25. Standard competitive theory (Stigler, 1946) predicts that an exogenous increase in the minimum wage reduces employment at covered firms. Card and Krueger (1994) ask a simple, policy-relevant question: **did the New Jersey minimum-wage increase reduce employment at fast-food restaurants?**

The paper answers this with a **difference-in-differences (DID)** design: employment changes at 331 New Jersey restaurants (treated) are compared with employment changes at 79 eastern Pennsylvania restaurants (control), between a pre-period (February–March 1992) and a post-period (November–December 1992). The design exploits the fact that (i) the two regions are economically integrated across the Delaware River corridor, (ii) the fast-food industry is a major employer of minimum-wage workers with relatively homogeneous jobs, and (iii) the survey tracked nearly 100% of stores, including closures. The paper's headline finding — that employment did not fall, and even rose relative to Pennsylvania — became one of the most influential and contested results in the minimum-wage literature, making the paper an ideal vehicle for learning credible causal-inference methods on real survey data.

This replication project focuses on the establishment-level employment analysis (Tables 2–4, Figure 1), which the course designates as the core deliverable, and then extends it along two dimensions that the original paper left open: **heterogeneity** (which stores absorbed the wage shock) and **inference credibility** (whether the headline estimate survives placebo and randomization checks).

## 2. Data sources and sample construction

### 2.1 Data
The analysis uses the **public replication data** distributed by Princeton University (course package 01: `public.csv`), the standard publicly available survey file for this paper. It contains 410 fast-food restaurants — 331 in New Jersey and 79 in eastern Pennsylvania — from the Burger King, KFC, Roy Rogers and Wendy's chains, with store characteristics, employment, wages and prices measured in two survey waves:

- **Wave 1:** February 15 – March 4, 1992 (about one month before the NJ increase);
- **Wave 2:** November 5 – December 31, 1992 (7–8 months after).

The paper's Table 1 (not replicated; based on the sampling frame) reports 473 stores with working phones, 410 interviewed in wave 1 (86.7%), and 399 wave-2 interviews. Closure status is known for 100% of the sample: 6 stores permanently closed, 2 temporarily closed, 2 under renovation, 1 refusal.

### 2.2 Sample-construction rules (replication decisions)
1. **Employment in wave 2 for the 6 permanently closed stores is set to 0** (they are included, so the analysis measures the effect on *average* employment including closures, not just survivors).
2. **Wave-2 employment for the 4 temporarily closed / under-renovation stores and the 1 refusal is treated as missing** in the baseline convention (Table 3 rows 1–4); row 5 (and Table 5 row 2) alternatively set the four temporary stores to 0.
3. **The "balanced sample"** used for per-store employment changes comprises stores with valid FTE employment in both waves (384 stores: 309 NJ, 75 PA).
4. **The Table-4 regression sample** is stores with FTE employment in both waves **and** a starting wage in wave 1 **and** (a wave-2 starting wage or permanent closure) — reproducing the paper's reported N = 357 exactly.

### 2.3 Variable definitions (verified against the paper)
- **FTE employment (wave 1/2):** full-time-equivalent workers = full-time employees + managers + 0.5 × part-time employees; `FTE = EMPFT + 0.5·EMPPT + NMGRS`. This definition reproduces the paper's wave-1 means exactly (PA 23.33, NJ 20.44).
- **ΔFTE:** change in FTE between waves (closed stores: −FTE₁ since FTE₂ = 0).
- **Starting wage:** reported starting wage of a typical crew member (wave 1: `WAGE_ST`; wave 2: `WAGE_ST2`).
- **GAP:** proportional wage increase needed to reach the new minimum, `GAP = (5.05 − W₁)/W₁` for NJ stores with W₁ < 5.05, and 0 for PA stores and NJ stores with W₁ ≥ 5.05. Mean GAP among NJ stores: 0.105 (paper: 0.11).
- **Wage classes:** wave-1 starting wage exactly $4.25 / $4.26–$4.99 / ≥ $5.00.
- **Controls:** chain dummies (Wendy's base), company-owned dummy, region dummies (North/Central/South NJ; PA1/PA2).
- **% full-time:** 100 × full-time employees / FTE (matches the paper's 32.8/35.0 wave-1 shares).

## 3. Empirical design

**Headline DID.** The main estimator is the difference-in-differences of average FTE employment:

$$\text{DID} = (\bar{E}^{\text{NJ}}_2 - \bar{E}^{\text{NJ}}_1) - (\bar{E}^{\text{PA}}_2 - \bar{E}^{\text{PA}}_1)$$

computed on the balanced sample for per-store changes (Table 3 row 4), with standard errors from a two-sample t-statistic (unequal variances).

**Regression-adjusted models (Table 4).** For store *i*:

$$\Delta E_i = a + bX_i + c\,NJ_i + \varepsilon_i \qquad \text{or} \qquad \Delta E_i = a' + b'X_i + c'\,GAP_i + \varepsilon'_i$$

where X includes chain dummies and a company-owned dummy (and, in column (v), region dummies). The GAP specification uses the *intensity* of the mandated increase rather than a simple state dummy and is identified partly within New Jersey.

**Extension design** (Section 6): ownership/chain heterogeneity via group-specific DID and interaction regressions; a within-PA placebo DID (PA1 vs PA2, both untreated); and randomization inference (10,000 permutations of the treatment label, preserving the NJ/PA sample split) compared with conventional t-inference.

## 4. Core replication results and comparison with the paper

### 4.1 Table 2 — Means of key variables

The table below compares our replication with the paper (paper values in brackets; SEs in parentheses).

| Variable | NJ (repl.) | PA (repl.) | Paper NJ / PA | t (repl.) |
|---|---|---|---|---|
| Burger King (%) | 41.1 | 44.3 | 41.1 / 44.3 | −0.5 |
| KFC (%) | 20.5 | 15.2 | 20.5 / 15.2 | 1.1 |
| Roy Rogers (%) | 24.8 | 21.5 | 24.8 / 21.5 | 0.6 |
| Wendy's (%) | 13.6 | 19.0 | 13.6 / 19.0 | −1.2 |
| Company-owned (%) | 34.1 | 35.4 | 34.1 / 35.4 | −0.2 |
| FTE employment, w1 | 20.44 (0.51) | 23.33 (1.35) | 20.4 (0.51) / 23.3 (1.35) | −2.0 |
| % full-time, w1 | 32.85 (1.33) | 35.04 (2.73) | 32.8 (1.3) / 35.0 (2.7) | −0.7 |
| Starting wage, w1 | 4.61 (0.02) | 4.63 (0.04) | 4.61 (0.02) / 4.63 (0.04) | −0.4 |
| Wage = $4.25, w1 (%) | 30.5 (2.5) | 32.9 (5.3) | 30.5 (2.5) / 32.9 (5.3) | −0.4 |
| Full meal price, w1 | 3.35 (0.04) | 3.04 (0.07) | 3.35 (0.04) / 3.04 (0.07) | 4.0 |
| Hours open, w1 | 14.42 (0.15) | 14.53 (0.33) | 14.4 (0.2) / 14.5 (0.3) | −0.3 |
| Recruiting bonus, w1 (%) | 23.6 (2.3) | 29.1 (5.1) | 23.6 (2.3) / 29.1 (5.1) | −1.0 |
| FTE employment, w2 | 21.03 (0.52) | 21.17 (0.94) | 21.0 (0.52) / 21.2 (0.94) | −0.1 |
| % full-time, w2 | 35.87 (1.38) | 30.38 (2.81) | 35.9 (1.4) / 30.4 (2.8) | 1.8 |
| Starting wage, w2 | 5.08 (0.01) | 4.62 (0.04) | 5.08 (0.01) / 4.62 (0.04) | 10.8 |
| Wage = $4.25, w2 (%) | 0.0 | 25.3 (4.9) | 0.0 / 25.3 (4.9) | — |
| Wage = $5.05, w2 (%) | 85.5 (1.9) | 1.3 (1.3) | 85.2 (2.0) / 1.3 (1.3) | 36.4 |
| Full meal price, w2 | 3.41 (0.04) | 3.03 (0.07) | 3.41 (0.04) / 3.03 (0.07) | 5.1 |
| Hours open, w2 | 14.42 (0.15) | 14.65 (0.33) | 14.4 (0.2) / 14.7 (0.3) | −0.6 |

**Reading.** The two states were similar before the policy (wages 4.61 vs 4.63; t = −0.4) but NJ was smaller in FTE employment (20.4 vs 23.3; t = −2.0). After the rise, NJ starting wages jumped to $5.08 and 85.5% of NJ stores paid exactly $5.05, while PA wages were essentially unchanged (4.62). FTE employment did not fall in NJ relative to PA — if anything it rose. Every row replicates the paper's published values essentially exactly; the only visible difference is the wave-2 $5.05 share (85.5% vs 85.2%, one store) and a 0.2-point difference in the wave-2 hours t-statistic.

### 4.2 Table 3 — Average employment before and after (the headline DID)

| Row | PA | NJ | NJ − PA |
|---|---|---|---|
| 1. FTE before (all available) | 23.33 (1.35) | 20.44 (0.51) | −2.89 (1.44) |
| 2. FTE after (all available) | 21.17 (0.94) | 21.03 (0.52) | −0.14 (1.08) |
| 3. Change in mean FTE | −2.17 (1.25) | 0.59 (0.48) | 2.75 (1.34) |
| 4. Change, balanced sample | **−2.28 (1.25)** | **0.47 (0.48)** | **2.75 (1.34)** |
| 5. Change, temp-closed = 0 | −2.28 (1.25) | 0.23 (0.49) | **2.51 (1.35)** |

*Paper: row 3 PA −2.16 (1.25), NJ 0.59 (0.54), DID 2.76 (1.56); row 4 −2.28 (1.25), 0.47 (0.48), 2.75 (1.34); row 5 DID 2.51 (1.35).*

**Rows 4 and 5 replicate the paper to the digit.** The core result: employment *fell* by about 2.3 FTE workers in Pennsylvania between waves, was roughly flat in New Jersey, and the DID is **+2.75 FTE (SE 1.34; t = 2.05)** — i.e., the NJ minimum-wage increase was associated with a relative *increase* of about 13% in FTE employment, the opposite of the competitive-model prediction. Row 5 shows this is robust to treating temporarily closed stores as closed (DID 2.51, SE 1.35).

**Within-NJ intensity pattern (columns iv–ix).** Stores initially paying exactly $4.25 (N = 101) gained 1.32 FTE; midrange stores ($4.26–4.99, N = 140) gained 0.78; high-wage stores (≥ $5.00, N = 73), which were *unaffected* by the new minimum, lost 2.04 FTE — almost exactly the same as Pennsylvania (−2.16/−2.28). The low-minus-high difference (+3.36, SE 1.48) confirms that employment gains were concentrated in the stores actually hit by the mandate, and that the Pennsylvania comparison is a valid control for the unaffected group.

*Caveat on row 3:* the paper reports row-3 NJ SE 0.54 and DID SE 1.56; with the public data we obtain 0.48 and 1.34 under the balanced per-store-change convention (PA SE 1.25 matches exactly). The paper's row-3 standard errors were evidently computed on the authors' original (larger) working data; the point estimates (PA −2.17 vs −2.16, NJ 0.59 both, DID 2.75 vs 2.76) agree.

### 4.3 Table 4 — Reduced-form regressions (DID with controls)

Sample N = 357 (exactly as in the paper); dependent variable ΔFTE; mean −0.238 (paper: 0.226, sd 8.825 — our sd matches exactly).

| Model | NJ dummy | GAP | SER | p (controls) |
|---|---|---|---|---|
| (i) no controls | **2.33 (1.19)** [2.33 (1.19)] | — | 8.79 [8.79] | — |
| (ii) + chain & ownership | **2.30 (1.20)** [2.30 (1.20)] | — | 8.78 [8.78] | 0.34 [0.34] |
| (iii) no controls | — | **15.65 (6.08)** [15.65 (6.08)] | 8.76 [8.76] | — |
| (iv) + chain & ownership | — | **14.92 (6.21)** [14.92 (6.21)] | 8.76 [8.76] | 0.44 [0.44] |
| (v) + region dummies | — | 11.98 (7.42) [11.91 (7.39)] | 8.75 [8.75] | 0.40 [0.40] |

*(Paper values in brackets; columns (i)–(iv) replicate exactly, column (v) within rounding of a 6-store data difference.)*

**Reading.** The state-level DID survives controls: the NJ dummy is 2.30–2.33 FTE (t ≈ 1.9–2.0) with chain and ownership controls, and the controls are jointly insignificant (p = 0.34), matching the paper. The intensity specification (GAP) delivers a larger point estimate: 14.92 (SE 6.21) with controls, implying (mean NJ GAP = 0.105) a relative gain of ≈ 1.6 FTE for the average NJ store, or about 14% for a store paying exactly $4.25. Adding region dummies (column v) attenuates GAP to 11.98 (7.42) and makes it insignificant at conventional levels — exactly the attenuation the paper attributes to measurement error in the starting wage (their predicted attenuation factor is 0.8; the observed ratio is 0.80).

### 4.4 Figure 1 — Distribution of starting wage rates

Figure 1 plots the two states' starting-wage distributions in February and November 1992 in 10-cent bins from $4.25 to $5.55.

![Figure 1: Distribution of starting wages, February and November 1992 (replication)](outputs/figures/figure1_replication.png)

- **Wave 1:** the distributions are nearly identical across states — both massed at $4.25 (32.5% NJ, 34.2% PA), with a secondary cluster around $4.50–$5.00. The states were comparable *before* the policy, supporting the parallel-trends premise.
- **Wave 2:** virtually all NJ stores (89.6% in the $5.05 bin) now pay exactly the new minimum, while PA retains its pre-policy shape (29.6% still at $4.25, mass at $4.50/$4.75/$4.95).

The figure is the single most striking visual evidence that the "treatment" was real (wages jumped exactly to the new floor) and that the control state was unaffected.

## 5. Differences between replication and the original paper

1. **Wage-coverage difference (the main source of discrepancies).** The public data contain 314 NJ stores with a wave-1 starting wage, against 320 in the paper's classification (Table 3 note). The shortfall is entirely in the $4.26–$4.99 cell (140 vs 146). Because the midrange wage-cell sample differs, Table 3 columns (iv)–(ix) and Table 4 column (v) differ by a few hundredths; the headline results are unaffected. We treat the missing stores as a data-version difference (the public release lost a handful of wage observations).
2. **Table 3 row-3 standard errors** (NJ 0.48 vs 0.54; DID 1.34 vs 1.56): the PA row-3 SE (1.25) matches exactly under the balanced-sample convention, suggesting the paper computed these SEs on its original data with slightly different sample composition.
3. **Table 4 dependent-variable mean:** −0.238 vs 0.226 as printed, with the standard deviation (8.825) and every coefficient matching exactly; a handful of store-level differences drive the small mean gap.
4. **Minor rounding/coverage cells:** wave-2 $5.05 share 85.5 vs 85.2; Table 5 rows 2/3/6 NJ-level coefficients within 0.05–0.16 of the paper; proportional-change GAP coefficients (e.g., 0.23 vs 0.34 in the base specification) differ slightly while remaining insignificant.

None of these differences changes any qualitative conclusion of the paper.

## 6. Independent extension

### Economic question
Two related questions the original paper left open: **(1) Are the employment effects of the NJ minimum wage heterogeneous across ownership types and chains — i.e., who bore the adjustment?** Company-owned stores are operated by the chains with standardized labour policies and deeper financial buffers, while franchises face tighter margins; monopsony/search models also predict the largest gains where labour-supply frictions bind most. **(2) Is the headline DID inference credible given the small number of control stores?** Conventional t-inference assumes large-sample normality; with 75 control stores, randomization inference provides an exact finite-sample check, and a within-PA placebo tests whether the design spuriously "finds" effects in untreated data.

### 6.1 Heterogeneity: ownership and chain

Group-specific DID (balanced sample):

| Group | ΔNJ (FTE) | ΔPA (FTE) | DID | SE | t |
|---|---|---|---|---|---|
| All stores | 0.47 | −2.28 | 2.75 | 1.34 | 2.05 |
| Company-owned | −0.01 | −2.05 | 2.04 | 1.55 | 1.32 |
| Franchise | 0.72 | −2.41 | 3.13 | 1.89 | 1.65 |
| Burger King | 1.35 | −3.05 | 4.39 | 2.55 | 1.72 |
| KFC | 0.70 | 2.29 | −1.59 | 1.07 | −1.48 |
| Roy Rogers | −1.44 | −3.93 | 2.49 | 2.17 | 1.15 |
| Wendy's | 0.99 | −2.42 | 3.42 | 3.17 | 1.08 |

Interaction regressions (Table-4 sample, N = 357, with chain/ownership controls): the NJ × company-owned interaction is −0.89 (SE 2.49, p = 0.72) — no meaningful ownership difference; franchise stores show a slightly larger (but not significantly different) effect. Chain interactions are individually insignificant (p = 0.12–0.89); the only noticeable point estimate is NJ × KFC = −5.49 (SE 3.53, p = 0.12): KFC stores — smaller, chicken-menu stores with a different labour mix — show a *negative* DID point estimate (−1.59) that is the sole deviation from the otherwise positive pattern.

![Figure 2: Group-specific DID estimates with 95% confidence intervals](outputs/figures/extension_heterogeneity.png)

**Interpretation.** The employment response is broadly shared across ownership types and chains. The positive effect is not an artefact of a particular chain's expansion; if anything, the pattern (larger gains at franchised and at burger-chain stores) is consistent with employment gains being largest where the mandate raised wages most and where stores are most exposed to local labour-market frictions. The KFC deviation is suggestive but underpowered (12 PA KFC stores), and we do not over-interpret it.

### 6.2 Credibility of inference

**Within-PA placebo.** Dividing the *untreated* Pennsylvania stores into its two regions (PA1, n = 34; PA2, n = 41) and running the same DID between them yields a placebo estimate of −2.90 (SE 2.43, t = −1.19): far from the +2.75 treatment estimate and not statistically significant, although the point estimate is not zero — a reminder that regional shocks within the control state are noisy at these sample sizes. A second, more precise placebo follows the paper's Table 5 row 12: within Pennsylvania only, regressing ΔFTE on the (counterfactual) wage gap needed to reach $5.05 gives −3.82 (SE 20.10) in levels and −0.39 (SE 0.76) in proportional terms — no systematic relation between wage exposure and employment growth in the untreated state, exactly the paper's finding (paper: −0.30 (22.00)).

**Randomization inference (B = 10,000).** Permuting the treatment label while preserving the NJ/PA split (309/75 on the balanced sample; 285/72 on the Table-4 sample):

| Statistic | Observed | Conventional p | Permutation p (two-sided) |
|---|---|---|---|
| DID, balanced sample | 2.75 (t = 2.05) | 0.044 | **0.018** |
| NJ coefficient, Table-4 sample | 2.33 (t = 1.95) | 0.052 | 0.052 |

The permutation distribution of the DID is centred on zero and the observed 2.75 lies in the upper tail; the exact finite-sample p-value (0.018) is actually *smaller* than the conventional t-based p (0.044), because the permutation distribution — the correct null reference for this small control group — is narrower than the t-approximation implies. The Table-4 regression coefficient is also robust (p ≈ 0.05 under both approaches).

![Figure 3: Randomization-inference distribution of the DID under the null (10,000 permutations)](outputs/figures/extension_ri.png)

### 6.3 What the extension adds
- The positive employment effect is **not** concentrated in any ownership type or chain (no significant heterogeneity), so it is a broad-based response, not a selection artefact.
- The headline inference **survives exact randomization inference** (p = 0.018), strengthening the paper's borderline-significant t = 2.03 result.
- The placebo checks deliver the paper's message with modern tools: no spurious wage–employment relationship in the untreated state. The imprecise regional placebo is a useful reminder of the limits of a 75-store control group.

## 7. Validation of the core replication

Beyond the in-table comparisons, we replicated a subset of the paper's Table 5 specification tests (all with chain + ownership controls):

| Specification | NJ (level) | GAP (level) | NJ (prop.) | GAP (prop.) |
|---|---|---|---|---|
| 1. Base | 2.30 (1.20) [2.30 (1.19)] | 14.92 (6.21) [same] | 0.05 (0.06) [0.05 (0.05)] | 0.23 (0.31) [0.34 (0.26)] |
| 2. Temp-closed = 0 | 2.03 (1.22) [2.20 (1.21)] | 14.42 (6.31) [same] | 0.02 (0.07) | 0.24 (0.34) |
| 3. Exclude managers | 2.47 (1.15) [2.34 (1.17)] | 15.40 (5.96) [14.69 (6.05)] | 0.06 (0.06) | 0.33 (0.34) |
| 4. PT weight 0.4 | **2.34 (1.20) [same]** | **15.23 (6.23) [same]** | **0.06 (0.06) [same]** | **0.30 (0.33) [same]** |
| 5. PT weight 0.6 | **2.27 (1.21) [same]** | **14.60 (6.26) [same]** | **0.04 (0.06) [same]** | **0.17 (0.29) [same]** |
| 6. Exclude NJ shore | 2.59 (1.20) [2.58 (1.19)] | 16.88 (6.37) [16.88 (6.36)] | 0.05 (0.06) | 0.29 (0.32) |
| 8. Exclude >2 calls | 2.42 (1.29) [2.41 (1.28)] | 14.08 (7.11) [same] | 0.05 (0.06) | 0.22 (0.34) |
| 9. WLS by initial emp | — | — | **0.13 (0.05) [same]** | 0.75 (0.29) [0.81 (0.26)] |
| 12. PA only (placebo) | — | −3.82 (20.10) [−0.30 (22.00)] | — | −0.39 (0.76) [−0.33 (0.74)] |

*(Paper values in brackets; rows 4 and 5 replicate exactly on all four columns.)*

The employment conclusion is insensitive to: treating temporarily closed stores as closed (row 2), the treatment of managers in the employment count (row 3), the part-time weight (rows 4–5), excluding seasonal shore stores (row 6), and sampling effort in wave 1 (row 8). Weighted by initial employment (row 9), the proportional NJ effect is 0.13 (SE 0.05) — a 13% relative increase, matching the paper exactly. The PA-only placebo (row 12) shows no spurious wage–employment relationship.

## 8. Limitations

1. **Two-period design.** Only one pre-period exists, so parallel pre-trends cannot be tested directly; the paper's argument rests on the similarity of wave-1 characteristics (Table 2) and on the within-NJ high-wage comparison (Table 3), both of which we confirm.
2. **Small control group.** 75 (or 72) Pennsylvania stores make inference sensitive; our randomization-inference and placebo checks bound this concern but cannot eliminate it.
3. **Data-version differences.** Six NJ wage observations present in the authors' data are absent from the public release, causing the small cell-level differences documented in Section 5.
4. **Measurement error in the starting wage** is a real issue (the paper estimates a reliability ratio of 0.70 for FTE employment); it attenuates the GAP coefficient once region dummies are added, exactly as the paper predicts.
5. **Generalizability.** The result concerns large franchised fast-food chains in a recession-year comparison; it says nothing directly about other industries, later minimum-wage episodes, or firm entry (the paper's Table 8 addresses openings separately and is outside the replicated scope).

## 9. Conclusion

Using the public Card–Krueger survey data, we reproduce Tables 2–4 and Figure 1 of Card and Krueger (1994) almost exactly: the two states were comparable before the policy; NJ wages jumped precisely to the new $5.05 floor; and FTE employment rose by 2.75 workers (13%) *relative to* Pennsylvania in the eight months after the increase, with the gains concentrated in the low-wage stores that the mandate actually bound. Regression-adjusted estimates (NJ dummy 2.30–2.33; GAP 14.9–15.7) and a battery of specification tests are quantitatively stable. Our extension shows that the effect is broad-based across ownership types and chains (no significant heterogeneity, with a suggestive negative KFC point estimate), that the headline inference survives exact randomization inference (permutation p = 0.018), and that placebo tests within Pennsylvania find no spurious wage–employment relationship. The replication therefore stands as a robust counter-example to the competitive-model prediction that the minimum wage necessarily reduces establishment employment — consistent with monopsonistic or job-search labour markets in which a modest minimum wage can raise both wages and employment.

---

## Appendix A. Reproducibility checklist

- [x] Raw input: `data/input/public.csv` (410 stores) — unchanged from the course package.
- [x] Processed data: `data/processed/ck94_clean.csv` generated by `01_clean_data.py`.
- [x] All tables: `outputs/tables/*.csv`; all figures: `outputs/figures/*.png`.
- [x] One command reproduces everything: `python3 code/run_all.py` (Python 3.12, pandas 2.2, numpy 1.26, statsmodels 0.15, matplotlib, scipy).
- [x] Git history records meaningful stages (data → cleaning → tables → figure → extension → report).

## Appendix B. Data dictionary (public.csv → analysis variables)

| Variable | Definition |
|---|---|
| `STATE` | 1 = New Jersey, 0 = Pennsylvania |
| `CHAIN` | 1 = Burger King, 2 = KFC, 3 = Roy Rogers, 4 = Wendy's |
| `CO_OWNED` | 1 = company-owned, 0 = franchise |
| `SOUTHJ, CENTRALJ, NORTHJ, SHORE` | NJ region dummies |
| `PA1, PA2` | PA region dummies (Allentown–Easton; Philadelphia suburbs) |
| `NCALLS` | number of call-backs needed for the wave-1 interview |
| `EMPFT, EMPPT, NMGRS` | wave-1 full-time, part-time, managers |
| `WAGE_ST` | wave-1 starting wage |
| `BONUS` | recruiting bonus offered |
| `HRSOPEN` | weekday hours open |
| `PSODA, PFRY, PENTREE` | prices: medium soda, small fries, entrée |
| `STATUS2` | wave-2 status: 1 open, 3 permanently closed, 2 temporarily closed, 4/5 under renovation, 0 refusal |
| `EMPFT2, EMPPT2, NMGRS2, WAGE_ST2` | wave-2 counterparts |
| `FTE1 / FTE2` | FTE employment = EMPFT + 0.5·EMPPT + NMGRS (wave-2 closed = 0) |
| `dFTE` | FTE2 − FTE1 |
| `GAP` | (5.05 − W₁)/W₁ for NJ, W₁ < 5.05; 0 otherwise |

## Appendix C. References

- Card, D., & Krueger, A. B. (1994). Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania. *American Economic Review*, 84(4), 772–793.
- Stigler, G. J. (1946). The Economics of Minimum Wage Legislation. *American Economic Review*, 36(3), 358–365.
- Katz, L. F., & Krueger, A. B. (1992). The Effect of the Minimum Wage on the Fast-Food Industry. *ILR Review*, 46(1), 6–21.
