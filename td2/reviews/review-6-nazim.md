# Review 6 – Simulator adaptation (second reviewer)

- Reviewer: Nazim Yacine (second reviewer; first reviewer: Adrian Bernard)
- Reviewed state: commit `175f4b4` (pre code review)
- Files: `td2/atelier-routage-new.py` (adapted), `td2/atelier-routage.py` (original)
- Author: Vivien Perrault

## How it was checked

The first reviewer checked `RESOURCES` against the TD 1 results and the choices against the rule. This review looks at the code's behaviour on its inputs and at what changed from the original workshop:

1. The original `choose` and its 7 scenarios were read and run, then compared with the adapted version.
2. `choose` was called with inputs that the 6 scenarios never use: no `family` field, a family name used elsewhere in the repository (`F4_combined`), a misspelled family, a difficulty above every level, and a temporarily exhausted free model.
3. The deferral path was traced: which resources can ever produce `defer`.
4. The command line was run with an unknown scenario name.

AI assistance was used to call `choose` on these inputs; the results were read and checked by the reviewer.

## Findings

| # | Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | important | `atelier-routage-new.py:70` | A request without a `family` field is silently treated as a period question (`request.get("family", "F1_period")`). A request built for the original workshop, or with a forgotten field, is routed to the cheapest period model instead of being refused. | `choose({difficulty: 2, …})` without `family` returns `run cohere/north-mini-code:free`, reason "for family [F1_period]". | |
| 2 | important | `atelier-routage-new.py:74` | An unknown family is never detected: `or r["level"] == 3` makes every level-3 resource eligible for any family name, and the reason states "eligible … for family [X]" as if X had been measured. Policy P9 says "not measured = not eligible". | `family = "F4_combined"` (the name used by `compute_accuracy.py`) and the misspelled `"F2_age"` both return `run senior-subscription (openai/gpt-oss-120b)`. | |
| 3 | important | `atelier-routage-new.py:13-62, 118` | `defer` can only happen for gpt-oss-120b, and only because the scenario switches off every resource whose `access` contains the string "subscription". No resource has a `reset_minutes`, so an exhausted free model is never deferred: the simulator moves to the next model at once. The policies set the wake-up after an HTTP 429 at 1 minute (Groq limits are per minute). | Qwen marked unavailable with `reset_minutes = 30`: `choose` returns `run cohere/north-mini-code:free`; `[r for r in RESOURCES if r["reset_minutes"]]` is empty. | |
| 4 | minor | `atelier-routage-new.py:121-128` | Two of the original scenarios disappeared: `high impact` (a high-stakes question that is not a combination) and `unknown capability` (difficulty above every level, expected `abstain`). The before/after comparison of deliverable 5 can no longer be done scenario by scenario. | Original: 7 scenarios; adapted: 6, with 4 on combinations. `choose` still abstains on difficulty 4 when called directly. | |
| 5 | minor | `atelier-routage-new.py:15, 26, 37, 48, 59, 81, 100` | `allocation` mixes units (50, 20, 100 calls or quota, and 0.30 for `senior-api`) without a comment, yet it is the first key of the selection. Its meaning cannot be checked against the TD 1 accounts. | – | |
| 6 | blocking | `atelier-routage-new.py:39` | Age at the order is routed to Cohere, wrong on C10. Same finding as the first reviewer (review 6, finding 1), confirmed. | `choose({family: "F2b_age_at_order"})` returns `cohere/north-mini-code:free`. | |

## What works

- The original `atelier-routage.py` is untouched: its 7 "before" outputs can be regenerated (`simple` → small-free, `deferrable` → defer, `budget exhausted` and `unknown capability` → abstain, …).
- The output format is kept: one JSON line per scenario, `nature = simulation`, and every decision carries a `reason`.
- The command line rejects an unknown scenario (`error: unknown scenario`).
- The decision order of the workshop (included capacity, defer, paid route within budget, abstain) is preserved, and difficulty 4 still ends in `abstain`.

## Summary

Beyond the TD 1 figures (first review), the code must refuse what it does not know: no default family, no level-3 bypass for unmeasured families, and a real reset time per free model so that `defer` follows the policy. Keep the original 7 scenarios alongside one scenario per family, so that the outputs before and after can be compared line by line.
