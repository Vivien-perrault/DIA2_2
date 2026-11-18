# Review 1 – `vote_k_sur_n` and the vote workshop

- Reviewer: Akihito Raffin
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/skeleton-multi-llm-en.py` (`vote_k_sur_n`, sandbox path), `td1/skeleton-multi-llm-en.py` (`vote_k_sur_n` only), `td2/atelier-vote.py`
- Authors: Baudouin Parent (`td2/` vote), Baptiste Marseille (`td1/` vote), Nazim Yacine (sandbox path), Ismaël Wane (`atelier-vote.py` path)

## How it was checked

1. Both implementations were read against the five rules of the contract (docstring and `td2/enonce-td2-en.md`, Step 1).
2. Both were run on nine edge cases built by hand: `k` given as a boolean or a float, an empty panel, a value given as a string or as a non-integer number, a value of 0, a duplicate member among the errors, proposals given as dictionaries, a panel where every member fails.
3. `td2/atelier-vote.py` and `td2/skeleton-multi-llm-en.py` were compared with the kit version (commit `a9c1cde`).
4. The 4 synthetic examples and the real questions C10 and C15 were run with `atelier-vote.py`.

AI assistance was used to write and run the edge cases; the results were read and checked by the reviewer.

## Edge cases

| Case | `td1/` (Baptiste) | `td2/` (Baudouin) | Contract |
|---|---|---|---|
| `k = True`, n = 1 | consensus 1 | `ValueError` | k must be an integer strict majority |
| `k = 2.0`, n = 3 | consensus 1 | `ValueError` | same |
| n = 0, k = 1 | `ValueError` | `ValueError` | refused (no strict majority) |
| values `"100"`, `100`, `5` | abstain (1 vote) | consensus **100** (2 votes) | values are integer cents |
| values `100.7`, `100`, `5` | abstain (1 vote) | consensus **100** (2 votes) | must not invent a value |
| values `0`, `0`, `5` | consensus 0 | consensus 0 | 0 is a value and votes |
| duplicate member among errors | `ValueError` | `ValueError` | duplicate refused |
| proposals as dictionaries | `AttributeError` | consensus 1 | contract: attributes |
| every member fails | abstain, 0 votes | abstain, 0 votes | abstain |

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `td2/skeleton-multi-llm-en.py:652` | `int(valeur)` silently converts every vote: `100.7` becomes `100` and then agrees with a real `100`. The contract says values are integer cents and the vote never invents a value; a non-integer value should be refused (or kept as is), not truncated into an agreement. | Edge case `100.7, 100, 5`: `td2/` returns consensus 100 with 2 votes. | |
| 2 | important | `td1/skeleton-multi-llm-en.py:603-650`, `td2/skeleton-multi-llm-en.py:604-660` | Two implementations of the same method coexist and behave differently on 5 of the 9 edge cases. They give the same 40 decisions on the real traces, but the plan steps 3 and 4 used `td1/` while the table of the 20 decisions and `atelier-vote.py` now use `td2/`. One must be kept and the other removed or made identical. | Edge-case table above. | |
| 3 | minor | `td1/skeleton-multi-llm-en.py:628` | `td1/` accepts a boolean or a float `k` (`True`, `2.0`), because only the inequality is tested. | Edge cases `k = True` and `k = 2.0`. | |
| 4 | minor | `td2/skeleton-multi-llm-en.py:628-630` | The comment says proposals can be dictionaries "(atelier-vote.py)", but `atelier-vote.py` builds `SimpleNamespace` objects; the dictionary branch is never used by the workshop. | `td2/atelier-vote.py`, `proposals_for`. | |
| 5 | minor | `td2/skeleton-multi-llm-en.py` | The `td2/` copy only finds the sandbox in `../td1/`: every other resource (database, questions, references, models) is still looked up next to it, so the copy can only serve the vote. `--run` and `--replay` fail from `td2/`. | `python skeleton-multi-llm-en.py --replay ../td1/traces-td1.csv` from `td2/`: `FileNotFoundError: db`. | |

## What works

- Both implementations respect the five rules on every real case: an error stays in n without voting, k must be a strict majority, a duplicate member is refused, a value reaching k is returned with its models, otherwise the vote abstains with the largest count.
- `atelier-vote.py` differs from the kit only by the path to the skeleton and the example command; the 4 synthetic examples give the expected decisions (agreement, disagreement, unavailable member, wrong consensus), C10 gives the wrong consensus at 119 410 and C15 abstains.
- The `td2/` skeleton differs from the kit only by `vote_k_sur_n` and the extra sandbox path: the prompt and the rest of the code are unchanged.

## Summary

The vote is correct for Q1 on the real traces. Before the post code review checkpoint: keep a single implementation, make it refuse non-integer values instead of truncating them and refuse a non-integer `k`, and either remove the `td2/` copy or make it find all its resources in `../td1/`.
