# Review 6 – Simulator adaptation

- Reviewer: Adrian Bernard (first reviewer; second reviewer: Nazim Yacine)
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/atelier-routage-new.py` (adapted), `td2/atelier-routage.py` (original, "before")
- Author: Vivien Perrault

## How it was checked

1. Both simulators run from `td2/`: the original prints its 7 scenarios, the adapted one its 6 scenarios, without error.
2. `RESOURCES` was compared, model by model, with the TD 1 family results recomputed by the corrected `td2/compute_accuracy.py` (commit `94382bb`), which match `td1/five-model-summary-en.csv`.
3. `choose` was called directly on requests that the 6 scenarios do not cover: age at the order (`F2b_age_at_order`), product list (`F3_product_list`), a high-impact age question, and a combination with gpt-oss-120b unavailable.
4. The choices were compared with the routing rule (`td2/reports/td2.md`, section 3) and the policies (`td2/td2-policies.md`, P5, P6, P8).

AI assistance was used to probe `choose` and cross the figures; the results were read and checked by the reviewer.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | blocking | `atelier-routage-new.py:39` | Cohere is eligible for `F2b_age_at_order` and is the resource chosen for it, although it is wrong on C10, the only question of that family (it is one of the two models of the C10 wrong consensus). Policy P8 forbids routing to a model that failed the family. | `choose({difficulty: 2, family: "F2b_age_at_order"})` returns `cohere/north-mini-code:free`; TD 1: Cohere C10 = 119 410, reference 558 980. | fixed in `4107d90` (Vivien Perrault) |
| 2 | blocking | `atelier-routage-new.py:17-18, 28-29, 39-40, 50-51` | The families and `td1_cells` come from the old, wrong family mapping of `compute_accuracy.py` (fixed in `94382bb`). The reason printed in each decision cites cells that do not justify it, which is what Q3 checks. | Qwen: families F1, F3 only, cells "C01, C05, C09, C12, C04, C08, C13, C16" (C08, C09 are age questions, C16 is a combination), but Qwen is 4/4 on age at a date (C02, C08, C09, C11). gpt-oss-20b: "F4_combined (66.7%)", actual 5/5 on C15-C19, and missing from the combination family. Cohere: "C01-C16 (75% accuracy)", actual 6/6 period, 4/4 product, 0/4 age at a date, 0/1 age at the order. gpt-oss-120b: "combinations C17-C20", actual C15-C19. | fixed in `4107d90` (Vivien Perrault) |
| 3 | important | `atelier-routage-new.py:81` | The selection key `min(allocation, level, id)` picks the resource with the **smallest** quota, not the rule's first model nor policy P6 ("ties → best TD 1 rate"). The simulator, the rule and the policies choose different first models. | F1 period: simulator Cohere (allocation 20), rule gpt-oss-20b, P6 gpt-oss-120b (20/20). F2 age at a date: simulator gpt-oss-120b, rule Qwen. | fixed in `4107d90` (Vivien Perrault) |
| 4 | important | `atelier-routage-new.py:43, 53-62, 74` | The resources mix real and fictitious ones: gpt-oss-120b is labelled `senior-subscription`, access `subscription`, while it is used on Groq's free plan; `senior-api` (0.30 cash) is fictitious and, with `r["level"] == 3`, eligible for every family. The rule's paid fallback is the real `openai/gpt-oss-120b#openrouter` (0.15 / 0.60 USD per million tokens). | Combination, gpt-oss-120b unavailable, urgent: the simulator chooses `senior-api` (0.30) instead of the rule's next free model, gpt-oss-20b (5/5 on C15-C19). | fixed in `4107d90` (Vivien Perrault) |
| 5 | important | `atelier-routage-new.py:76` | The checks do not follow the rule by use: there are two fixed strings, decided by `high_impact` or "combination", instead of none / 2-of-3 / deterministic check / human review for internal dashboard, customer figure and payout (P5). | Every high-impact request returns "source verification and human review"; no request ever returns a quorum. | fixed in `4107d90` (Vivien Perrault) |
| 6 | important | `atelier-routage-new.py:110-128` | The scenarios cover period, age at a date and combinations only: no scenario for age at the order (C10, the wrong consensus) nor product list, although the docstring announces F1, F2, F2b, F3 and combinations. Dots is absent from `RESOURCES` without a stated reason. | 6 scenarios: 1 F1, 1 F2, 4 combinations. | fixed in `4107d90` (Vivien Perrault) |
| 7 | blocking (deliverable 5) | – | The simulator outputs before and after adaptation are not saved in the repository. | No output file in `td2/`; the report section 3 does not mention the simulator. | fixed in `4107d90` (Vivien Perrault) |
| 8 | minor | `atelier-routage-new.py:50, 71` | Family names differ between files: `F1_F2_F3_combination` here, `F4_combined` in `compute_accuracy.py`, "Combinaisons" in the rule. | – | fixed in `4107d90` (Vivien Perrault) |
| 9 | minor | `atelier-routage-new.py:11, 22, 33` | `level` values (1, 2, 3) are not derived from TD 1 and exclude eligible models: Qwen (level 1) can never serve a request of difficulty 2, although it is 4/4 on age at a date. | – | fixed in `4107d90` (Vivien Perrault) |

## What works

- The adapted file keeps the original `atelier-routage.py` untouched, so the "before" outputs can still be produced.
- The decision structure (run included capacity, defer when the resource resets before the deadline, paid route within budget, abstain) and the `reason` field carried by every decision follow the workshop's design.
- Deferral and abstention behave as intended on the combination scenarios: `defer` with a wake-up when gpt-oss-120b is exhausted and the request can wait, `abstain` when nothing is eligible within the budget.

## Summary

The simulator does not yet implement our rule: it routes age at the order to Cohere (the C10 failure), cites cells from the old family mapping, and its choices differ from both the rule and the policies. To fix before the Q3 marking: rebuild `RESOURCES` from the corrected TD 1 family results (real models, real prices, no fictitious route eligible by default), make `choose` select the rule's first model with the fallback order of the rule, add one scenario per family including C10, and save the outputs before and after in `td2/`.
