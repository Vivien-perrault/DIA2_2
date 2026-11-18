# TD 2 – Code review: assignment

This commit is the **pre code review** checkpoint: the reviewed state is the commit that adds this file. Nobody pushes changes to the reviewed files until the review reports are pushed.

## Rules

- A reviewer never reviews their own work (authors taken from the Git history).
- Each reviewer writes one report, `td2/reviews/review-<item>.md`, using the template below, and pushes it.
- Fixes come after the reports. Anyone may fix any point, but announces it to the group first, and the report records who fixed it and in which commit.
- When all points are fixed or accepted, the group pushes the **post code review** checkpoint commit.
- AI assistance used during the review is declared in the report.

## Assignment

| # | Item | Files | Author(s) | Reviewer | Second reviewer |
|---|---|---|---|---|---|
| 1 | `vote_k_sur_n` and the vote workshop | `td2/skeleton-multi-llm-en.py`, `td1/skeleton-multi-llm-en.py` (`vote_k_sur_n` only), `td2/atelier-vote.py` | Baudouin Parent, Baptiste Marseille, Nazim Yacine | Akihito Raffin | |
| 2 | Table of the 20 vote decisions | `td2/td2-step1-vote.md`, `votes-20-questions.jsonl` | Baudouin Parent, Antonin Charron | Ismaël Wane | Chandra R S Sukumar |
| 3 | Wrong consensus (C10, C02, DEMO-VOTE, DEMO-SQL-C11) | `td2/reports/td2.md` section 2, `td2/sql/` | Baptiste Marseille, Nazim Yacine, Akihito Raffin | Vivien Perrault | |
| 4 | Policies | `td2/td2-policies.md` | Baudouin Parent | Nesrine Aissa | |
| 5 | Routing rule | `td2/reports/td2.md` section 3 | Antonin Charron | Baptiste Marseille | Adrian Bernard |
| 6 | Simulator adaptation | `td2/atelier-routage-new.py`, simulator outputs before and after | Vivien Perrault | Adrian Bernard | Nazim Yacine |
| 7 | Accuracy per family | `td2/compute_accuracy.py` | Vivien Perrault, Chandra R S Sukumar | Baudouin Parent | |
| 8 | TD 2 README | `td2/README.md` | Chandra R S Sukumar | Antonin Charron | |

Items 5 and 6 carry Q3 and have a second reviewer. They must be reviewed together: the rule (item 5), the policies (item 4) and the simulator (item 6) must choose the same first model per family and cite the same TD 1 cells.

## What to check

- **Code (items 1, 6, 7)**: it runs from `td2/` with the commands of the README; it gives the expected result on the real traces; edge cases (abstention, unavailable member, duplicate pair, k not a strict majority; for the simulator, defer and abstain).
- **Figures (items 2, 3, 7)**: every number is recomputed from `td1/traces-td1.csv` or `td1/data/boutique.sqlite`, not copied.
- **Rule and policies (items 4, 5, 6)**: each line cites the TD 1 cells that justify it; the rule, the policies and the simulator say the same thing; what happens when the first model is unavailable.
- **Text (all)**: links work, files are in the right folder, claims match the evidence.

## Report template

```markdown
# Review <n> – <item>

- Reviewer: <name>
- Reviewed state: commit <hash> (pre code review)
- Files: <list>

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | blocking / important / minor | | | how it was checked | commit <hash> by <name>, or "accepted: <reason>" |

Summary: <what works, what must change>
```

Severity: **blocking** = a deliverable is wrong or does not run; **important** = a claim, a rule or a figure contradicts the evidence; **minor** = wording, location, link.
