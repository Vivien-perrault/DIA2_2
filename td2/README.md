# TD 2 – The quorum, then the routing rule

Sub-group **DIA2_2** (Majeure DIA, ESILV). Session 2, 18 November 2026.
Assignment: [enonce-td2-en.md](enonce-td2-en.md). Report: [reports/td2.md](reports/td2.md).

> **Skeleton, written during the session.** Sections marked _To complete_ will be filled in once the corresponding deliverables are pushed.

## Inputs

TD 2 makes **no new network call**. It reuses the real TD 1 traces:

- [../td1/traces-td1.csv](../td1/traces-td1.csv): 102 calls, 5 models × 20 questions;
- [../td1/reference-td1.csv](../td1/reference-td1.csv): the 20 checked references;
- [../td1/data/boutique.sqlite](../td1/data/boutique.sqlite): the database, unchanged.

## Deliverables

| # | Deliverable (assignment) | Status | Where |
|---|---|---|---|
| 1 | `vote_k_sur_n` completed | Done | [skeleton-multi-llm-en.py](skeleton-multi-llm-en.py) (see "Open points") |
| 2 | Table of the 20 vote decisions | Done: 2-of-3 panel and 3-of-5 quorum | [td2-step1-vote.md](td2-step1-vote.md) |
| 3 | Commented wrong consensus (C10, counter-example C02, supplementary DEMO-VOTE and DEMO-SQL-C11) | In progress: plan steps 1 to 9 done, 10 to 12 left | [reports/td2.md](reports/td2.md), [sql/](sql/), plan [../PLAN-TD2-ETAPE2.md](../PLAN-TD2-ETAPE2.md) |
| 4 | One-page routing rule, justified by TD 1 cells | _To complete_ | _To complete_ |
| 5 | Simulator outputs, before and after adaptation | _To complete_ | _To complete_ |
| 6 | Prompts, if changed since TD 1 | Unchanged: no new call | [../td1/prompts-en.md](../td1/prompts-en.md) |

## Vote: summary

| Panel | Correct consensus | Wrong consensus | Abstentions |
|---|---|---|---|
| Fixed 2-of-3 (GPT-OSS 120B, Cohere, Qwen) | 16/20 | 1/20 (C10) | 3/20 (C15, C17, C19) |
| 3-of-5 (the five TD 1 models) | 16/20 | 1/20 (C02) | 3/20 (C10, C15, C17) |

| Question | 2-of-3 | 3-of-5 | Reference |
|---|---|---|---:|
| **C10** | **wrong** consensus at 119 410 (Cohere + Qwen) | abstention (2 against 2) | 558 980 |
| C02 | correct at 590 320 | **wrong** consensus at 0 | 590 320 |

Full table and commentary: [td2-step1-vote.md](td2-step1-vote.md). Cause and proof for C10: [reports/td2.md](reports/td2.md), sections 2.4 to 2.6, and [sql/delta-C10.sql](sql/delta-C10.sql).

## Routing rule

_To complete: one line per family (period, age on a date, age at the order, product list, combinations), with the first model called, the check retained for each use, what to do when the model is unavailable, and the TD 1 cell that justifies each line._

## Files

| File | Role |
|---|---|
| [skeleton-multi-llm-en.py](skeleton-multi-llm-en.py) | TD 2 copy of the skeleton, with `vote_k_sur_n`; `atelier-vote.py` uses this local copy first |
| [atelier-vote.py](atelier-vote.py) | Runs `vote_k_sur_n` on 4 synthetic examples, then on the real traces with the fixed 2-of-3 panel. Modified to fall back on `../td1/` for the skeleton. |
| [atelier-routage.py](atelier-routage.py) | Routing simulator, 7 scenarios, fictitious resources, no network call |
| [td2-step1-vote.md](td2-step1-vote.md) | Table of the 20 decisions, 2-of-3 and 3-of-5, with commentary |
| [sql/demo-vote.py](sql/demo-vote.py) | DEMO-VOTE: constructed example `[0, 0, 100]` |
| [sql/](sql/) `C10-*.sql`, `delta-C10.sql` | C10 queries of the models and of the reference, delta query |
| [sql/](sql/) `C11-*.sql`, `delta-C11.sql` | Replayed historical case DEMO-SQL-C11 |
| [reports/td2.md](reports/td2.md) | Session report |

## Reproduce

From this folder, with the virtual environment at the repository root:

```powershell
..\.venv\Scripts\Activate.ps1
python atelier-vote.py                                            # 4 synthetic examples
python atelier-vote.py --traces ../td1/traces-td1.csv --case C10  # one real question (replace C10)
python sql/demo-vote.py                                           # DEMO-VOTE
python atelier-routage.py                                         # the 7 simulator scenarios
```

## Cross-checks

| What | Checked by | Written record |
|---|---|---|
| C10 delta = 439 570 cents | Baptiste Marseille, Python recomputation on the CSV files | [reports/td2.md](reports/td2.md), section 2.6 |
| Full review of the wrong consensus | _To complete (plan step 11)_ | _To complete_ |
| Table of the 20 decisions | _To complete_ | _To complete_ |
| Routing rule | _To complete_ | _To complete_ |

## Contributions

| Member | TD 2 contribution |
|---|---|
| Nazim Yacine | Step 2 plan; DEMO-VOTE (plan step 1); DEMO-SQL-C11 (plan step 9) |
| Baptiste Marseille | `vote_k_sur_n` in `td1/`; plan steps 2 to 8 (C10 case, quorums, queries, diagnosis, delta and its check) |
| Baudouin Parent | `vote_k_sur_n` in `td2/`; table of the 20 decisions, 2-of-3 vs 3-of-5, with commentary |
| Ismaël Wane | Repository reorganisation into `td1/`, `td2/`, `td3/`; `atelier-vote.py` path adaptation |
| Antonin Charron | Project architecture diagram |
| _To complete_ | Routing rule and simulator |

An AI coding assistant is used back and forth, with small successive prompts; its outputs are checked manually within the sub-group.

## Open points

- **`atelier-vote.py` currently fails in `td2/`**: it loads the local `td2/skeleton-multi-llm-en.py` first, and that copy looks for `sandbox_sqlite.py` next to itself, which only exists in `td1/` (`FileNotFoundError: sandbox`). To fix before the Q1 demonstration.
- **Two implementations of `vote_k_sur_n`**: one in `td1/skeleton-multi-llm-en.py` (Baptiste, used for the plan steps 3 and 4), one in `td2/skeleton-multi-llm-en.py` (Baudouin, used for the table). Both should be checked to give the same decisions, then one kept.
- `td2-step1-vote.md` cites a `compare-vote.py` script that is not in the repository: to commit, or remove the mention.
- Routing rule and simulator outputs to integrate.
