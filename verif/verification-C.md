# Verification of batch C: openrouter:cohere/north-mini-code:free

- Operator: Akihitorh (author of commit `b72962e`)
- Checked by: _(name of the checker)_
- Date of check: 2026-10-21
- Files checked: `traces-C.csv`, `state-C.jsonl` (commit `b72962e`), against `reference-td1.csv`
- Comparison rows produced: [`comparison-C.csv`](comparison-C.csv), to merge into `model-question-comparison-en.csv`

## Checks

| Check | Result |
|---|---|
| Records in `traces-C.csv` (CSV records, not text lines: SQL spans several lines) | 20 = 20 initial calls, no retry |
| Attempts per cell (protocol: at most 2) | 1 on every cell |
| HTTP status | 200 on every call, no 429 |
| `nature` | `real` on every record |
| `model_returned` = `model_requested` | yes on all 20 records |
| `cost_native` | 0 on every record (free route) |
| `reference` column = `reference-td1.csv` | identical for all 20 questions |
| `prompt_sha256` per question | one fingerprint per question (20 distinct), identical to batch D |
| Run window | 13:47:10-13:49:36 UTC, 2026-10-21 |
| Offline replay of the stored SQL (`--replay traces-C.csv`, output not committed) | 12/20 correct, 1 invalid, same verdicts as the real run |

## Result

12 correct, 7 incorrect (C02, C08, C10, C11, C15, C17, C19), 1 sql_invalid (C09), 0 not executed.

| Case | Status | Cause, from the SQL field, checked on the database |
|---|---|---|
| C02 | incorrect (0 vs 590320) | Adds `date('2026-09-25') BETWEEN o.date AND o.date`: keeps only orders whose timestamp equals the text `2026-09-25`; timestamps carry a time, so nothing matches. |
| C08 | incorrect (0 vs 605580) | Adds `date('2026-09-24') >= o.date AND date('2026-09-24') < o.date`: two contradictory conditions, so 0. |
| C09 | sql_invalid | Syntax error near "AS": a column alias `AS age_year` inside the WHERE expression. No value. |
| C10 | incorrect (119410 vs 558980) | Age at the time of the order: keeps only year difference 25 with the birthday passed (119410); misses year difference 26 with the birthday not yet passed (439570). 119410 + 439570 = 558980. |
| C11 | incorrect (0 vs 446690) | Hard-coded bounds select customers born between 2025-12-01 and 2026-11-25; the latest birth date in the base is 2006-08-15, so 0. |
| C15 | incorrect (314020 vs 168680) | The first OR branch accepts every customer aged 0 to 25 on the reference date: 314020 (checked). |
| C17 | incorrect (371990 vs 258180) | Age filter is "born after 2000-09-25", i.e. ages 0 to 25 instead of exactly 25: 371990 (checked). |
| C19 | incorrect (0 vs 1990) | Builds an invalid date modifier (`'-25-01-01'`): `date()` returns NULL, both bounds are NULL, no customer passes, so 0. |

All eight failures are in the age family. Every question without an age filter is correct (C01, C03-C07, C12-C14, C20), and only two of the ten age questions are correct (C16, C18).

## Call count

20 calls, no retry, all at zero cost.
