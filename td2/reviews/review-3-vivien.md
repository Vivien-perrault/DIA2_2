# Review 3 – Wrong consensus (C10, C02, DEMO-VOTE, DEMO-SQL-C11)

- Reviewer: Vivien Perrault
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/reports/td2.md` section 2 (2.0 to 2.10), `td2/sql/`
- Authors: Baptiste Marseille, Nazim Yacine, Akihito Raffin

## How it was checked

1. Section 2 was read from the reviewed commit (`git show 175f4b4:td2/reports/td2.md`).
2. Every `.sql` file of `td2/sql/` was executed on `td1/data/boutique.sqlite` opened read-only, and every result was compared with the figure printed in the report.
3. The diagnosis of section 2.5 was checked against the two model queries, and the claim on the missed customers (2.8) against their birth dates and order dates.
4. The section was checked against what Q2 level 2 asks: identified case, agreeing values, independent reference, declared quorum distinguished from the agreement, cause in the SQL, independent check able to detect it, nature of each example.
5. `td2/sql/relecture.py` was read to see what it actually compares.

AI assistance was used to execute the queries and read the script; the results were read and checked by the reviewer.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `td2/reports/td2.md`, section 2.7 | DEMO-SQL-C11 is said to be reproduced "as the TD 2 assignment gives it", but the assignment in the repository (`td2/enonce-td2-en.md`, pack 2026-10-18) contains no DEMO-SQL-C11, M1 or M2. The source of a historical case is part of what Q2 checks: cite the version used (online course page, URL and date consulted) or copy the excerpt into the repository. | `grep -i "C11\|DEMO-SQL" td2/enonce-td2-en.md` finds nothing. | accepted: no traceable source found in time; labelled as a replayed historical case |
| 2 | minor | `td2/sql/relecture.py:3`, `td2/reports/td2.md`, section 2.9 | The script is described as comparing each result "with the figure written in the report", but it never reads `td2.md`: the expected values are literals copied into the script. If the report is edited, the 36 checks still pass. Reword ("values copied from the report") or read the figures from the report. | The only mention of `td2.md` in the script is its docstring. | fixed in `b03ea80` (Baptiste Marseille) |
| 3 | minor | `td2/reports/td2.md`, section 2.8, "Méthode de contrôle" | Both detection methods need a reference written for that exact question. For a new question, with no reference yet, they do not apply. A check of the age convention itself (for example recomputing the completed age of each returned customer in Python, or a small test set with birthdays on the boundary dates) would detect the C10 error without a per-question reference, and it is the "deterministic check" that the routing rule asks for. | – | fixed in `b03ea80` (Baptiste Marseille) |
| 4 | minor | `td2/reports/td2.md`, section 2.7 | M1 is attributed to gpt-oss-20b and M2 to Cohere in the September pilot. In our own batch, gpt-oss-20b is right on C11 (446 690) and Cohere also returns 0, with a different query. One sentence would avoid a reader confusing the pilot answers with ours. | `td1/traces-td1.csv`, C11: gpt-oss-20b `correct` 446 690, Cohere `incorrect` 0. | fixed in `b03ea80` (Baptiste Marseille) |
| 5 | minor | `td2/reports/td2.md`, sections 2.2-2.3 | The counter-example C02 (wrong consensus at 0 in 3-of-5) gives no cause in the SQL; the three different causes of the C02 zeros are documented in `td1/verif/` (batches B, C, E) and could be linked. Same finding as review 2 (Ismaël, finding 3). | – | fixed in `b03ea80` (Baptiste Marseille) |

## What works

- **Every query reproduces the report**: `C10-cohere.sql` 119 410, `C10-qwen.sql` 119 410, `C10-reference.sql` 558 980, `C11-M1` 0, `C11-M2` 0; `delta-C10.sql` gives C004, C005, C007 and C022 for both models (439 570 cents missed, 0 added); `delta-C11.sql` gives 6 customers and 446 690 cents.
- **The diagnosis is right**: both models test "year difference 25 and birthday reached" and miss the orders placed before the 26th birthday in the following calendar year; Qwen's second branch targets age 23 and selects nothing. The four missed customers were born in 2000 and all their counted orders fall in 2026 before their 26th birthday.
- **Q2 level 2 is covered**: identified case (C10, `cell_id` listed), agreeing values, independent reference with its `checked_by`, 2-of-3 and 3-of-5 results kept apart from the agreement, cause in the `WHERE` clause, and a detection method that does not rely on the vote.
- **Natures are labelled**: DEMO-VOTE as a constructed example, DEMO-SQL-C11 as a replayed historical case, C10 as `real`.
- `relecture.py` runs and its 36 checks pass.

## Summary

The wrong-consensus case is complete, correct and reproducible. To fix: give a traceable source for DEMO-SQL-C11, describe `relecture.py` accurately, and add a generic age check to the detection method so that it also works for a question without a reference.
