# Verification of batch D: groq:qwen/qwen3.8-27b

- Operator: Adrian BERNARD
- Checked by: Chandra R S SUKUMAR
- Date of check: 2026-10-21
- Files checked: `traces-D.csv`, `state-D.jsonl` (commit `6875ee2`), against `reference-td1.csv`
- Comparison rows produced: [`comparison-D.csv`](comparison-D.csv), to merge into `model-question-comparison-en.csv`

## Checks

| Check | Result |
|---|---|
| Records in `traces-D.csv` (CSV records, not text lines: SQL spans several lines) | 24 = 20 initial calls + 4 retries |
| Attempts per cell (protocol: at most 2) | max 2 (C16, C18, C19, C20) |
| `nature` | `real` on every record |
| `model_returned` = `model_requested` | yes on the 19 answered records; empty on the 5 HTTP 429 records (no answer) |
| `reference` column = `reference-td1.csv` | identical for all 20 questions |
| `prompt_sha256` per question | one fingerprint per question, identical across attempts (20 distinct fingerprints) |
| Run window | 12:53:10-12:54:47 UTC, 2026-10-21 |
| Offline replay of the stored SQL (`--replay traces-D.csv`, output not committed) | 16/20 correct, same verdicts as the real run |

## Result

16 correct, 3 incorrect (C15, C17, C19), 1 not executed (C18). Accuracy on executed cells: 16/19.

| Case | Status | Cause, from the SQL or error field |
|---|---|---|
| C15 | incorrect (0 vs 168680) | Age filter compares birth month-day only, ignoring the year; the two bounds contradict each other, so nothing matches. |
| C17 | incorrect (248490 vs 258180) | Age boundary off by one day on the birthday 09-25: C001 (born 2001-09-25, 80190) excluded, C004 (born 2000-09-25, 70500) included. 258180 - 80190 + 70500 = 248490. |
| C18 | not_executed | HTTP 429, Groq output-tokens-per-minute limit (OTPM 1000) on both attempts. Access failure, not a wrong answer. Not retried: retry budget exhausted. |
| C19 | incorrect (83580 vs 1990) | Year string compared with a full date as text: the age filter has no effect; 83580 is the revenue of product d in September 2026 for all customers. |

All three wrong answers are in the age family combined with another filter (period and/or product list). Single-filter age questions (C02, C08-C11) are all correct.

## HTTP 429 events

5 responses with HTTP 429 (C16, C18 x2, C19, C20), all on Groq's output-tokens-per-minute limit for this model (1000 tokens/min on the Free plan). With answers of about 130-230 tokens and the 3-second pause, the limit is reached after about 5-6 answers. The skeleton retried each once; C16, C19 and C20 were answered on attempt 2.

## Call count

24 calls in the batch (20 initial + 4 retries), within the 5-call margin. One earlier Qwen call from `check_access.py` is counted separately.
