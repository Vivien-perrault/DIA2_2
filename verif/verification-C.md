# Verification of batch C: openrouter:cohere/north-mini-code:free

- Operator: _(name of the operator of batch C)_
- Checked by: _(name of the checker)_
- Date of check: 2026-10-21
- OpenRouter account used: Adrian BERNARD's personal account (distinct from the account used for batch E)
- Files checked: `traces-C.csv`, `state-C.jsonl`, against `reference-td1.csv`
- Comparison rows produced: [`comparison-C.csv`](comparison-C.csv), to merge into `model-question-comparison-en.csv`

## Run

```bash
python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --pause 5 --state state-C.jsonl --out traces-C.csv
```

The pause was set to 5 seconds instead of the default 3 to stay under OpenRouter's request-per-minute limit on free models, after the HTTP 429 seen on Groq for batch D. Prompt, references, model and parameters are unchanged.

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
| Run window | 13:43:11-13:45:33 UTC, 2026-10-21 |
| Offline replay of the stored SQL (`--replay traces-C.csv`, output not committed) | 12/20 correct, 1 invalid, same verdicts as the real run |

## Result

12 correct, 7 incorrect (C08, C09, C10, C11, C17, C18, C19), 1 sql_invalid (C02), 0 not executed.

| Case | Status | Cause, from the SQL field, checked on the database |
|---|---|---|
| C02 | sql_invalid | Syntax error near "AS": a cast-like `AS 'YYYY-MM-DD'` inside `date()`. No value. |
| C08 | incorrect (0 vs 605580) | Adds a condition keeping only orders placed on the reference day 2026-09-24; there is no order that day, so 0. |
| C09 | incorrect (0 vs 487980) | The age formula never subtracts from the reference year: it compares about 2000 (birth year) with 25, never true, so 0. |
| C10 | incorrect (119410 vs 558980) | Age at the time of the order: keeps only year difference 25 with the birthday passed (119410); misses year difference 26 with the birthday not yet passed (439570). 119410 + 439570 = 558980. |
| C11 | incorrect (768850 vs 446690) | The julianday condition is always true, so the filter becomes "born after 2000-12-01": every customer aged 0 to 25 is counted (768850, checked on the database). |
| C17 | incorrect (197080 vs 258180) | Builds `month-year` (e.g. `03-2001`) instead of `month-day`, so the birthday test only uses the month: 2001 births January-September plus 2000 births October-December = 197080 (checked). C002, C003 (2001-09-24/26) and C004, C005 (2000-09-25/26) are misclassified. |
| C18 | incorrect (95600 vs 62480) | Age at the time of the order: compares month and day separately instead of month-day together, and the first branch accepts age 25 or more; that branch alone gives 95600 (checked). |
| C19 | incorrect (0 vs 1990) | Subtracts date strings as numbers (`'2026-09-25' - birth_date` = 25, then / 10000 = 0): the computed age is 0 and no customer passes the bounds. |

All eight failures are in the age family. Every period and product question without an age filter is correct (C01, C03-C07, C12-C14, C20), and only two of the ten age questions are correct (C15, C16).

## Call count

20 calls on the OpenRouter account, no retry, all at zero cost. The earlier `check_access.py` run used one call to this model on the same account; it is counted separately.
