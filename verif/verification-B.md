# Verification of batch B: groq:openai/gpt-oss-20b

- Operator: Baudouin PARENT (author of commit `70cf4df`)
- Checked by: Baudouin
- Date of check: 2026-10-21
- Files checked: `traces-B.csv`, `state-B.jsonl` (commit `70cf4df`), against `reference-td1.csv`
- Comparison rows produced: [`comparison-B.csv`](comparison-B.csv), to merge into `model-question-comparison-en.csv`

## Checks

| Check | Result |
|---|---|
| Records in `traces-B.csv` (CSV records, not text lines: SQL spans several lines) | 22 = 20 initial calls + 2 retries |
| Attempts per cell (protocol: at most 2) | 1 on 18 cells, 2 on C19 and C20 |
| HTTP status | 200 on 20 calls; 429 on attempt 1 of C19 (12:38:32) and C20 (12:38:39) |
| `nature` | `real` on every record |
| `model_returned` = `model_requested` | yes on all 20 records with HTTP 200 |
| `cost_native` | empty on every record (Groq free plan reports no cost) |
| `reference` column = `reference-td1.csv` | identical for all 20 questions |
| `prompt_sha256` per question | one fingerprint per question (20 distinct), identical to batches A and C-E |
| Output length | at most 564 completion tokens (of which 480 were reasoning tokens), below the 1024 cap: no truncation |
| Run window | 12:36:32-12:38:42 UTC, 2026-10-21 |
| Offline replay of the stored SQL (`--replay traces-B.csv`, output not committed) | 19/20 correct, same verdicts as the real run |

## Access failures

C19 and C20 received HTTP 429 on their first attempt. The `error` field says "Rate limit reached for model `openai/gpt-oss-20b` ... on tokens per minute (TPM)". With the default 3-second pause, about 950 tokens per call (prompt + completion) reached the Free plan's tokens-per-minute limit for this model. These are failed accesses, not wrong answers. Each cell was retried once, about 3 seconds later, and both retries are correct. The final status comes from attempt 2, and both attempts stay in the traces.

## Result

19 correct, 1 incorrect (C02), 0 sql_invalid, 0 not executed.

| Case | Status | Cause, from the SQL field, checked on the database |
|---|---|---|
| C02 | incorrect (0 vs 590320) | Age bounds `birth_date > '2025-09-25' AND birth_date <= '2026-09-25'` select customers aged 0, not 25: the model subtracted one year instead of 25 and 26. No customer was born after 2006-08-15, so 0. |

The only failure is a simple age question on a reference date. The same model is correct on C08, C09 and C11 (same family, other dates) and on all five combined questions. This looks like an isolated error rather than a systematic misreading of the convention.

## Call count

22 calls: 20 initial calls and 2 retries after HTTP 429, all on the Groq free plan.
