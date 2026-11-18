# Review 2 – Table of the 20 vote decisions (second reviewer)

- Reviewer: Chandra R S Sukumar (second reviewer; first reviewer: Ismaël Wane)
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/td2-step1-vote.md`, `votes-20-questions.jsonl`
- Authors: Baudouin Parent, Antonin Charron

## How it was checked

Every figure was recomputed independently, not copied from the files under review:

1. From `td1/traces-td1.csv`, keep the last attempt of each (model, question): 100 cells.
2. A cell with a value (`correct` or `incorrect`) becomes an `executed` proposal; `sql_invalid` or no value becomes an `error` that stays in n.
3. Run `Orchestrateur.vote_k_sur_n` from `td2/skeleton-multi-llm-en.py` on the fixed panel (gpt-oss-120b, north-mini-code, qwen3.8-27b, k = 2) and on the five models (k = 3).
4. Compare each decision with `td1/reference-td1.csv` after the vote, then rebuild every column of the table and compare it cell by cell with `td2-step1-vote.md`.
5. Compare the 20 records of `votes-20-questions.jsonl` with the recomputed 2-of-3 decisions.

AI assistance was used to write the recomputation script; the results were read and checked by the reviewer.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `td2/td2-step1-vote.md:3` | The method cites a script `compare-vote.py` that is not in the repository: the table cannot be regenerated with the stated method. | `compare-vote.py` absent from the whole repository at `175f4b4`. | fixed in `bdfa625` (Baudouin Parent) |
| 2 | minor | `td2/td2-step1-vote.md:3` | File names are given without paths or links (`skeleton-multi-llm-en.py`, `traces-td1.csv`). Two copies of the skeleton exist (`td1/` and `td2/`); the method does not say which one was used. | Both implementations give the same 40 decisions (checked), so the result is not affected. | fixed in `bdfa625` (Baudouin Parent) |
| 3 | minor | `votes-20-questions.jsonl` | The raw vote output sits at the repository root instead of `td2/`, and no TD 2 document links to it. | `grep votes-20-questions` finds it only in `review-assignment.md`. | fixed in `bdfa625` (Baudouin Parent) |
| 4 | minor | `votes-20-questions.jsonl:1` | The file starts with a UTF-8 byte order mark (`EF BB BF`, typical of a PowerShell redirect): a standard JSONL reader fails on line 1. | `json.loads` raises "Unexpected UTF-8 BOM" on the first line. | fixed in `1b05465` (Antonin Charron) |
| 5 | minor | `votes-20-questions.jsonl` | The raw output covers the 2-of-3 panel only; the 3-of-5 column of the table has no raw output file. | 20 records, all with `n = 3`, `k = 2`. | fixed in `bdfa625` (Baudouin Parent) |

## What works

- **All 20 rows of the table match** the recomputation, column by column: the five model values, both decisions with their votes, both comparisons with the reference and the "decision changes" column (C02, C10, C19).
- **The summary is correct**: both panels give 16/20 correct, 1/20 wrong consensus (C10 for 2-of-3, C02 for 3-of-5) and 3/20 abstentions.
- **`votes-20-questions.jsonl` matches** the recomputed 2-of-3 decisions on all 20 questions, all `nature = real`.
- **The commentary is supported by the traces**: C17 has four distinct values over five models; the shared wrong value on C08 (north-mini-code and dots, 0) is outvoted in both panels; the single wrong values (C09 dots 0, C11 north-mini-code 0, C18 dots 39580) are outvoted; gpt-oss-20b is wrong only on C02.
- The vote never receives the reference: the comparison is done after the decision.

## Summary

The table and its conclusions are correct and reproducible from the traces. The fixes are about reproducibility and file hygiene: commit or remove `compare-vote.py`, give paths, move the JSONL into `td2/` without the BOM, and optionally add the 3-of-5 raw output.
