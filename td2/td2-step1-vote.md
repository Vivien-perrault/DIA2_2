## Step 1 - k-of-n vote: fixed 2-of-3 panel vs 3-of-5 quorum

**Method.** `Orchestrateur.vote_k_sur_n` (in [`skeleton-multi-llm-en.py`](skeleton-multi-llm-en.py), the same implementation as in `td1/`) is run on the latest stored attempt of each model for each question ([`../td1/traces-td1.csv`](../td1/traces-td1.csv), nature = real, no new network call). The vote never receives the reference: a trace with a value becomes an `executed` proposal, anything else (invalid SQL, access error, missing trace) is an `error` that stays in n and casts no vote. The comparison with [`../td1/reference-td1.csv`](../td1/reference-td1.csv) is done after the decision. The table below is printed by [`compare-vote.py`](compare-vote.py); the raw decisions are in [`votes-20-questions.jsonl`](votes-20-questions.jsonl) (2-of-3, output of `atelier-vote.py`) and [`votes-3of5.jsonl`](votes-3of5.jsonl) (3-of-5).

- 2-of-3: fixed panel `openai/gpt-oss-120b`, `cohere/north-mini-code:free`, `qwen/qwen3.8-27b`, k = 2.
- 3-of-5: the five TD 1 models, k = 3. **Exploratory panel**: it contains two models of the same family (`gpt-oss-120b` and `gpt-oss-20b`), whereas the assignment asks for a panel of distinct families. Its results are shown for comparison, not as a quorum we would deploy.

### Results on C01–C20

| case | reference | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | north-mini-code | dots-3-note-preview | 2-of-3 | 2/3 vs ref | 3-of-5 | 3/5 vs ref | decision changes? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | 792800 | 792800 | 792800 | 792800 | 792800 | 792800 | 792800 (3 votes) | OK | 792800 (5 votes) | OK |  |
| C02 | 590320 | 590320 | 0 | 590320 | 0 | 0 | 590320 (2 votes) | OK | 0 (3 votes) | WRONG | **yes** |
| C03 | 936350 | 936350 | 936350 | 936350 | 936350 | 936350 | 936350 (3 votes) | OK | 936350 (5 votes) | OK |  |
| C04 | 2826250 | 2826250 | 2826250 | 2826250 | 2826250 | 2826250 | 2826250 (3 votes) | OK | 2826250 (5 votes) | OK |  |
| C05 | 38480 | 38480 | 38480 | 38480 | 38480 | 38480 | 38480 (3 votes) | OK | 38480 (5 votes) | OK |  |
| C06 | 0 | 0 | 0 | 0 | 0 | 0 | 0 (3 votes) | OK | 0 (5 votes) | OK |  |
| C07 | 13970 | 13970 | 13970 | 13970 | 13970 | 13970 | 13970 (3 votes) | OK | 13970 (5 votes) | OK |  |
| C08 | 605580 | 605580 | 605580 | 605580 | 0 | 0 | 605580 (2 votes) | OK | 605580 (3 votes) | OK |  |
| C09 | 487980 | 487980 | 487980 | 487980 | err | 0 | 487980 (2 votes) | OK | 487980 (3 votes) | OK |  |
| C10 | 558980 | 558980 | 558980 | 119410 | 119410 | err | 119410 (2 votes) | WRONG | abstain (max 2) | abstain | **yes** |
| C11 | 446690 | 446690 | 446690 | 446690 | 0 | 446690 | 446690 (2 votes) | OK | 446690 (4 votes) | OK |  |
| C12 | 1666490 | 1666490 | 1666490 | 1666490 | 1666490 | 1666490 | 1666490 (3 votes) | OK | 1666490 (5 votes) | OK |  |
| C13 | 107740 | 107740 | 107740 | 107740 | 107740 | 107740 | 107740 (3 votes) | OK | 107740 (5 votes) | OK |  |
| C14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 (3 votes) | OK | 0 (5 votes) | OK |  |
| C15 | 168680 | 168680 | 168680 | 0 | 314020 | err | abstain (max 1) | abstain | abstain (max 2) | abstain |  |
| C16 | 376740 | 376740 | 376740 | 376740 | 376740 | 376740 | 376740 (3 votes) | OK | 376740 (5 votes) | OK |  |
| C17 | 258180 | 258180 | 258180 | 248490 | 371990 | 189870 | abstain (max 1) | abstain | abstain (max 2) | abstain |  |
| C18 | 62480 | 62480 | 62480 | 62480 | 62480 | 39580 | 62480 (3 votes) | OK | 62480 (4 votes) | OK |  |
| C19 | 1990 | 1990 | 1990 | 83580 | 0 | 1990 | abstain (max 1) | abstain | 1990 (3 votes) | OK | **yes** |
| C20 | 1106090 | 1106090 | 1106090 | 1106090 | 1106090 | 1106090 | 1106090 (3 votes) | OK | 1106090 (5 votes) | OK |  |

| panel | correct consensus | wrong consensus | abstentions |
|---|---|---|---|
| 2-of-3 | 16/20 | 1/20 (C10) | 3/20 (C15, C17, C19) |
| 3-of-5 | 16/20 | 1/20 (C02) | 3/20 (C10, C15, C17) |

### Commentary

**Same totals, different errors.** Both panels score 16/20 correct, 1/20 wrong and 3/20 abstentions, but not on the same questions: the decision changes on 3/20 questions (C02, C10, C19). Going from 3 to 5 voters does not reduce the number of errors here; it moves them.

**C02: 2-of-3 correct, 3-of-5 wrong consensus.** `gpt-oss-120b` and `qwen3.8-27b` both return the reference 590320, so the fixed panel is right (cohere's 0 is outvoted). In the 3-of-5 quorum, the two models added to the panel (`gpt-oss-20b`, `dots-3-note-preview`) both return 0, like cohere: three models from three different families, but only two providers (Cohere and Dots both go through OpenRouter), reach k = 3 on the same wrong value. Adding voters added a correlated error. A value of 0 means the faulty queries' filter matched no order line; the three different clauses are analysed in the TD 1 verification notes ([batch B](../td1/verif/verification-B.md), [batch C](../td1/verif/verification-C.md), [batch E](../td1/verif/verification-E.md)).

**C10: 2-of-3 wrong consensus, 3-of-5 abstains.** `qwen3.8-27b` and `north-mini-code` agree on 119410 (reference 558980) and win the fixed panel against `gpt-oss-120b`. In the 3-of-5 quorum, `gpt-oss-20b` joins `gpt-oss-120b` on the reference, `dots` fails (error, counted in n), and the vote is 2 against 2: no value reaches k = 3, so the quorum abstains. Here the larger quorum turns a wrong answer into an abstention, which is the safe outcome.

**C19: 2-of-3 abstains, 3-of-5 correct.** The three panel members return three different values (1990, 83580, 0), so the fixed panel abstains. In the 3-of-5 quorum, `gpt-oss-20b` and `dots` join `gpt-oss-120b` on 1990 and reach k = 3. Caveat: two of these three votes come from the same family (`gpt-oss-120b` and `gpt-oss-20b`, both OpenAI open-weight models), so this consensus is less independent than its vote count suggests.

**Questions where both panels abstain: C15 and C17.** Only the two `gpt-oss` models return the reference; the other three disagree with them and with each other (on C17 the five models return four different values). These are questions where no quorum gives an answer, and therefore candidates for a deterministic check or a human review in the routing rule (step 3) and for the checking cost in TD 3.

**Other shared wrong values (outvoted).** C08: `north-mini-code` and `dots` both return 0 (reference 605580), outvoted in both panels. Single wrong values (C09 dots 0, C11 cohere 0, C18 dots 39580) are outvoted as well.

**A vote does not beat the best single model on these traces, in hindsight.** `gpt-oss-120b` alone is correct on 20/20 cases and `gpt-oss-20b` on 19/20 (wrong on C02), whereas each panel is correct on 16/20. But the best single model is only known after comparing every answer with the references: without them, a single model gives no signal when it is wrong, whereas the vote abstains on C15, C17 and C19. The vote mainly protects against weak members by abstaining; it cannot add correctness that the majority of the panel lacks, and a consensus is not a proof of correctness (C02, C10). This is measured on one batch of 20 questions at temperature 0, one attempt per cell: it is a property of these traces, not a general ranking.
