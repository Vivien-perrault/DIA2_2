# Review 5 – Routing rule (second reviewer)

- Reviewer: Adrian Bernard (second reviewer; first reviewer: Baptiste Marseille)
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/reports/td2.md`, section 3 (lines 327-346)
- Author: Antonin Charron
- Read together with: `td2/td2-policies.md` (item 4) and `td2/atelier-routage-new.py` (item 6, see [review-6-adrian.md](review-6-adrian.md))

## How it was checked

1. Every rate and every cell cited in the table was recomputed from `td1/traces-td1.csv` (last attempt per model and question) with the families of `td1/questions-td1.json`, using the corrected `td2/compute_accuracy.py`.
2. Each first model and fallback was checked against the eligibility it claims (100 % on the family) and against the tie-break of policy P6.
3. Each check by use was checked against the vote results of `td2/td2-step1-vote.md` (2-of-3 and 3-of-5).
4. Prices were checked against `td3/portefeuille-modeles-2026-09-28.csv`.

AI assistance was used to recompute the rates; the results were read and checked by the reviewer.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `td2/reports/td2.md:342, 345` | For period (F1) and product list (F3), the first model is gpt-oss-20b. All five models are free and 100 % on these families, so the choice is a tie that the rule does not settle; policy P6 settles ties by the best TD 1 rate, which gives gpt-oss-120b (20/20 against 19/20). gpt-oss-20b is also the model that hit Groq's 8 000 tokens-per-minute limit (2 HTTP 429 out of 22 calls). | `td2/td2-policies.md` P6; `td1/traces-td1.csv`: gpt-oss-20b C19 and C20 attempt 1 = HTTP 429. | fixed in `3b4aab3` (Antonin Charron) |
| 2 | important | `td2/reports/td2.md:343` | For age at a date (F2), the first model is Qwen, while gpt-oss-120b is also 4/4 at 0 USD; P6 gives gpt-oss-120b (20/20 against 16/20). | Same as above. | fixed in `3b4aab3` (Antonin Charron) |
| 3 | important | `td2/reports/td2.md:342-346` | The rule, the policies and the simulator choose three different first models: F1 gpt-oss-20b (rule) / gpt-oss-120b (P6) / Cohere (simulator); F2 Qwen (rule) / gpt-oss-120b (P6 and simulator); F2b gpt-oss-120b (rule) / Cohere (simulator, wrong on C10). Q3 asks which TD 1 cell justifies a line: the three files must give the same answer. | `review-6-adrian.md`, findings 1 and 3. | fixed in `3b4aab3` (Antonin Charron), `4107d90` (Vivien Perrault), `a1e0036` (Baudouin Parent) |
| 4 | minor | `td2/reports/td2.md:342, 345` | The F1 and F3 fallback says "the next free model at 100 % on another provider (Cohere on OpenRouter or Qwen on Groq)": Qwen is on Groq, the same provider as gpt-oss-20b, so it does not protect against a Groq outage. | `td1/modeles-autorises.json`: qwen3.8-27b gate `groq`. | fixed in `3b4aab3` (Antonin Charron) |
| 5 | minor | `td2/reports/td2.md:346` | For combinations, the customer check says the 2-of-3 panel "fails" on C15, C17, C19: it **abstains** on these three questions (it gives no figure), which is the safe outcome; the reason for a deterministic check is that it gives no answer, not that it gives a wrong one. | `td2/td2-step1-vote.md`: C15, C17, C19 = "abstain (max 1)". | fixed in `3b4aab3` (Antonin Charron) |
| 6 | minor | `td2/reports/td2.md:344` | "gpt-oss-120b … sans limite TPM 8 000" has no source: the 8 000 tokens-per-minute limit is documented for gpt-oss-20b only. | `td1/five-model-summary-en.csv` cites the limit for gpt-oss-20b; nothing for gpt-oss-120b. | fixed in `3b4aab3` (Antonin Charron) |
| 7 | minor | `td2/reports/td2.md`, section 3 | The section does not mention the simulator outputs (deliverable 5) nor link to `atelier-routage-new.py`. | No occurrence of "simulat" or "atelier-routage" in the report. | fixed in `3b4aab3` (Antonin Charron) and `4107d90` (Vivien Perrault) |

## What works

- **Every rate and every cell cited is correct**: F1 6/6 for all five models (C01, C04-C07, C20); F2 4/4 for gpt-oss-120b and Qwen, 3/4 for gpt-oss-20b (C02 wrong), 1/4 for Dots (C11 right), 0/4 for Cohere (C09 `sql_invalid`); F2b only the two gpt-oss models right on C10, Dots `sql_invalid`; F3 4/4 for all; combinations 5/5 for both gpt-oss models (gpt-oss-20b C19 on attempt 2), 2/5 for the others with the right cells (Cohere and Qwen C16, C18; Dots C16, C19); gpt-oss-20b C20 right on attempt 2.
- **Every line has a first model, a check for the three uses and a course of action when the first model is unavailable** (next model, defer, paid route, abstain), which is what Q3 level 2 asks.
- The checks follow the vote results: deterministic check for customer figures on F2 (3-of-5 wrong consensus on C02), F2b (2-of-3 wrong consensus on C10) and combinations.
- Models that failed a family are excluded from its fallback (Cohere and Dots on F2; Qwen, Cohere and Dots on F2b and combinations), consistent with P8.
- The paid fallback price (gpt-oss-120b on OpenRouter, 0.15 / 0.60 USD per million tokens) matches the portfolio.

## Summary

The table is correct and complete for Q3; what must change is the choice of the first model on F1, F3 and F2, which contradicts P6 and differs from the simulator. Decide one tie-break (P6's "best TD 1 rate", or another one written in both files), apply it in the rule, the policies and the simulator, and fix the provider of the F1/F3 fallback.
