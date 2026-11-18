# TD 2 : Policies

**Version:** `td2-v2` (18 November 2026, after the code review; `td2-v1` is commit `0dbb1e2`). Based on our TD 1 traces (`traces-td1.csv`, 100 cells + 2 retries) and Lecture 2. Twenty questions measure our method on these questions only, not a guaranteed error rate.

## 1. The policies

| # | policy | rule | why | in code? |
|---|---|---|---|---|
| P1 | Vote | k-of-n with strict majority (`n // 2 < k <= n`), k fixed before the answers | one winner at most; k cannot be lowered after seeing the answers | yes (`vote_k_sur_n`) |
| P2 | Who votes | only an executed query with a value votes; errors stay in n; one model = one vote; retries are not votes | a value without its query cannot be checked | yes |
| P3 | Abstention | if no value reaches k, answer "I don't know" (`None`) | a wrong figure looks right; abstaining is honest | yes |
| P4 | Suspicious 0 | a consensus on 0 is delivered only when the reference population is empty (C06, C14); otherwise it is escalated to the reference query | C02: three different bugs all gave 0 | no (written rule, report section 3.1 principle 4) |
| P5 | Checks by stakes | dashboard: format check only, if the model is 100 % on a family of at least two questions, otherwise a deterministic check (F2b); customer figure: 2-of-3 on period and product questions; payout: reference query. On age questions (F2, F2b, combinations): reference query or deterministic age check for customers, reference query + second person for payouts | quorums failed on age questions (C02, C10) | yes (simulator, `CHECKS`) |
| P6 | Routing | eligible = 100 % right on the question family in TD 1; free routes before the paid route. Ties between free models: keep the gpt-oss models for the families only they pass (F2b, combinations), and prefer a provider other than Groq where several models are at 100 % (F1, F3) | "always cheapest" fails on age questions; "always the best model" sends every question to the same model and stops everything when Groq is down | yes (simulator, `ORDER`; eligibility recomputed from the traces) |
| P7 | Deferral | wait only if the request can wait and a free route resets before the deadline; re-check availability at wake-up | an announced refill time is not a guarantee | yes (simulator, 1-minute reset per free route) |
| P8 | Fallback | never to a model that failed the family; if no route is available, the reference query alone (customer, payout) or abstain (dashboard) | no silent fallback to a weak model | partly (simulator: never a failed model, then abstain; the reference query is not simulated) |
| P9 | New models | not measured = not eligible; a new model is tested in shadow mode (logged, no vote) first | available is not capable | partly (simulator refuses a missing or unmeasured family; no shadow mode) |
| P10 | Traces | one line per attempt; every decision gives its reason with the TD 1 cells | no trace, no defensible decision | yes |

## 2. Key evidence

- Both quorums: 16/20 right, 1/20 wrong, 3/20 abstentions, but 3-of-5 is wrong on C02 and 2-of-3 on C10. A bigger quorum moves errors, it does not remove them.
- `gpt-oss-120b` alone: 20/20. A vote does not beat the best single model; it mainly abstains when weak members disagree.
- Family rates (first model / fallback): F1 period and F3 products: all models 100 %, F2 age at a date: 120b 4/4, qwen 4/4, 20b 3/4, F2b age at the order: only the two gpt-oss models right (1/1), age combinations: only the two gpt-oss models 5/5.
- Weak point: both gpt-oss models are on Groq; if Groq is down, age questions defer, take the paid route or abstain.

## 3. Delays

| setting (skeleton) | value | verdict |
|---|---|---|
| timeout | 45 s | **OK.** Slowest answer in TD 1: 6.4 s (dots, C08). Longer timeouts would only matter for text or very hard tasks (said in Lecture 2; not in the written slides). |
| pause between requests | 3 s | **Too short for gpt-oss-20b.** Its free limit is 8,000 tokens/min; a call uses about 908 tokens (prompt 640 + completion 266; 1,070 with the 162 reasoning tokens counted separately), so ~15 calls/min ask for about twice the limit → 2 of 22 calls refused (429). Pause should be ≈ 60 × 908 / 8,000 ≈ **7 s** (8 s with reasoning) for that model. qwen, rerun with a 15 s pause, had no 429. |
| attempts | 2 (one retry) | **Not always enough:** in batch B both refused calls succeeded on the retry, but in the first run of batch D (3 s pause) C18 was refused twice and not executed; the batch was rerun with `--pause 15`. For production, a longer retry policy (several attempts, about 1 min apart; said in Lecture 2) is safer but too slow for a lab slot. |
| wake-up after 429 | 1 min (policy) | **Policy, not the skeleton's behaviour:** the skeleton retries a 429 once, only when `Retry-After` is at most 60 s (`RETRY_AFTER_MAX_S`). The simulator models a 1-minute reset per free route, since the limits are per minute; availability is re-checked at wake-up. |
| waiting by use | / | dashboard may wait for the refill, customer figure never waits past its deadline, payout never waits for a model (reference query). |
