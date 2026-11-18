# Review 4 – Policies

- Reviewer: Chandra R S Sukumar (in place of Nesrine Aissa, assigned in `review-assignment.md`)
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/td2-policies.md`
- Author: Baudouin Parent

## How it was checked

Reviews 5 and 6 compare the routing rule and the simulator with P5 and P6. This review checks the policies file on its own claims:

1. The "in code?" column of each policy was checked against the code that exists at the reviewed commit: `vote_k_sur_n` (`td2/skeleton-multi-llm-en.py`), the batch rules of the skeleton, and `choose` in `td2/atelier-routage-new.py`.
2. The "Key evidence" section was recomputed from `td1/traces-td1.csv` (last attempt per model and question, families of `td1/questions-td1.json`).
3. The "Delays" table was checked against the skeleton constants, the token counts of the traces, and the first run of batch D (`td1/traces-D-run1.csv`).
4. The references to Lecture 2 were searched in `lectures/cm2-en.html` and in the lecture transcript.

AI assistance was used to recompute the figures and search the sources; the results were read and checked by the reviewer.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `td2/td2-policies.md`, table, rows P5, P6, P8 | The "in code?" column says "yes (simulator)" for P5 (checks by stakes) and P6 (routing), and "yes" for P8 (fallback), but the simulator does not implement them: it has two fixed check strings and no quorum (P5), picks the resource with the smallest allocation instead of "100 % on the family, then cheapest, ties → best TD 1 rate" (P6), and falls back to the fictitious `senior-api` or to Cohere, which failed the family (P8). | `review-6-adrian.md`, findings 1, 3, 4, 5; `choose({family: "F2b_age_at_order"})` returns Cohere. | |
| 2 | important | `td2/td2-policies.md`, table, rows P7, P9 | P7 (deferral) is marked "yes" and P9 (new models) "partly (eligibility only)": in the simulator, deferral only exists for the resource labelled "subscription" (no other resource has a reset time), and an unknown family is accepted by every level-3 resource, so "not measured = not eligible" is not enforced. | `review-6-nazim.md`, findings 2 and 3. | |
| 3 | minor | `td2/td2-policies.md`, Delays, row "pause between requests" | The token count per gpt-oss-20b call is given as about 1 170. The traces give 908 (prompt + completion) or 1 070 if the reasoning tokens counted separately are added, so the suggested pause is about 7 to 8 s, not 9 s. The conclusion (3 s is too short for this model) holds. | `td1/traces-td1.csv`, gpt-oss-20b, 20 HTTP 200 calls: average prompt 640, completion 266, reasoning 162. | |
| 4 | minor | `td2/td2-policies.md`, Delays, row "attempts" | "Enough here: both refused calls succeeded on the retry" only covers batch B. In the first run of batch D, C18 was refused twice (HTTP 429 on both attempts) and was not executed; the run was redone with a 15 s pause. The row should mention it, since it is the case where one retry was not enough. | `td1/traces-D-run1.csv`: 5 HTTP 429, C18 attempts 1 and 2 = 429. | |
| 5 | minor | `td2/td2-policies.md`, Delays, rows "attempts", "timeout" | The figures attributed to Lecture 2 ("up to 10 attempts, 1 min apart", "up to 10 min per Lecture 2") are not found in `lectures/cm2-en.html` nor in the lecture transcript. Give the slide or section, or mark them as said orally. | Search for "attempt", "10 min" in `lectures/cm2-en.html`: only the 10-minute break. | |
| 6 | minor | `td2/td2-policies.md`, Delays, row "wake-up after 429" | The skeleton does not wake up after 1 minute: it retries a 429 once only when `Retry-After` is at most 60 s (`RETRY_AFTER_MAX_S`), otherwise it does not retry. The row describes a policy, not the current behaviour; say which one. | `td1/skeleton-multi-llm-en.py:138`. | |

## What works

- **The key evidence is right**: both quorums give 16/20 correct, 1/20 wrong and 3/20 abstentions; gpt-oss-120b alone is 20/20; F1 and F3 are 100 % for every model; on age at a date gpt-oss-120b and Qwen are 4/4 and gpt-oss-20b 3/4; on age at the order and on age combinations only the two gpt-oss models are right.
- **The single-provider weak point is identified**: both gpt-oss models are on Groq.
- **P1 to P3 and P10 are implemented as stated**: strict majority, errors in n without a vote, one model one vote, abstention without a value, one trace line per attempt with its reason.
- **P4 is honestly marked "no (written rule)"**, and its justification (three different bugs giving 0 on C02) is confirmed by the TD 1 queries.
- **The delays are mostly right**: the slowest answer is 6.4 s (Dots, C08), so the 45 s timeout is safe; gpt-oss-20b had 2 refused calls out of 22; the rerun of Qwen with a 15 s pause had no 429.

## Summary

The policies are sound and their evidence is correct; what overstates is the "in code?" column, which claims that the simulator applies P5 to P8 when it does not yet. Mark these policies "not yet in code" until the simulator is rebuilt, correct the token count, mention the first run of batch D, and source the Lecture 2 figures.
