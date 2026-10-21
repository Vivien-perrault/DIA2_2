# Verification of batch A: groq:openai/gpt-oss-120b

- Operator: Antonin CHARRON (author of commit `b923182`)
- Checked by: Nazim
- Date of check: 2026-10-21
- Files checked: `traces-A.csv`, `state-A.jsonl` (commit `b923182`), against `reference-td1.csv`
- Comparison rows produced: [`comparison-A.csv`](comparison-A.csv), to merge into `model-question-comparison-en.csv`

## Checks

| Check | Result |
|---|---|
| Records in `traces-A.csv` (CSV records, not text lines: SQL spans several lines) | 20 = 20 initial calls, no retry |
| Attempts per cell (protocol: at most 2) | 1 on every cell |
| HTTP status | 200 on every call, no 429 |
| `nature` | `real` on every record |
| `model_returned` = `model_requested` | yes on all 20 records |
| `cost_native` | empty on every record (Groq free plan reports no cost) |
| `reference` column = `reference-td1.csv` | identical for all 20 questions |
| `prompt_sha256` per question | one fingerprint per question (20 distinct), identical to batches B-E |
| Output length | at most 536 completion tokens (of which 390 were reasoning tokens), below the 1024 cap: no truncation |
| Run window | 12:23:08-12:24:26 UTC, 2026-10-21 |
| Offline replay of the stored SQL (`--replay traces-A.csv`, output not committed) | 20/20 correct, same verdicts as the real run |

## Result

20 correct, 0 incorrect, 0 sql_invalid, 0 not executed.

Every family is correct, including the ten age questions (C02, C08-C11, C15-C19). This is the only model in the batch whose age logic follows the anniversary convention of the prompt on every question.

## Call count

20 calls, no retry, all on the Groq free plan.
