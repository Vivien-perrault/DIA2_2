#!/usr/bin/env python3
"""TD 2 step 1: the 20 vote decisions, fixed 2-of-3 panel and exploratory 3-of-5 panel.

Reads the last attempt of each model per question in ../td1/traces-td1.csv, runs
vote_k_sur_n of the local skeleton, compares with ../td1/reference-td1.csv only
after the decision, prints the Markdown table of td2-step1-vote.md and writes the
raw 3-of-5 decisions to votes-3of5.jsonl (the 2-of-3 ones come from atelier-vote.py).
No network call.

    python compare-vote.py
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
TD1 = HERE.parent / "td1"

COLUMNS = [("groq", "openai/gpt-oss-120b"), ("groq", "openai/gpt-oss-20b"), ("groq", "qwen/qwen3.8-27b"),
           ("openrouter", "cohere/north-mini-code:free"), ("openrouter", "dots-studio/dots-3-note-preview:free")]
PANEL_2OF3 = [("groq", "openai/gpt-oss-120b"), ("openrouter", "cohere/north-mini-code:free"), ("groq", "qwen/qwen3.8-27b")]
PANEL_3OF5 = COLUMNS        # exploratory: gpt-oss-120b and gpt-oss-20b are the same family


def load_vote():
    spec = importlib.util.spec_from_file_location("student_skeleton", HERE / "skeleton-multi-llm-en.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)


def last_attempts():
    last = {}
    with open(TD1 / "traces-td1.csv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["nature"] != "real":
                continue
            key = (row["provider"], row["model_requested"], row["case_id"])
            if key not in last or int(row["attempts"]) >= int(last[key]["attempts"]):
                last[key] = row
    return last


def proposal(row, provider, model):
    valid = row is not None and row["verdict"] in {"correct", "incorrect"} and row["value"] != ""
    return SimpleNamespace(provider=provider, model_requested=model,
                           value=int(row["value"]) if valid else None,
                           verdict="executed" if valid else "error")


def show(decision):
    if decision["consensus"]:
        return f"{decision['value']} ({decision['votes']} votes)"
    return f"abstain (max {decision['votes']})"


def judge(decision, reference):
    if not decision["consensus"]:
        return "abstain"
    return "OK" if decision["value"] == reference else "WRONG"


def main():
    vote = load_vote()
    last = last_attempts()
    with open(TD1 / "reference-td1.csv", encoding="utf-8", newline="") as f:
        references = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(f)}

    print("| case | reference | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | north-mini-code | dots-3-note-preview "
          "| 2-of-3 | 2/3 vs ref | 3-of-5 | 3/5 vs ref | decision changes? |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    raw = []
    for case in sorted(references):
        values = []
        for provider, model in COLUMNS:
            p = proposal(last.get((provider, model, case)), provider, model)
            values.append(str(p.value) if p.verdict == "executed" else "err")
        d3 = vote([proposal(last.get((p, m, case)), p, m) for p, m in PANEL_2OF3], 2)
        d5 = vote([proposal(last.get((p, m, case)), p, m) for p, m in PANEL_3OF5], 3)
        ref = references[case]
        changes = "**yes**" if (d3["consensus"], d3["value"]) != (d5["consensus"], d5["value"]) else ""
        print(f"| {case} | {ref} | " + " | ".join(values)
              + f" | {show(d3)} | {judge(d3, ref)} | {show(d5)} | {judge(d5, ref)} | {changes} |")
        raw.append({"case": case, "nature": "real", "n": len(PANEL_3OF5), "k": 3, "decision": d5,
                    "reference": ref, "matches_reference": (d5["value"] == ref) if d5["consensus"] else None})

    with open(HERE / "votes-3of5.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for record in raw:
            f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
