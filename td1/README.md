# TD 1 - Comparing five models on the same twenty questions

Sub-group **DIA2_2** (Majeure DIA, ESILV). Session 1, 21 October 2026.
Assignment: [enonce-td1-en.md](enonce-td1-en.md). Protocol: [consigne-etudiante-en.md](consigne-etudiante-en.md). Report: [reports/td1.md](reports/td1.md).

## Metadata

| Item | Value |
|---|---|
| Pack version | `Pack 2026-10-18-students-1` (data seed `20260925`) |
| Database SHA-256 (`data/boutique.sqlite`) | `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2` |
| Environment | Python 3.10+, standard `sqlite3`, `requests`; API keys in local environment variables `GROQ_API_KEY` and `OPENROUTER_API_KEY`, never in the repository |
| Models | 5 free models, exact identifiers and parameters in [modeles-autorises.json](modeles-autorises.json) |
| Prompt | Unchanged from the kit, verbatim in [prompts-en.md](prompts-en.md) |

## Result

| Batch | Model | Account | Correct | Final trace |
|---|---|---|---|---|
| A | `groq:openai/gpt-oss-120b` | Antonin Charron (Groq) | **20/20** | [traces-A.csv](traces-A.csv) |
| B | `groq:openai/gpt-oss-20b` | Baudouin Parent (Groq) | 19/20 | [traces-B.csv](traces-B.csv) |
| C | `openrouter:cohere/north-mini-code:free` | Akihito Raffin (OpenRouter) | 12/20 | [traces-C.csv](traces-C.csv) |
| D | `groq:qwen/qwen3.8-27b` | Adrian Bernard (Groq) | 16/20 | [traces-D.csv](traces-D.csv) |
| E | `openrouter:dots-studio/dots-3-note-preview:free` | Vivien Perrault (OpenRouter) | 13/20 | [traces-E.csv](traces-E.csv) |

All 20 failures involve an **age** condition; every period and product-list question without an age filter is correct for all five models. Details, causes and limits are in the [report](reports/td1.md).

## Members and contributions

| Member | TD 1 contribution |
|---|---|
| Antonin Charron | Operator A; references C01-C02; comparison and summary CSVs; `.gitignore` |
| Baudouin Parent | Operator B; references C17-C18; merged raw traces into `traces-td1.csv`; check of batch B |
| Akihito Raffin | Operator C; references C09-C10 |
| Adrian Bernard | Operator D (run and rerun); references C13-C14 and [sql/](sql/); batch C note alignment |
| Vivien Perrault | Operator E; references C05-C06; check of batch E |
| Baptiste Marseille | Verification of batch C; references C07-C08 |
| Chandra R S Sukumar | Verification of batch D; references C11-C12 |
| Ismaël Wane | Independent check of C15-C16 |
| Nesrine Aissa | References C19-C20 |
| Nazim Yacine | References C03-C04; reference fixes; verification notes; verbatim prompt; report |

An AI coding assistant was used in back-and-forth, step-by-step prompts; its outputs were checked manually within the sub-group (see the report, section 9).

## Artefacts

| File | Content |
|---|---|
| [reference-td1.csv](reference-td1.csv) | 20 reference queries and values, executed on the database; `checked_by` names the member who cross-checked each one |
| [traces-td1.csv](traces-td1.csv), [traces-td1.jsonl](traces-td1.jsonl) | 102 real calls (100 first attempts, 2 retries after HTTP 429), all five batches merged |
| `traces-X.csv`, `state-X.jsonl` (X = A to E) | Raw traces of each batch, kept as produced |
| [traces-D-run1.csv](traces-D-run1.csv), [state-D-run1.jsonl](state-D-run1.jsonl) | First run of batch D (5 HTTP 429, C18 not executed), kept as a separate experiment, not counted |
| [model-question-comparison-en.csv](model-question-comparison-en.csv) | 100 rows: final result per model and question, explanation, pointer to the trace |
| [five-model-summary-en.csv](five-model-summary-en.csv) | Index, prices, access and results by family for the five models |
| [prompts-en.md](prompts-en.md) | System message and user template, verbatim |
| [verif/](verif/) | One verification note and comparison file per batch |
| [reports/td1.md](reports/td1.md) | Session report |

## Cross-checks

| What | Checked by | Record |
|---|---|---|
| References C01-C20 | A second member per question | `checked_by` column of [reference-td1.csv](reference-td1.csv) |
| Batch A | Nazim Yacine | [verif/verification-A.md](verif/verification-A.md) |
| Batch B | Baudouin Parent (self-check) | [verif/verification-B.md](verif/verification-B.md) |
| Batch C | Baptiste Marseille | [verif/verification-C.md](verif/verification-C.md) |
| Batch D | Chandra R S Sukumar | [verif/verification-D.md](verif/verification-D.md) |
| Batch E | Vivien Perrault (self-check) | [verif/verification-E.md](verif/verification-E.md) |

Each verification note records the checks run (record count, attempts, nature, references, prompt fingerprints, offline replay) and the cause of each failure, checked on the database.

## Reproduce

From this folder, with the virtual environment at the repository root (`..\.venv`):

```powershell
..\.venv\Scripts\Activate.ps1
python verify-data.py                                  # hashes of the database and CSV files
python check_access.py --no-network                    # Python and database checks, no API call
python sandbox_sqlite.py --db data/boutique.sqlite     # 25 sandbox self-tests
python skeleton-multi-llm-en.py --rates                # rates per model from traces-td1.jsonl
python skeleton-multi-llm-en.py --replay traces-td1.csv --state replay.jsonl --out replay.csv
```

The replay re-executes the stored SQL offline and gives the same verdicts as the real runs; its output (`nature = replay`) must not be committed. A new network batch (`--run`) needs a separate allocation agreed with the instructor.

## Open points

- Batches B and E were checked by their own operators: an independent review by another member is still to do.
- `prompts/prompt-td1.md` duplicates `prompts-en.md` (identical content); one copy should be removed.
- TD 2 uses these traces: see [../td2/](../td2/).
