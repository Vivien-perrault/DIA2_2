# Verification of batch E: openrouter:dots-studio/dots-3-note-preview:free

- Operator: Vivien PERRAULT (author of commit `4e13fdb`)
- Checked by: Vivien
- Date of check: 2026-10-21
- OpenRouter account used: _(to confirm by the operator)_, distinct from the account used for batch C (Adrian BERNARD)
- Files checked: `traces-E.csv`, `state-E.jsonl` (commit `4e13fdb`), against `reference-td1.csv`
- Comparison rows produced: [`comparison-E.csv`](comparison-E.csv), to merge into `model-question-comparison-en.csv`

## Checks

| Check | Result |
|---|---|
| Records in `traces-E.csv` (CSV records, not text lines: SQL spans several lines) | 20 = 20 initial calls, no retry |
| Attempts per cell (protocol: at most 2) | 1 on every cell |
| HTTP status | 200 on every call, no 429 |
| `nature` | `real` on every record |
| `model_returned` = `model_requested` | yes on all 20 records |
| `cost_native` | 0 on every record (free route) |
| `reference` column = `reference-td1.csv` | identical for all 20 questions |
| `prompt_sha256` per question | one fingerprint per question (20 distinct), identical to batches A-D |
| Output length | at most 480 completion tokens, no reasoning tokens, below the 1024 cap: no truncation |
| Run window | 13:26:10-13:28:10 UTC, 2026-10-21 |
| Offline replay of the stored SQL (`--replay traces-E.csv`, output not committed) | 13/20 correct, 2 invalid, same verdicts as the real run |

## Result

13 correct, 5 incorrect (C02, C08, C09, C17, C18), 2 sql_invalid (C10, C15), 0 not executed.

| Case | Status | Cause, from the SQL field, checked on the database |
|---|---|---|
| C02 | incorrect (0 vs 590320) | Keeps birth year 2001 with month-day `<= 09-25` AND month-day `> 09-25`. The lower bound is taken from `'2025-09-25'`, which has the same month-day. The two conditions contradict each other, so 0. |
| C08 | incorrect (0 vs 605580) | The first block requires birth month-day = `09-24`, the last block requires month-day `< 09-24` or `> 09-24`. The only candidate, C002 (born 2001-09-24), is excluded, so 0. |
| C09 | incorrect (0 vs 487980) | Hard-codes `birth_date = '2001-09-26'` (one exact birthday instead of a one-year range) and adds an order-date filter on 2026-09-26 only, which the question does not ask. There is no order that day, so 0. The birth filter alone would give 47900 (checked). |
| C10 | sql_invalid | Syntax error near "years": `CAST(... AS DATE) + 25 years` is not SQLite syntax; the `date()` modifier `'+25 years'` is needed. No value. |
| C15 | sql_invalid | Syntax error near "AS": misplaced parenthesis in `CAST((strftime('%Y', '2026-09-25') AS INTEGER) - ...`. No value. |
| C17 | incorrect (189870 vs 258180) | Compares birth month and day separately. The 2000 branch requires month `> 9` AND day `> 25`, so C005 (born 2000-09-26, 68310) is excluded. 258180 - 68310 = 189870 (checked). |
| C18 | incorrect (39580 vs 62480) | Age at the time of the order: keeps only year difference 25 with the birthday passed (39580). It misses year difference 26 with the birthday not yet passed (22900). 39580 + 22900 = 62480 (checked). |

All seven failures are in the age family. Every question without an age filter is correct (C01, C03-C07, C12-C14, C20), and only three of the ten age questions are correct (C11, C16, C19). Two failures are invalid SQL: this model sometimes writes date arithmetic that SQLite does not support.

## Call count

20 calls, no retry, all at zero cost.
