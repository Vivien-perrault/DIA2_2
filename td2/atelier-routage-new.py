#!/usr/bin/env python3
"""TD 2: the sub-group's routing rule, exercised on the simulator.

Adapted from atelier-routage.py (kept unchanged for the "before" outputs).
Real models of the TD 1 batch, real prices of the portfolio, no API call, no key.
Eligibility is recomputed from the TD 1 traces: a model is eligible for a family
only if its last attempt is correct on every question of that family.
Availability and reset times are supplied by each scenario, not measured.
"""
import argparse
import csv
import json
from pathlib import Path

TRACES = Path(__file__).resolve().parent.parent / "td1" / "traces-td1.csv"

# Families: "type" field of td1/questions-td1.json (same as compute_accuracy.py)
FAMILIES = {
    "F1_period": ["C01", "C04", "C05", "C06", "C07", "C20"],
    "F2_age_fixed_date": ["C02", "C08", "C09", "C11"],
    "F2b_age_at_order": ["C10"],
    "F3_product_list": ["C03", "C12", "C13", "C14"],
    "F4_combined": ["C15", "C16", "C17", "C18", "C19"],
}

# Free routes of the TD 1 batch; a per-minute limit resets after 1 minute.
# Paid route: gpt-oss-120b on OpenRouter, portfolio 2026-09-28, 0.15 / 0.60 USD
# per million input / output tokens.
TOKENS_IN, TOKENS_OUT = 640, 266        # mean per call in TD 1 (gpt-oss-20b, HTTP 200)
RESOURCES = [
    {"id": "openrouter:cohere/north-mini-code:free", "provider": "openrouter", "cash": 0.0, "available": True, "reset_minutes": 1},
    {"id": "openrouter:dots-studio/dots-3-note-preview:free", "provider": "openrouter", "cash": 0.0, "available": True, "reset_minutes": 1},
    {"id": "groq:qwen/qwen3.8-27b", "provider": "groq", "cash": 0.0, "available": True, "reset_minutes": 1},
    {"id": "groq:openai/gpt-oss-120b", "provider": "groq", "cash": 0.0, "available": True, "reset_minutes": 1},
    {"id": "groq:openai/gpt-oss-20b", "provider": "groq", "cash": 0.0, "available": True, "reset_minutes": 1},
    {"id": "openrouter:openai/gpt-oss-120b", "provider": "openrouter",
     "cash": round((TOKENS_IN * 0.15 + TOKENS_OUT * 0.60) / 1e6, 6), "available": True, "reset_minutes": None,
     "measured_as": "groq:openai/gpt-oss-120b"},
]

# The rule (td2/reports/td2.md, section 3): first model, then fallbacks, free routes
# before the paid route. Tie-break: keep the gpt-oss models for the families only
# they pass, and prefer a provider other than Groq where several models are at 100 %.
ORDER = {
    "F1_period": ["openrouter:cohere/north-mini-code:free", "openrouter:dots-studio/dots-3-note-preview:free",
                  "groq:qwen/qwen3.8-27b", "groq:openai/gpt-oss-120b", "groq:openai/gpt-oss-20b"],
    "F3_product_list": ["openrouter:cohere/north-mini-code:free", "openrouter:dots-studio/dots-3-note-preview:free",
                        "groq:qwen/qwen3.8-27b", "groq:openai/gpt-oss-120b", "groq:openai/gpt-oss-20b"],
    "F2_age_fixed_date": ["groq:qwen/qwen3.8-27b", "groq:openai/gpt-oss-120b"],
    "F2b_age_at_order": ["groq:openai/gpt-oss-120b", "groq:openai/gpt-oss-20b"],
    "F4_combined": ["groq:openai/gpt-oss-120b", "groq:openai/gpt-oss-20b"],
}

# Check before delivery, by use (policy P5); age families need a deterministic check.
CHECKS = {
    "dashboard": {"default": "format check only (model 100 % on the family in TD 1)",
                  "F2b_age_at_order": "deterministic age check (family of one question)"},
    "customer": {"default": "2-of-3 quorum (fixed panel)",
                 "age": "reference query or deterministic age check (quorums failed on C02, C10)"},
    "payout": {"default": "reference query",
               "age": "reference query and review by a second person"},
}


def td1_results(traces=TRACES):
    """Last attempt per (route, question) -> correct or not, from the TD 1 traces."""
    last = {}
    with open(traces, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            key = (f"{row['provider']}:{row['model_requested']}", row["case_id"])
            if key not in last or int(row["attempts"]) >= int(last[key]["attempts"]):
                last[key] = row
    return {key: row["verdict"] == "correct" for key, row in last.items()}


RESULTS = td1_results()


def evidence(route, family):
    """(eligible, cells) for a route on a family; a paid route inherits the measure of its free twin."""
    measured = next((r.get("measured_as", r["id"]) for r in RESOURCES if r["id"] == route), route)
    cases = FAMILIES[family]
    right = [c for c in cases if RESULTS.get((measured, c))]
    return len(right) == len(cases), f"{len(right)}/{len(cases)} on {', '.join(cases)}"


def checks_for(request):
    use, family = request["use"], request["family"]
    table = CHECKS[use]
    if family in table:
        return table[family]
    if family.startswith("F2") or family == "F4_combined":
        return table.get("age", table["default"])
    return table["default"]


def choose(request, resources):
    """Deterministic routing: refuse what was not measured, then follow the rule's order."""
    family = request.get("family")
    if family not in FAMILIES:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": None,
                "reason": f"family {family!r} not measured in TD 1: not eligible (policy P9)"}
    if request.get("use") not in CHECKS:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": None,
                "reason": f"use {request.get('use')!r} unknown: no check can be chosen"}
    checks = checks_for(request)
    state = {r["id"]: r for r in resources}
    free = [state[i] for i in ORDER[family] if i in state and evidence(i, family)[0]]

    # 1. First eligible free route available, in the rule's order
    for r in free:
        if r["available"]:
            rank = "first model" if r["id"] == ORDER[family][0] else "fallback"
            return {"action": "run", "resource": r["id"], "cash": 0, "checks": checks,
                    "reason": f"{rank} for {family}, TD 1 {evidence(r['id'], family)[1]}"}
    # 2. Defer when the request can wait and a free route resets before the deadline
    waiting = [r for r in free if r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        r = min(waiting, key=lambda r: r["reset_minutes"])
        return {"action": "defer", "resource": r["id"], "cash": 0, "checks": checks,
                "wake_in_minutes": r["reset_minutes"],
                "reason": f"free routes for {family} exhausted; recheck {r['id']} at wake-up (a reset time is not a guarantee)"}
    # 3. Paid route within budget, if its model is eligible on the family
    paid = [r for r in resources if r["cash"] > 0 and r["available"] and r["cash"] <= request["budget"]
            and evidence(r["id"], family)[0]]
    if paid:
        r = min(paid, key=lambda r: r["cash"])
        return {"action": "run", "resource": r["id"], "cash": r["cash"], "checks": checks,
                "reason": f"no free route in time; paid route within budget, TD 1 {evidence(r['id'], family)[1]}"}
    # 4. Abstain: never fall back to a model that failed the family (policy P8)
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no eligible route for {family} within deadline and budget"}


def down(ids, reset=1):
    """Copy of RESOURCES with the given routes unavailable."""
    return [dict(r, available=False, reset_minutes=reset if r["cash"] == 0 else None) if r["id"] in ids else dict(r)
            for r in RESOURCES]


GROQ = [r["id"] for r in RESOURCES if r["provider"] == "groq"]
FREE = [r["id"] for r in RESOURCES if r["cash"] == 0]


def scenarios():
    base = {"use": "dashboard", "can_wait": True, "deadline_minutes": 120, "budget": 0.30}
    return [
        # The 7 scenarios of atelier-routage.py, mapped to a question family
        ("simple", {**base, "family": "F1_period"}, RESOURCES),
        ("complex", {**base, "family": "F4_combined"}, RESOURCES),
        ("deferrable", {**base, "family": "F4_combined"}, down(GROQ)),
        ("urgent", {**base, "family": "F4_combined", "can_wait": False, "deadline_minutes": 5}, down(GROQ, reset=10)),
        ("budget exhausted", {**base, "family": "F4_combined", "can_wait": False, "budget": 0}, down(GROQ, reset=10)),
        ("high impact", {**base, "family": "F4_combined", "use": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "F5_customer_segments"}, RESOURCES),
        # One scenario per family, then the first model unavailable
        ("F1 period, dashboard", {**base, "family": "F1_period"}, RESOURCES),
        ("F1 period, first model unavailable", {**base, "family": "F1_period"}, down(["openrouter:cohere/north-mini-code:free"])),
        ("F2 age at a date, customer", {**base, "family": "F2_age_fixed_date", "use": "customer"}, RESOURCES),
        ("F2 age at a date, first model unavailable", {**base, "family": "F2_age_fixed_date"}, down(["groq:qwen/qwen3.8-27b"])),
        ("F2b age at the order (C10), customer", {**base, "family": "F2b_age_at_order", "use": "customer"}, RESOURCES),
        ("F2b age at the order, first model unavailable", {**base, "family": "F2b_age_at_order"}, down(["groq:openai/gpt-oss-120b"])),
        ("F3 product list, payout", {**base, "family": "F3_product_list", "use": "payout"}, RESOURCES),
        ("F4 combinations, Groq down, cannot wait", {**base, "family": "F4_combined", "can_wait": False, "deadline_minutes": 5}, down(GROQ, reset=10)),
        ("all free routes down, cannot wait, no budget", {**base, "family": "F1_period", "can_wait": False, "budget": 0}, down(FREE, reset=10)),
        ("missing family", {k: v for k, v in base.items()}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}, ensure_ascii=False))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
