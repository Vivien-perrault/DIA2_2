# Review 7 - Accuracy per family

- Reviewer: Baudouin Parent
- Files: `td2/compute_accuracy.py`
- AI assistance: Claude (Anthropic) was used to run the script on `td1/traces-td1.csv`, recompute the 25 rates independently, run two edge-case tests on a modified copy of the traces and draft this report. Each finding was checked by the reviewer.

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | minor | `compute_accuracy.py`:25–30 | The `nature` column is not filtered: a `replay` or `simulation` row of the same model and question replaces the `real` row (same `attempts`, later in the file) and enters the rate. The skeleton says natures are never mixed in a rate. No effect on the current traces (all `real`). | Copy of the traces + one `replay` row (gpt-oss-120b, C01, wrong value): F1 goes from 6/6 to 5/6. | Keep `nature == "real"` only, or add `--nature`. |
| 2 | minor | `compute_accuracy.py`:28 | The key is `(model_requested, case_id)`, without `provider`. The same model through two routes merges into one rate. The routing rule plans the paid route `gpt-oss-120b#openrouter`: once traced, its rows would overwrite the Groq rows. No effect on the current traces. | Copy of the traces + one `openrouter` row for gpt-oss-120b C02 (wrong): F2 goes from 4/4 to 3/4. | Key on `(provider, model_requested, case_id)`, as `cell_id` does. |
| 3 | minor | `compute_accuracy.py`:12–19 | The families are typed by hand, while the comment says they come from the `type` field of `td1/questions-td1.json`. A change in the JSON would not be seen. | Read the code; the mapping matches the families of section 3 of `reports/td2.md`. | Read `type` from `questions-td1.json`. |
| 4 | minor | `compute_accuracy.py`:8–10 | The traces path is fixed (`../td1/traces-td1.csv`, else the script's folder); no `--traces` argument. | Read the code. | Add `--traces`. |
| 5 | minor | `compute_accuracy.py`:50 | `verdict == "correct" or val == ref`: the second test never changes the result on our traces (the skeleton already sets `correct` on equality). Harmless, but it hides the source of truth. | All 100 latest cells: same count with the verdict alone. | accepted: harmless. |

**Checked and correct:**
- Runs (`python td2/compute_accuracy.py`) and finds `td1/traces-td1.csv` from `td2/`.
- Last attempt per cell: gpt-oss-20b C19 and C20 (429, then correct on attempt 2) are counted on attempt 2.
- The 25 rates (5 models × 5 families) match an independent recomputation from `td1/traces-td1.csv`:

| model | F1 (6) | F2 (4) | F2b (1) | F3 (4) | F4 (5) |
|---|---|---|---|---|---|
| gpt-oss-120b | 6/6 | 4/4 | 1/1 | 4/4 | 5/5 |
| gpt-oss-20b | 6/6 | 3/4 (✗ C02) | 1/1 | 4/4 | 5/5 |
| qwen3.8-27b | 6/6 | 4/4 | 0/1 | 4/4 | 2/5 (✓ C16, C18) |
| north-mini-code | 6/6 | 0/4 | 0/1 | 4/4 | 2/5 (✓ C16, C18) |
| dots-3-note-preview | 6/6 | 1/4 (✓ C11) | 0/1 | 4/4 | 2/5 (✓ C16, C19) |

- Rates are printed with their denominator (`correct / total`), never as a percentage alone.
- Invalid SQL (`sql_invalid`) and refused calls on the last attempt count as wrong, as in TD 1.

Summary: the script is correct on our traces and its figures can be used as the single source of rates for step 3 (they match section 3 of the report). Findings 1 and 2 have no effect today but would give wrong rates as soon as replayed traces or the paid route are added (TD 3): worth fixing before then. Findings 3–5 are robustness and readability.
