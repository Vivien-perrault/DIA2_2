# Review 2 – Table of the 20 vote decisions (first reviewer)

- Reviewer: Ismaël Wane (first reviewer; second reviewer: Chandra R S Sukumar)
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/td2-step1-vote.md`, `votes-20-questions.jsonl`
- Authors: Baudouin Parent, Antonin Charron

## How it was checked

The second reviewer recomputed the table with her own script. This review takes other angles:

1. **Official tool.** `td2/atelier-vote.py --traces ../td1/traces-td1.csv --case Cxx` was run on the 20 questions, and its 20 outputs were compared with `votes-20-questions.jsonl`.
2. **Inputs of the vote.** `proposals_for` in `atelier-vote.py` was read: it keeps the last CSV row per panel member. The order of the retried rows in `td1/traces-td1.csv` was checked (gpt-oss-20b on C19 and C20: attempt 1 = HTTP 429, then attempt 2 = HTTP 200).
3. **Panel against the assignment.** The fixed panel and the 3-of-5 panel were compared with `td2/enonce-td2-en.md` (Step 1: "a k-of-n vote on a panel of distinct families").
4. **Reasoning of the commentary.** Each conclusion was checked for what the traces support and what they do not.

AI assistance was used to run the tool on the 20 questions and compare the outputs; the results were read and checked by the reviewer.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `td2/td2-step1-vote.md:6, 33-36` | The 3-of-5 panel contains two models of the same family (`openai/gpt-oss-120b` and `openai/gpt-oss-20b`), while the assignment asks for "a panel of distinct families". The table presents 3-of-5 as a quorum on the same footing as the fixed panel; only the C19 paragraph mentions the issue. The 3-of-5 results should be declared as an exploratory panel that does not meet the distinct-family rule. | `td2/enonce-td2-en.md:16`; on C19 the 3-of-5 consensus rests on gpt-oss-120b, gpt-oss-20b and Dots. | |
| 2 | minor | `td2/td2-step1-vote.md:42` | "Three models from three different providers/families" on C02: the families are distinct (OpenAI, Cohere, Dots), but there are only two providers, since Cohere and Dots both go through OpenRouter. | `td1/modeles-autorises.json`: gate `openrouter` for both. | |
| 3 | minor | `td2/td2-step1-vote.md:42` | "The exact clause is analysed in step 2": step 2 of the report analyses the SQL of C10 (and C11), not that of C02; the C02 zeros are explained nowhere in TD 2. | `td2/reports/td2.md` at `175f4b4`: C02 appears only in the quorum results (sections 2.2, 2.3, summary). The causes of the three C02 zeros are in `td1/verif/` (batches B, C, E). | |
| 4 | minor | `td2/td2-step1-vote.md:52` | "A vote does not beat the best single model": the best single model (gpt-oss-120b, 20/20) is only known after comparing every answer with the references. Without the references, a single model gives no signal when it is wrong, whereas the vote abstains on C15, C17, C19. The sentence should state that the comparison uses hindsight. | – | |
| 5 | minor | `td2/td2-step1-vote.md`, 3-of-5 columns | The official tool only runs the fixed 2-of-3 panel; the 3-of-5 columns come from `compare-vote.py`, which is absent. Same finding as the second reviewer, confirmed. | `atelier-vote.py`: `PANEL` has three members and `evaluate` calls the vote with k = 2. | |

## What works

- **The official tool reproduces the raw output exactly**: the 20 outputs of `atelier-vote.py` are identical, field by field, to the 20 records of `votes-20-questions.jsonl`.
- **The inputs follow the rules**: the last row per member is its last attempt (the two retries of gpt-oss-20b come after their HTTP 429); a wrong value still votes; `sql_invalid` stays in n without a vote; the reference is only used after the decision.
- **The fixed panel matches the assignment**: gpt-oss-120b (Groq), north-mini-code (OpenRouter) and qwen3.8-27b (Groq), three distinct families, k = 2.
- **The main conclusions are sound**: a larger quorum moves the errors (C02, C10) instead of removing them; C15 and C17 are the questions where no quorum answers, hence candidates for a deterministic check.

## Summary

The table is reproducible with the official tool for the fixed panel and its main conclusions hold. To fix: declare the 3-of-5 panel as exploratory (two gpt-oss models), correct "three providers" on C02, point the C02 causes to `td1/verif/` instead of step 2, and say that "the best single model" is a hindsight comparison.
