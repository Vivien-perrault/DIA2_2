# Verification of batch D: groq:qwen/qwen3.8-27b

- Operator: Adrian BERNARD
- Checked by: Chandra R S SUKUMAR
- Date of check: 2026-10-21
- Files checked: `traces-D.csv`, `state-D.jsonl` (rerun of 2026-10-21, 13:28-13:33 UTC), against `reference-td1.csv`
- Comparison rows produced: [`comparison-D.csv`](comparison-D.csv), to merge into `model-question-comparison-en.csv`

## Rerun with a longer pause

The first batch D (commit `6875ee2`, 12:53-12:54 UTC) ran with the default 3-second pause and hit Groq's output-tokens-per-minute limit for this model (OTPM 1000 on the Free plan): 5 HTTP 429 responses, C18 not executed after 2 attempts. With the instructor's agreement, the batch was rerun in full with `--pause 15` and the files were overwritten; the first batch remains in the Git history. The prompt, references, model and parameters are unchanged; only the pause between requests changed.

## Checks

| Check | Result |
|---|---|
| Records in `traces-D.csv` (CSV records, not text lines: SQL spans several lines) | 20 = 20 initial calls, no retry |
| Attempts per cell (protocol: at most 2) | 1 on every cell |
| HTTP status | 200 on every call, no 429 |
| `nature` | `real` on every record |
| `model_returned` = `model_requested` | yes on all 20 records |
| `reference` column = `reference-td1.csv` | identical for all 20 questions |
| `prompt_sha256` per question | one fingerprint per question (20 distinct fingerprints) |
| Run window | 13:28:21-13:33:20 UTC, 2026-10-21 |
| Offline replay of the stored SQL (`--replay traces-D.csv`, output not committed) | 16/20 correct, same verdicts as the real run |

## Result

16 correct, 4 incorrect (C10, C15, C17, C19), 0 not executed.

| Case | Status | Cause, from the SQL field |
|---|---|---|
| C10 | incorrect (119410 vs 558980) | Age at the time of the order: the second branch uses a year difference of 24 before the birthday (age 23) instead of 26 (age 25), so it matches nothing. Only customers who had already turned 25 in the order's year are counted (119410); the missing branch is worth 439570, and 119410 + 439570 = 558980. |
| C15 | incorrect (0 vs 168680) | Age filter compares birth month-day only, ignoring the year; the two bounds contradict each other, so nothing matches. |
| C17 | incorrect (248490 vs 258180) | Age boundary off by one day on the birthday 09-25: C001 (born 2001-09-25, 80190) excluded, C004 (born 2000-09-25, 70500) included. 258180 - 80190 + 70500 = 248490. |
| C19 | incorrect (83580 vs 1990) | Year string compared with a full date as text: the age filter has no effect; 83580 is the revenue of product d in September 2026 for all customers. |

All four wrong answers are in the age family: C10 (age at the time of the order) and C15, C17, C19 (age combined with a period and/or product list). The single-filter age questions on a reference date (C02, C08, C09, C11) are correct.

C15, C17 and C19 returned the same SQL as in the first batch. C10 was correct in the first batch and C18 was not executed there: the model's answer is not fully stable between two runs at temperature 0.

## Call count

20 calls in this rerun, no retry. The first batch used 24 calls (20 initial + 4 retries) and `check_access.py` used one earlier Qwen call; both are counted separately.
