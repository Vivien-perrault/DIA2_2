# TD 2 – Fix plan after the code review

Deadline: before 17:00. Order = impact on the marking (Q3 first, then Q2, then hygiene). Each fix references the review findings it closes; when it is done, write the commit hash in the "Fix" column of each finding.

## Decision to take first (blocks every Q3 fix)

**First model per family when several free models are at 100 %.** Applying P6 as written ("ties → best TD 1 rate") sends every family to gpt-oss-120b, and Q3 level 0 is "a rule that sends every question to the same model". Proposed tie-break, to write in P6, the rule and the simulator:

> Among the free models at 100 % on the family, keep the gpt-oss models for the families only they pass, and prefer a provider other than Groq, so that a Groq limit or outage does not stop every family.

| Family (TD 1 cells) | First model | Fallback order | Why |
|---|---|---|---|
| F1 period (C01, C04-C07, C20) | Cohere (OpenRouter) | Dots (OpenRouter), Qwen (Groq), gpt-oss-120b (Groq), defer, paid gpt-oss-120b (OpenRouter), abstain | all five 6/6; other provider than Groq |
| F3 product list (C03, C12-C14) | Cohere (OpenRouter) | same as F1 | all five 4/4 |
| F2 age at a date (C02, C08, C09, C11) | Qwen (Groq) | gpt-oss-120b (Groq), defer, paid gpt-oss-120b, abstain | Qwen and gpt-oss-120b 4/4; keeps gpt-oss-120b for F2b and combinations |
| F2b age at the order (C10) | gpt-oss-120b (Groq) | gpt-oss-20b (Groq), defer, paid, abstain | only the two gpt-oss models 1/1 |
| Combinations (C15-C19) | gpt-oss-120b (Groq) | gpt-oss-20b (Groq), defer, paid, abstain | only the two gpt-oss models 5/5 |

## Fixes by review

### Review 6 (Adrian, Nazim) + Review 4 (Chandra) – simulator `td2/atelier-routage-new.py` — priority 1, ~40 min

| # | Fix | Closes |
|---|---|---|
| S1 | Rebuild `RESOURCES` with the five real models: provider, price (0 on the free route), families at 100 % and the exact TD 1 cells, from `compute_accuracy.py` (corrected). Remove `senior-subscription` / `senior-api`; add the paid route `openai/gpt-oss-120b#openrouter` (0.15 / 0.60 USD per million tokens). | R6-Adrian 1, 2, 4, 9; R6-Nazim 5, 6 |
| S2 | Rewrite `choose`: refuse a missing or unknown family; eligible = 100 % on the family; pick the first model of the table above, then the fallback order; defer when the request can wait and the model resets before the deadline; paid route within budget; abstain. | R6-Adrian 3; R6-Nazim 1, 2; R4-Chandra 1, 2 |
| S3 | Checks by use (dashboard / customer / payout) per family, as in the rule. | R6-Adrian 5; R4-Chandra 1 |
| S4 | A reset time per free model (1 min for a per-minute limit), so that `defer` works for every model. | R6-Nazim 3; R4-Chandra 2 |
| S5 | Scenarios: the 7 original ones + one per family (C10 included) + "first model unavailable" for each. | R6-Adrian 6; R6-Nazim 4 |
| S6 | Save the outputs before (`atelier-routage.py`) and after (`atelier-routage-new.py`) in `td2/simulator-before.jsonl` and `td2/simulator-after.jsonl`; link them from the report. | R6-Adrian 7; R5-Adrian 7 |

### Review 5 (Baptiste, Adrian) – routing rule, `td2/reports/td2.md` section 3 — priority 1, ~15 min

| # | Fix | Closes |
|---|---|---|
| R1 | Apply the first models and fallback orders of the table above; state the tie-break. | R5-Adrian 1, 2, 3; R5-Baptiste 1, 6 |
| R2 | State the Groq dependency for F2, F2b and combinations. | R5-Baptiste 2 |
| R3 | Payout: reference query (P5), no 3-of-5; add the rule for a consensus on 0 (P4: accepted only when the reference population is empty, e.g. C06, C14). | R5-Baptiste 3, 4 |
| R4 | Principle 3: a family of one question (F2b) never qualifies for `none`. | R5-Baptiste 5 |
| R5 | Wording: Qwen is on Groq; the 2-of-3 panel "abstains" on C15, C17, C19; remove the unsourced "sans limite TPM" for gpt-oss-120b; link the simulator outputs. | R5-Adrian 4, 5, 6, 7 |

### Review 4 (Chandra) – policies `td2/td2-policies.md` — priority 1, ~10 min

| # | Fix | Closes |
|---|---|---|
| P1 | Rewrite the P6 tie-break as above. | R5-Adrian 3; R5-Baptiste 6 |
| P2 | "in code?" column: true after S1-S5, otherwise "not yet". | R4-Chandra 1, 2 |
| P3 | Delays: ~908 tokens per call (1 070 with reasoning) → pause ≈ 7-8 s; mention C18 refused twice in the first run of batch D; source the Lecture 2 figures or mark them "said in lecture"; say the 1-minute wake-up is a policy, the skeleton retries only if `Retry-After` ≤ 60 s. | R4-Chandra 3, 4, 5, 6 |

### Review 1 (Akihito) – vote — priority 2, ~10 min

| # | Fix | Closes |
|---|---|---|
| V1 | Keep the `td2/` implementation; refuse a non-integer value instead of `int()` truncation; fix the comment on dictionaries. | R1 1, 4 |
| V2 | Make `td1/` identical to `td2/` (or point it to the same code), so that a single behaviour exists. | R1 2, 3 |
| V3 | Note in the TD 2 README that the `td2/` skeleton copy only serves the vote. | R1 5 |

After V1-V2: rerun `atelier-vote.py` on C10 and C15 and `relecture.py` (must stay "Tout est conforme").

### Review 2 (Ismaël, Chandra) – table of the 20 decisions — priority 2, ~10 min

| # | Fix | Closes |
|---|---|---|
| T1 | Declare the 3-of-5 panel as exploratory (two gpt-oss models, not distinct families). | R2-Ismaël 1 |
| T2 | C02: "two providers, three families"; point the C02 causes to `td1/verif/`; say that "best single model" is a hindsight comparison. | R2-Ismaël 2, 3, 4 |
| T3 | Commit `compare-vote.py` (ask Baudouin) or remove the mention; give paths. | R2-Chandra 1, 2; R2-Ismaël 5 |
| T4 | Move `votes-20-questions.jsonl` into `td2/` without the BOM; link it. | R2-Chandra 3, 4 |

### Review 3 (Vivien) – wrong consensus — priority 3, ~10 min

| # | Fix | Closes |
|---|---|---|
| W1 | Source of DEMO-SQL-C11: online course page URL and date consulted, or copy the excerpt. | R3 1 |
| W2 | `relecture.py`: say "expected values copied from the report". | R3 2 |
| W3 | Detection method: add a generic age check (boundary birthdays). | R3 3 |
| W4 | C11 sentence on our own batch; link the C02 causes. | R3 4, 5 |

### Reviews 7 (Baudouin) and 8 (Antonin) — pending

To add when pushed. Known for the README (item 8): the open points are out of date (`atelier-vote.py` fixed in `fb349cd`; both votes give the same 40 decisions).

## End

1. Fill the "Fix" column of every review with the commit hash.
2. Update `td2/README.md` (deliverables, cross-checks, contributions including the reviews and the replacement of Nesrine).
3. Push the **post code review** checkpoint commit.
