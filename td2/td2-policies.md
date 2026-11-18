# TD 2 : Policies

**Version:** `td2-v1` (18 November 2026). Based on our TD 1 traces (`traces-td1.csv`, 100 cells + 2 retries) and Lecture 2. Twenty questions measure our method on these questions only, not a guaranteed error rate.

## 1. The policies

| # | policy | rule | why | in code? |
|---|---|---|---|---|
| P1 | Vote | k-of-n with strict majority (`n // 2 < k <= n`), k fixed before the answers | one winner at most; k cannot be lowered after seeing the answers | yes (`vote_k_sur_n`) |
| P2 | Who votes | only an executed query with a value votes; errors stay in n; one model = one vote; retries are not votes | a value without its query cannot be checked | yes |
| P3 | Abstention | if no value reaches k, answer "I don't know" (`None`) | a wrong figure looks right; abstaining is honest | yes |
| P4 | Suspicious 0 | a consensus on 0 is escalated to the reference query when the population should not be empty | C02: three different bugs all gave 0 | no (written rule) |
| P5 | Checks by stakes | dashboard: none, customer figure: 2-of-3, payout: reference query; on age questions (F2, F2b): reference for customers, reference + second person for payouts | quorums failed on age questions (C02, C10) | yes (simulator) |
| P6 | Routing | eligible = 100 % right on the question family in TD 1; then cheapest; ties → best TD 1 rate | "always cheapest" fails on age questions | yes (simulator) |
| P7 | Deferral | wait only if the request can wait and the resource resets before the deadline; re-check availability at wake-up | an announced refill time is not a guarantee | yes |
| P8 | Fallback | never to a model that failed the family; if no model is available, the reference query alone (customer, payout) or abstain (dashboard) | no silent fallback to a weak model | yes |
| P9 | New models | not measured = not eligible; a new model is tested in shadow mode (logged, no vote) first | available is not capable | partly (eligibility only) |
| P10 | Traces | one line per attempt; every decision gives its reason with the TD 1 cells | no trace, no defensible decision | yes |

## 2. Key evidence

- Both quorums: 16/20 right, 1/20 wrong, 3/20 abstentions, but 3-of-5 is wrong on C02 and 2-of-3 on C10. A bigger quorum moves errors, it does not remove them.
- `gpt-oss-120b` alone: 20/20. A vote does not beat the best single model; it mainly abstains when weak members disagree.
- Family rates (first model / fallback): F1 period and F3 products: all models 100 %, F2 age at a date: 120b 4/4, qwen 4/4, 20b 3/4, F2b age at the order: only the two gpt-oss models right (1/1), age combinations: only the two gpt-oss models 5/5.
- Weak point: both gpt-oss models are on Groq; if Groq is down, age questions go to the reference query or abstain.

## 3. Delays

| setting (skeleton) | value | verdict |
|---|---|---|
| timeout | 45 s | **OK.** Slowest answer in TD 1: 6.4 s (dots). Too long would only matter for text or very hard tasks (up to 10 min per Lecture 2). |
| pause between requests | 3 s | **Too short for gpt-oss-20b.** Its free limit is 8,000 tokens/min; at ~15 calls/min × ~1,170 tokens we asked about twice that → 2 of 22 calls refused (429). Pause should be ≈ 60 × 1,170 / 8,000 ≈ **9 s** for that model. qwen, paced ~15 s, had no 429. |
| attempts | 2 (one retry) | **Enough here:** both refused calls succeeded on the retry. For production, Lecture 2's policy (up to 10 attempts, 1 min apart) is safer but too slow for a lab slot (up to 10 min per cell). |
| wake-up after 429 | 1 min | **OK:** the limit is per minute. Availability is re-checked at wake-up. |
| waiting by use | / | dashboard may wait for the refill, customer figure never waits past its deadline, payout never waits for a model (reference query). |
