"""TD 2 and TD 3: Routing policy adapted with TD 1 portfolio models, 
question families (F1, F2, F2b, F3, combinations), and cell justifications.
"""
import argparse
import json

# Portefeuille complet des modèles du TD 1, leurs niveaux, prix et cellules justificatives
RESOURCES = [
    {
        "id": "qwen/qwen3.8-27b", 
        "level": 1, 
        "access": "free", 
        "available": True,
        "cash": 0.0, 
        "allocation": 50.0, 
        "reset_minutes": None, 
        "families": ["F1_period", "F3_product_list"],
        "td1_cells": "C01, C05, C09, C12, C04, C08, C13, C16 (100% accuracy)"
    },
    {
        "id": "openai/gpt-oss-20b", 
        "level": 2, 
        "access": "free", 
        "available": True,
        "cash": 0.0, 
        "allocation": 50.0, 
        "reset_minutes": None, 
        "families": ["F1_period", "F2b_age_at_order", "F3_product_list"],
        "td1_cells": "C01-C12 (100%), F4_combined (66.7%)"
    },
    {
        "id": "cohere/north-mini-code:free", 
        "level": 2, 
        "access": "tokens", 
        "available": True,
        "cash": 0.0, 
        "allocation": 20.0, 
        "reset_minutes": None, 
        "families": ["F1_period", "F2b_age_at_order", "F3_product_list"],
        "td1_cells": "C01-C16 (75% accuracy)"
    },
    {
        "id": "senior-subscription (openai/gpt-oss-120b)", 
        "level": 3, 
        "access": "subscription", 
        "available": True,
        "cash": 0.0, 
        "allocation": 100.0, 
        "reset_minutes": None, 
        "families": ["F1_period", "F2_age_fixed_date", "F2b_age_at_order", "F3_product_list", "F1_F2_F3_combination"],
        "td1_cells": "C01-C20 (100% accuracy including F1+F2+F3 combinations C17-C20)"
    },
    {
        "id": "senior-api", 
        "level": 3, 
        "access": "tokens", 
        "available": True,
        "cash": 0.30, 
        "allocation": 0.30, 
        "reset_minutes": None, 
        "families": ["F1_period", "F2_age_fixed_date", "F2b_age_at_order", "F3_product_list", "F1_F2_F3_combination"],
        "td1_cells": "External fallback API"
    },
]


def choose(request, resources):
    """Politique de routage déterministe basée sur les familles de questions et les ressources TD 1.
    """
    target_family = request.get("family", "F1_period")
    is_combination = target_family == "F1_F2_F3_combination"
    
    # Filtrage des ressources éligibles selon la difficulté / famille
    eligible = [r for r in resources if r["level"] >= request["difficulty"] and (target_family in r["families"] or r["level"] == 3)]
    
    checks = "source verification and human review" if request["high_impact"] or is_combination else "read-only execution and value check"
    
    # 1. Capacité incluse immédiatement disponible (priorité aux quotas gratuits / abonnements inclus)
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (r["allocation"], r["level"], r["id"]))
        reason_str = f"eligible included capacity for family [{target_family}] based on TD 1 cells [{chosen['td1_cells']}]"
        return {"action": "run", "resource": chosen["id"], "cash": 0,
                "checks": checks, "reason": reason_str}
                
    # 2. Attente / Report si ressource temporairement épuisée mais dans les délais
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        reason_str = f"recheck availability at wake-up for family [{target_family}] (TD 1 cells: [{chosen['td1_cells']}])"
        return {"action": "defer", "resource": chosen["id"], "cash": 0,
                "checks": checks, "reason": reason_str,
                "wake_in_minutes": chosen["reset_minutes"]}
                
    # 3. Utilisation payante (cash) si autorisée par le budget
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["allocation"], r["id"]))
        reason_str = f"available route within authorised budget for [{target_family}] (TD 1 cells: [{chosen['td1_cells']}])"
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"],
                "checks": checks, "reason": reason_str}
                
    # 4. Abstention si aucune ressource ne correspond
    return {"action": "abstain", "resource": None, "cash": 0,
            "checks": checks, "reason": f"no eligible resource for family [{target_family}] within deadline and budget"}


def scenarios():
    base_f1 = {"difficulty": 1, "high_impact": False, "can_wait": True,
               "deadline_minutes": 120, "budget": 0.30, "family": "F1_period"}
    base_f2 = {"difficulty": 2, "high_impact": False, "can_wait": True,
               "deadline_minutes": 120, "budget": 0.30, "family": "F2_age_fixed_date"}
    base_combo = {"difficulty": 3, "high_impact": True, "can_wait": True,
                  "deadline_minutes": 120, "budget": 0.30, "family": "F1_F2_F3_combination"}
                  
    exhausted_sub = [dict(r, available=False, reset_minutes=60) if "subscription" in r["access"] else dict(r)
                     for r in RESOURCES]
                     
    return [
        ("simple_F1_period", base_f1, RESOURCES),
        ("complex_F2_age", base_f2, RESOURCES),
        ("combination_F1_F2_F3", base_combo, RESOURCES),
        ("deferrable_combination", base_combo, exhausted_sub),
        ("urgent_combination", {**base_combo, "can_wait": False, "deadline_minutes": 5}, exhausted_sub),
        ("budget_exhausted", {**base_combo, "can_wait": False, "budget": 0}, exhausted_sub),
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
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()