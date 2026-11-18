# Review 8 – TD 2 README

- Reviewer: Antonin Charron
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/README.md`
- Author: Chandra R S Sukumar

## How it was checked

1. Inspected `git show 175f4b4:td2/README.md` and verified it matches the working copy of `td2/README.md`.
2. Executed all four commands in `## Reproduce` from `td2/` with `..\.venv\Scripts\python.exe`: `atelier-vote.py`, `atelier-vote.py --traces ../td1/traces-td1.csv --case C10`, `sql/demo-vote.py`, and `atelier-routage.py`.
3. Checked the existence of all relative links in `td2/README.md` from `td2/` (`Test-Path`).
4. Cross-checked the Deliverables, Files, Cross-checks, Contributions, and Open points sections against `td2/reports/td2.md`, `td2/reviews/review-assignment.md`, and the files present in `td2/`.

AI assistance was used to run the checks and draft this review; every command output, path, and finding was verified by the reviewer.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `td2/README.md:94` | Open point 1 claims "`atelier-vote.py` currently fails in `td2/`" with `FileNotFoundError: sandbox`, which contradicts the actual state at `175f4b4`: running `atelier-vote.py` and `atelier-vote.py --traces ../td1/traces-td1.csv --case C10` from `td2/` succeeds (as documented in `td2/reports/td2.md:315`). | Executed both commands from `td2/`: exit code 0, expected JSON outputs printed. | |
| 2 | minor | `td2/README.md:22` | Broken relative link `[../PLAN-TD2-ETAPE2.md](../PLAN-TD2-ETAPE2.md)`: the file does not exist at the repository root. | `Test-Path "..\PLAN-TD2-ETAPE2.md"` returned `False`; `Get-ChildItem "..\" -Filter "PLAN-TD2*"` returned empty. | |
| 3 | important | `td2/README.md:22-24, 41-43, 74-77, 97` | Deliverables 3, 4, 5, the `Routing rule` section, `Cross-checks`, and `Open points` are still marked "In progress: plan steps 1 to 9 done, 10 to 12 left" or `_To complete_`, whereas Step 2 (including `sql/relecture.py` 36 checks) and Step 3 (`td2/reports/td2.md` § 3, `td2-policies.md`, `atelier-routage-new.py`, `compute_accuracy.py`) already exist at `175f4b4`. | `td2/reports/td2.md` has sections 2.0–2.10 and 3.1; `td2/` contains `td2-policies.md`, `atelier-routage-new.py`, `compute_accuracy.py`. | |
| 4 | minor | `td2/README.md:45-57` | The `## Files` table omits several TD 2 files present in `td2/` (`td2-policies.md`, `atelier-routage-new.py`, `compute_accuracy.py`, `sql/relecture.py`, `reviews/review-assignment.md`) and `votes-20-questions.jsonl`. | `Get-ChildItem td2` lists these files; none appear in `td2/README.md:47-57`. | |
| 5 | minor | `td2/README.md:79-89` | The `## Contributions` table is incomplete: it omits Akihito Raffin (Step 2 cross-review/synthesis), Vivien Perrault (`atelier-routage-new.py`, `compute_accuracy.py`), Adrian Bernard, Nesrine Aissa, Chandra R S Sukumar (`td2/README.md`, `compute_accuracy.py`), and leaves `_To complete_` for routing rule and simulator (Antonin Charron wrote § 3.1). | `td2/reports/td2.md:323` and `td2/reviews/review-assignment.md:15-25`. | |

## What works

- **All four commands in `## Reproduce` run cleanly from `td2/`**: `atelier-vote.py` (4 synthetic examples), `atelier-vote.py --traces ../td1/traces-td1.csv --case C10` (`119410`, 2 votes, `matches_reference: false`), `sql/demo-vote.py` (`0`, `100`, `consensus=True`), and `atelier-routage.py` (7 scenarios).
- **Vote summary figures match** `td2/td2-step1-vote.md` and `td2/reports/td2.md`: 16/20 correct, 1/20 wrong (C10 for 2-of-3, C02 for 3-of-5), 3/20 abstentions.
- **Input and core file links work**: `../td1/traces-td1.csv`, `../td1/reference-td1.csv`, `../td1/data/boutique.sqlite`, `../td1/prompts-en.md`, `enonce-td2-en.md`, `reports/td2.md`, `td2-step1-vote.md`, `skeleton-multi-llm-en.py`, `atelier-vote.py`, `atelier-routage.py`, and `sql/demo-vote.py` all resolve.
- Clear, concise structure (Inputs, Deliverables, Vote summary, Files, Reproduce, Cross-checks, Contributions, Open points) and explicit AI usage disclosure.

## Summary

The README is well-structured and all `## Reproduce` commands work as written from `td2/`. Because it was written as a session skeleton, it needs a post-review update to: (1) remove the stale `atelier-vote.py` failure in Open points, (2) remove or fix the broken `../PLAN-TD2-ETAPE2.md` link, (3) fill in Deliverables 3–5, `Routing rule`, `Cross-checks`, and `Contributions` with the completed Step 2/Step 3 work, and (4) add `td2-policies.md`, `atelier-routage-new.py`, `compute_accuracy.py`, `sql/relecture.py`, and `reviews/` to `## Files`.
