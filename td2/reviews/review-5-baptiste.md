# Review 5 – Routing rule (first reviewer)

- Reviewer: Baptiste Marseille (first reviewer; second reviewer: Adrian Bernard)
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/reports/td2.md`, section 3 (lines 327-346)
- Author: Antonin Charron

## How it was checked

1. The section was read from the reviewed commit (`git show 175f4b4:td2/reports/td2.md`), not from the working copy.
2. The rates and cells of the table were recomputed from `td1/traces-td1.csv` (last attempt per model and question, families of `td1/questions-td1.json`).
3. The **fallback order** of each line was read step by step and checked against the eligible models of the family: is every free model at 100 % tried before a paid route or an abstention?
4. The **checks by use** were compared with policies P4 and P5 of `td2/td2-policies.md`, and the general principles (section 3.1, points 1-3) with the table.
5. The three links of the section were opened; the paid prices were checked against `td3/portefeuille-modeles-2026-09-28.csv`.

AI assistance was used to read the section and recompute the figures; the results were read and checked by the reviewer. The same assistant helped the second reviewer: this review deliberately uses other angles (fallback order, P4/P5, principles) to stay as independent as possible.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `td2/reports/td2.md:342, 345` | For period (F1) and product list (F3), the fallback skips two free models that are 100 % on the family: gpt-oss-120b on Groq and Dots on OpenRouter. When the first model (gpt-oss-20b) hits its own tokens-per-minute limit, the rule goes to Cohere or Qwen, then defers, then **pays** for gpt-oss-120b on OpenRouter, while gpt-oss-120b is free on Groq. | TD 1: gpt-oss-120b 6/6 and 4/4, Dots 6/6 and 4/4; fallback steps 1-3 of the F1 and F3 lines. | |
| 2 | important | `td2/reports/td2.md:343, 344, 346` | For age at the order (F2b) and combinations, every eligible free model is on Groq (gpt-oss-120b, gpt-oss-20b); for age at a date, Qwen and gpt-oss-120b are also both on Groq. The rule does not state that a Groq outage leaves only the paid route or an abstention, which the policies note as the "weak point". | `td1/modeles-autorises.json`: gate `groq` for the three models; `td2/td2-policies.md` section 2, last point. | |
| 3 | minor | `td2/reports/td2.md:342, 345` | For payouts on F1 and F3, the rule asks for a 3-of-5 quorum plus a deterministic check or review; policy P5 asks for the reference query. A 3-of-5 quorum adds nothing once the reference query is run, and it is the quorum that gave a wrong consensus on C02. | `td2/td2-policies.md` P5; `td2/td2-step1-vote.md`, C02 3-of-5 = 0. | |
| 4 | minor | `td2/reports/td2.md`, section 3 | Policy P4 (a consensus on 0 is escalated to the reference query) does not appear in the rule. Two references are genuinely 0 (C06, C14), so the rule should say when a 0 is accepted. | `td2/td2-policies.md` P4; `td1/reference-td1.csv`: C06 = 0, C14 = 0. | |
| 5 | minor | `td2/reports/td2.md:344` | Principle 3 allows `none` only for a model at 100 % on the family; on age at the order this 100 % rests on one question (C10). The line already recommends a SQL check; the principle should say that a family of one question does not qualify for `none`. | F2b = C10 only. | |
| 6 | important | `td2/reports/td2.md:342, 343, 345` | The first model on F1, F3 (gpt-oss-20b) and F2 (Qwen) is a tie between free models at 100 %, settled differently from policy P6 (best TD 1 rate, which gives gpt-oss-120b). Same finding as the second reviewer; confirmed independently. | `td2/td2-policies.md` P6; gpt-oss-120b 20/20, gpt-oss-20b 19/20, Qwen 16/20. | |

## What works

- **The figures are right**: every rate and every cell of the table matches the traces, including the retries (gpt-oss-20b C19 and C20 on attempt 2).
- **The structure answers Q3**: one line per family, the cells that justify it, a first model, a check for each of the three uses, and a fallback ending in `defer` or `abstain`.
- **Exclusions are consistent**: a model wrong on a family never appears in that family's fallback.
- **The checks follow the evidence**: deterministic check for customer figures where a quorum failed (F2 on C02, F2b on C10, combinations).
- **Links and prices**: the three links open; gpt-oss-120b on OpenRouter at 0.15 / 0.60 USD per million tokens matches the portfolio.

## Summary

The rule is correct on the figures and complete for Q3. To fix: put the free 100 % models (gpt-oss-120b on Groq, Dots) before any paid route on F1 and F3, state the Groq single-provider dependency for age and combinations, align payouts and zeros with P4/P5, and settle the first-model tie the same way as P6.
