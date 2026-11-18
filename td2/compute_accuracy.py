import csv
import os
from collections import defaultdict

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

TRACES_FILE = os.path.join(PARENT_DIR, "td1", "traces-td1.csv")
if not os.path.exists(TRACES_FILE):
    TRACES_FILE = os.path.join(CURRENT_DIR, "traces-td1.csv")

QUESTION_FAMILIES = {
    "C01": "F1_period", "C05": "F1_period", "C09": "F1_period", "C12": "F1_period",
    "C02": "F2_age_fixed_date", "C06": "F2_age_fixed_date", "C11": "F2_age_fixed_date", "C15": "F2_age_fixed_date",
    "C03": "F2b_age_at_order", "C07": "F2b_age_at_order", "C10": "F2b_age_at_order", "C14": "F2b_age_at_order",
    "C04": "F3_product_list", "C08": "F3_product_list", "C13": "F3_product_list", "C16": "F3_product_list",
    "C17": "F4_combined", "C18": "F4_combined", "C19": "F4_combined", "C20": "F4_combined",
}

def compute_accuracy(traces_file):
    stats = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "total": 0, "cases": []}))

    with open(traces_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row.get("model_requested", "unknown").strip()
            case_id = row.get("case_id", "").strip()
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