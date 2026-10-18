# AI-Use Disclosure — Card & Krueger (1994) Replication Project

This project was completed with substantial assistance from an AI assistant
(Doubao / an AI coding-and-analysis agent). Consistent with the course policy,
the student remains responsible for every data choice, method, validation
check, interpretation, and conclusion. This document states, transparently,
**where and how AI was used, how its outputs were checked, and what was
corrected or rejected**.

## 1. Where and how AI was used

1. **Reading and summarising the source paper.** The AI extracted the empirical
   design, sample rules, and the exact numbers in Tables 2–4, Table 5 and
   Figure 1 from the PDF of Card & Krueger (1994) so that replication targets
   were fixed before any analysis.
2. **Writing the analysis code.** All Python code in `code/` was drafted by the
   AI (data cleaning, variable construction, regressions, figures, extension).
   The student reviewed the logic of each script.
3. **Diagnosing replication mismatches.** When a number did not match the paper,
   the AI proposed and tested candidate explanations (sample definitions,
   standard-error conventions, FTE definitions), e.g. the Table-4 sample rule
   that yields N = 357, and the %-full-time definition (EMPFT/FTE).
4. **Drafting the empirical report and README.** The AI wrote the first full
   draft; the student edited and verified the interpretation sections.
5. **Workflow management.** Version control (Git), folder structure and the
   one-command reproducibility script (`run_all.py`) were set up with AI help.

## 2. How AI-generated code, analysis, and writing were checked

- **Every reported number was cross-verified against the paper.** Replication
  targets (N = 357, coefficients 2.33/2.30/15.65/14.92, sd 8.825, DID 2.75/2.51,
  wage means 20.44/23.33/5.08/4.62, etc.) were transcribed from the paper and
  compared programmatically with our outputs before being written into the
  report.
- **Sample-construction rules were validated against published sample sizes**:
  410 stores, 331/79 split, 6 closed / 4 temporary / 1 refusal, balanced N = 384,
  regression N = 357.
- **The pipeline was run end-to-end repeatedly** (`python3 code/run_all.py`) and
  all tables/figures regenerated from the raw CSV without manual edits.
- **Figures were visually inspected** after generation (Figure 1 and the two
  extension figures) to confirm they convey the intended patterns.
- **Statistical outputs were sanity-checked**: t-stats, p-values, permutation
  results, and two-sample SEs were recomputed with independent formulas.
- **Writing was checked for factual claims**: every sentence asserting a number
  or a comparison in the report is backed by an output CSV or the paper.

## 3. Important AI errors or suggestions that were corrected or rejected

| # | What happened | Resolution |
|---|---|---|
| 1 | Initial Table-4 sample (employment + wave-1 *and* wave-2 wage both required) gave N = 351, not 357, and a GAP coefficient of 17.05 instead of 15.65. | Corrected the sample rule (wave-2 wage required **or** permanently closed) after testing candidate definitions against the published N = 357; coefficients then matched exactly (15.65). |
| 2 | First "% full-time" definition (managers included) gave 37.7/38.8 vs the paper's 32.8/35.0. | Tested five candidate definitions; found % full-time = EMPFT/FTE, which matches the paper exactly (32.85/35.04; 35.87/30.38). |
| 3 | Table 5 was initially estimated with NJ and GAP in a single regression, giving NJ = 1.06 instead of 2.30. | Re-read the paper's design (separate NJ-dummy and GAP models) and split the models; columns then matched (2.30/14.92). |
| 4 | `pd.get_dummies` silently dropped the original CHAIN column, breaking Table 2 chain shares. | Kept a copy of the chain id before one-hot encoding; Table 2 then matched. |
| 5 | The AI initially proposed a "longer-horizon event-study" extension and a "new sample period" extension. | Rejected: the public data contain only two waves and no later-period data; these would have been untestable. Replaced with the heterogeneity + placebo + randomization-inference extension that is feasible and answers a clear economic question. |
| 6 | The AI suggested matching the paper's row-3 SEs (NJ 0.54, DID 1.56) by ad-hoc formulas. | Rejected as unsound; instead reported the balanced-sample convention (PA 1.25 exact) and transparently documented the small discrepancy as a data-version difference. |

## 4. Statement of responsibility

The AI's role was to accelerate computation and drafting. All substantive
choices — the replication conventions documented in Section 2 of the report,
the extension design, the interpretation of the (sometimes fragile) estimates,
and the decision to flag rather than smooth over discrepancies — were made and
endorsed by the student. Any remaining errors are the student's own.
