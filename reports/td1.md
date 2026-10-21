# TD 1 report - Sub-group DIA2_2

Session 1, 21 October 2026. Five free models on the same twenty revenue questions, against references computed by the sub-group.

## 1. Summary

- **Reference**: 20 queries and values in [`reference-td1.csv`](../reference-td1.csv), each checked by a second member (`checked_by` column).
- **Batch**: 100 cells (20 questions x 5 models), all executed, all `real`. 102 calls in [`traces-td1.csv`](../traces-td1.csv): 100 first attempts and 2 retries.
- **Result**: 80 correct, 17 incorrect, 3 `sql_invalid`, 0 `not_executed`.
- **Main finding**: all 20 failures are in questions with an **age** condition. All 50 period and product-list cells without an age filter are correct, for all five models.

| Model (operator) | Correct | Incorrect | SQL invalid | Median latency |
|---|---|---|---|---|
| groq `openai/gpt-oss-120b` (A) | **20/20** | 0 | 0 | 844 ms |
| groq `openai/gpt-oss-20b` (B) | 19/20 | 1 | 0 | 651 ms |
| groq `qwen/qwen3.8-27b` (D) | 16/20 | 4 | 0 | 689 ms |
| openrouter `dots-studio/dots-3-note-preview:free` (E) | 13/20 | 5 | 2 | 3184 ms |
| openrouter `cohere/north-mini-code:free` (C) | 12/20 | 7 | 1 | 1611 ms |

Latency is the median over the HTTP 200 calls in `traces-td1.csv`.

## 2. Work attempted and completed

| Step | Status | Evidence |
|---|---|---|
| 1. References | Done: 20/20, each one checked independently | [`reference-td1.csv`](../reference-td1.csv), [`sql/`](../sql/) |
| 2. Five model batches | Done: 100/100 cells | [`traces-A.csv`](../traces-A.csv) ... [`traces-E.csv`](../traces-E.csv), `state-A.jsonl` ... `state-E.jsonl` |
| 2. Merged traces | Done: 102 rows under one header | [`traces-td1.csv`](../traces-td1.csv) |
| 3. Comparison CSV | Done: 100 rows, one final result per cell | [`model-question-comparison-en.csv`](../model-question-comparison-en.csv) |
| 3. Five-model summary | Done | [`five-model-summary-en.csv`](../five-model-summary-en.csv) |
| 3. Verification notes | Done for all five batches: checks, offline replay and cause of each failure, checked on the database | [`verif/`](../verif/): `verification-A.md` ... `verification-E.md` and `comparison-A.csv` ... `comparison-E.csv` |
| Prompt | Unchanged from the kit; the 20 fingerprints recomputed from it match the traces | [`prompts/prompt-td1.md`](../prompts/prompt-td1.md), verbatim copy of `SYSTEM_PROMPT` and `USER_PROMPT_TEMPLATE` from [`skeleton-multi-llm-en.py`](../skeleton-multi-llm-en.py) |

Consistency checks run for this report (scripted, on the committed files):

- Every row of `model-question-comparison-en.csv` matches the **last** attempt of its cell in `traces-td1.csv` (status, value and reference): 0 mismatches.
- One prompt fingerprint (`prompt_sha256`) per question across the five models: 20 questions, 20 fingerprints.
- `model_returned` = `model_requested` on every row.
- `skeleton-multi-llm-en.py`, `sandbox_sqlite.py`, `schema.sql`, `questions-td1.json` and `modeles-autorises.json` have the SHA-256 recorded in `manifest.json`. Prompt, conventions and call parameters are those of the kit.
- The family counts in `five-model-summary-en.csv` match the comparison CSV.
- Replaying the stored SQL offline (`--replay`, output not committed) gives the same verdicts as the real runs, for all five batches.

## 3. Results

### Models x questions matrix

This is a view of `model-question-comparison-en.csv`, not a second entry. `OK` = correct, `X` = incorrect, `SQL` = sql_invalid.

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 | C19 | C20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-120b | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| gpt-oss-20b | OK | X | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| qwen3.8-27b | OK | OK | OK | OK | OK | OK | OK | OK | OK | X | OK | OK | OK | OK | X | OK | X | OK | X | OK |
| dots-3-note | OK | X | OK | OK | OK | OK | OK | X | X | SQL | OK | OK | OK | OK | SQL | OK | X | X | OK | OK |
| north-mini-code | OK | X | OK | OK | OK | OK | OK | X | SQL | X | X | OK | OK | OK | X | OK | X | OK | X | OK |

### By question family

Families follow the `type` field of `questions-td1.json`, grouped as in `five-model-summary-en.csv`:

- period: C01, C04-C07, C20 (6 questions);
- age: C02, C08, C09, C11 on a reference date, and C10 at the time of the order (5);
- product list: C03, C12-C14 (4);
- combined: C15-C19 (5).

| Model | Period | Age | Product | Combined |
|---|---|---|---|---|
| gpt-oss-120b | 6/6 | 5/5 | 4/4 | 5/5 |
| gpt-oss-20b | 6/6 | 4/5 | 4/4 | 5/5 |
| qwen3.8-27b | 6/6 | 4/5 | 4/4 | 2/5 |
| dots-3-note | 6/6 | 1/5 | 4/4 | 2/5 |
| north-mini-code | 6/6 | 0/5 | 4/4 | 2/5 |

The questions missed most often are C02, C10, C15 and C17, each by three models. In the combined family, C16 is the only question that all five models got right. C16 is age on a reference date plus a product list, with no period.

### Access failures and retries

- **Batch B** (gpt-oss-20b, Groq): C19 and C20 got **HTTP 429** (rate limit, `org_...` in the `error` field) on attempt 1. Both cells are correct on attempt 2. Both attempts are kept in `traces-B.csv` and `traces-td1.csv`. This is a failed access, not a wrong answer. The final status comes from attempt 2.
- **Batch D** (qwen3.8-27b, Groq): the first run, at 12:53-12:54 UTC, hit Groq's output-tokens-per-minute limit: 5 HTTP 429 responses, and C18 was not executed after 2 attempts. With the instructor's agreement, it was rerun in full with `--pause 15` at 13:28-13:33 UTC: 20 calls, no 429. The files were overwritten. The first run (24 calls: 16 correct, 3 incorrect, 5 HTTP 429, C18 not executed) was restored from commit `6875ee2` into [`traces-D-run1.csv`](../traces-D-run1.csv) and [`state-D-run1.jsonl`](../state-D-run1.jsonl). It is kept as a separate experiment: it is not in `traces-td1.csv` and does not count in the results. See [`verif/verification-D.md`](../verif/verification-D.md).
- No other non-200 status. Every cell has at most 2 attempts.

## 4. Observed causes

Causes are read from the `sql` field of each trace. Where possible, we checked them by recomputing the wrong value on the database; for example, 258180 - 68310 = 189870 for dots C17. The detail for each cell is in [`verif/verification-X.md`](../verif/) and in the `explanation` column.

| Cause | Cells |
|---|---|
| Age at the time of the order: only year difference 25 with the birthday passed; the "year difference 26, birthday not yet passed" case is missed | north C10, qwen C10, dots C18 |
| Month and day compared separately, or contradictory month-day bounds | dots C02, C08, C17; qwen C15 |
| A spurious condition on the order date is added (the reference date is treated as an order date), so 0 | north C02, C08; dots C09 |
| Missing bound: every customer aged 0 to 25 is counted | north C15, C17 |
| Off by one day on the birthday (customers born on 09-25 misclassified) | qwen C17 |
| Wrong date bounds or arithmetic: customers aged 0, an invalid `date()` modifier returning NULL, text compared with a date | gpt-oss-20b C02; north C11, C19; qwen C19 |
| Invalid SQLite syntax (`AS` alias inside an expression, `+ 25 years`, misplaced parenthesis in `CAST`) | north C09; dots C10, C15 |

There is no truncated output: completion tokens stay well under the 1024 cap (at most 564). There is no wrong model either: `model_returned` is always the model requested.

## 5. Hypotheses

These come from one batch of 20 questions, with one run per cell. They are not a general ranking.

1. **The age convention is the discriminating difficulty.** The prompt defines completed age precisely. Every model handles simple period and product filters, but only the two GPT-OSS models handle anniversary logic reliably.
2. **Reasoning may help.** The two GPT-OSS models run with `reasoning_effort: low` and are the only ones with 5/5 combined. Qwen (`reasoning_effort: none`) and the two OpenRouter models (reasoning disabled) miss 3/5 combined questions. Testing this would require the same model with reasoning on and off, which we did not run.
3. **Temperature 0 is not fully deterministic.** Qwen got C10 right in its first run (`6875ee2`) and wrong in the rerun. A single run does not measure a model's stability.
4. **"Reference date" is sometimes read as an order date.** Three failures (north C02, C08; dots C09) add a filter on the order date that the question does not ask for. A clearer prompt could test this hypothesis, but it would change the prompt fingerprint and start a separate experiment.
5. **Routing hypothesis for TD 2:**
   - period and product-only questions → the cheapest or fastest model; all five were 100% on them;
   - questions with an age condition → `gpt-oss-120b`, or a check or vote that includes it.

## 6. Cost and portfolio

- All calls were made on free routes, so the native cost is 0 or empty.
- Only `gpt-oss-120b` has a documented paid route of the same model in the portfolio: OpenRouter, 0.15 / 0.60 USD per million input / output tokens, dated 2026-09-28. At that price, its 20 calls (12,814 prompt tokens and 4,952 completion tokens, as counted by Groq) would cost about 0.005 USD.
- The other four models are N/A: there is no matching paid route in the kit. See [`five-model-summary-en.csv`](../five-model-summary-en.csv).

## 7. Limitations

- **One run per cell**, 20 questions: the observed rates have wide uncertainty. Some families have only 4 to 6 questions.
- **Batch D first run** is kept in separate files (`traces-D-run1.csv`, `state-D-run1.jsonl`), not in `traces-td1.csv`. With it, batch D used 44 Groq calls instead of 20.
- **Self-checks**: batches B and E were checked by their own operators, so those checks are not independent. Every value and cause in them was also recomputed on the database by script.
- **Batch C verification note**: its first version described a run that did not match the committed traces. It was corrected in commits `c7f7fbb` and `7967d88` and now matches [`traces-C.csv`](../traces-C.csv) (13:47-13:49 UTC). We checked it again on the database: every cause and value is confirmed.
- The `explanation` column of `model-question-comparison-en.csv` was written before the verification notes. Some wording is shorter or less precise than in `verif/` (for example dots C15: the problem is a misplaced parenthesis, not an unbalanced one). Statuses and values are identical.
- Token counts come from each provider's tokenizer, so they are not comparable across models.
- Public index and paid prices are N/A for the two OpenRouter free models and for gpt-oss-20b and Qwen, which have no matching paid route in the kit.

## 8. Replayed and synthetic examples

- **Every row in `traces-td1.csv` and in the comparison CSV has `nature = real`.** No replayed or simulated row enters a count.
- Each verification note mentions an offline replay of the stored SQL (`--replay`) as a check. The replay output (`nature = replay`) was not committed and is not part of the results.
- No instructor-supplied historical or simulated example was used: the batch contains real access failures (the HTTP 429 responses in batches B and D).

## 9. Contributions

Compiled from the Git history and from `reference-td1.csv`. **Each member should check and correct their own line.**

| Member | Contribution |
|---|---|
| Antonin Charron | Operator A (gpt-oss-120b, 20/20); references C01-C02; filled the comparison and summary CSVs; `.gitignore` |
| Baudouin Parent | Operator B (gpt-oss-20b); references C17-C18; merged the raw traces into `traces-td1.csv`; check of batch B |
| Akihito Raffin | Committed batch C (north-mini-code) traces; references C09-C10 |
| Adrian Bernard | Operator D (qwen3.8-27b, run and rerun); OpenRouter account used for batch C; aligned the batch C note with the committed traces; references C13-C14 and `sql/` |
| Vivien Perrault | Operator E (dots-3-note); references C05-C06; check of batch E |
| Baptiste Marseille | Verification of batch C; references C07-C08 |
| Chandra R S Sukumar | Verification of batch D; references C11-C12 |
| Ismaël Wane | Independent check of C15-C16 |
| Nesrine Aissa | References C19-C20 |
| Nazim | References C03-C04; reference fixes; README; re-check of batch C; verification of batch A; drafts of the B and E notes; verbatim prompt file; restored the first run of batch D; this report |

**Use of AI assistance.** We used an AI coding assistant during the session, working back and forth with small, step-by-step prompts. Its outputs were checked manually and together within the sub-group. Reference values come from SQL executed on the database, never from a model's answer.

## 10. Next steps (TD 2)

1. Vivien confirms the OpenRouter account used for batch E in `verif/verification-E.md`.
2. Merge the verified explanations from `verif/comparison-*.csv` into `model-question-comparison-en.csv`, if the sub-group wants the more precise wording.
3. Write the k-of-n vote in `atelier-vote.py`. Test it on C02, C15 and C17, where three models fail: a majority vote across the five models can still be wrong if the failures agree, so plan an independent check of the age logic.
4. Turn the routing hypothesis (section 5) into the sub-group's routing rule and test it with `atelier-routage.py`.
5. Rotate roles as required by the protocol.
