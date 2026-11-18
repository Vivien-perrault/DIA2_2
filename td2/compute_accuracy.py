import csv
import os
from collections import defaultdict

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

TRACES_FILE = os.path.join(PARENT_DIR, "td1", "traces-td1.csv")
if not os.path.exists(TRACES_FILE):
    TRACES_FILE = os.path.join(CURRENT_DIR, "traces-td1.csv")

# Familles selon le champ "type" de td1/questions-td1.json (mêmes familles que five-model-summary-en.csv)
QUESTION_FAMILIES = {
    "C01": "F1_period", "C04": "F1_period", "C05": "F1_period", "C06": "F1_period", "C07": "F1_period", "C20": "F1_period",
    "C02": "F2_age_fixed_date", "C08": "F2_age_fixed_date", "C09": "F2_age_fixed_date", "C11": "F2_age_fixed_date",
    "C10": "F2b_age_at_order",
    "C03": "F3_product_list", "C12": "F3_product_list", "C13": "F3_product_list", "C14": "F3_product_list",
    "C15": "F4_combined", "C16": "F4_combined", "C17": "F4_combined", "C18": "F4_combined", "C19": "F4_combined",
}

def compute_accuracy(traces_file):
    stats = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "total": 0, "cases": []}))

    # Seule la dernière tentative de chaque (modèle, question) compte, comme dans le TD 1
    last = {}
    with open(traces_file, mode="r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            key = (row.get("model_requested", "unknown").strip(), row.get("case_id", "").strip())
            if key not in last or int(row.get("attempts") or 1) >= int(last[key].get("attempts") or 1):
                last[key] = row

    for (model, case_id), row in last.items():
        verdict = row.get("verdict", "").strip()

        raw_val = row.get("value", "").strip()
        raw_ref = row.get("reference", "").strip()

        try:
            val = float(raw_val) if raw_val else None
            ref = float(raw_ref) if raw_ref else None
        except ValueError:
            val, ref = None, None

        family = QUESTION_FAMILIES.get(case_id, "Unknown")

        stats[model][family]["total"] += 1
        stats[model][family]["cases"].append(case_id)

        # Une réponse est correcte si le verdict est 'correct' ou si les valeurs correspondent
        if verdict == "correct" or (val is not None and ref is not None and val == ref):
            stats[model][family]["correct"] += 1

    return stats

def print_markdown_report(stats):
    print("\n## TD 1 Accuracy Rate per Question Family\n")
    for model, families in sorted(stats.items()):
        print(f"### Modèle : `{model}`")
        print("| Famille | Correct / Total | Accuracy (%) | Cases testés |")
        print("| :--- | :---: | :---: | :--- |")
        
        for family, data in sorted(families.items()):
            correct = data["correct"]
            total = data["total"]
            accuracy = (correct / total * 100) if total > 0 else 0.0
            cases_str = ", ".join(sorted(set(data["cases"])))
            
            print(f"| **{family}** | {correct} / {total} | {accuracy:.1f} % | {cases_str} |")
        print("\n" + "-"*60 + "\n")

if __name__ == "__main__":
    stats = compute_accuracy(TRACES_FILE)
    print_markdown_report(stats)