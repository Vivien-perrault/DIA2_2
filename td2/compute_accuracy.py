import argparse
import csv
import json
import os
from collections import defaultdict

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

TRACES_FILE = os.path.join(PARENT_DIR, "td1", "traces-td1.csv")
QUESTIONS_FILE = os.path.join(PARENT_DIR, "td1", "questions-td1.json")

# Famille lue depuis le champ "type" de td1/questions-td1.json (mêmes familles que five-model-summary-en.csv)
TYPE_TO_FAMILY = {
    "period": "F1_period",
    "age on a reference date": "F2_age_fixed_date",
    "age at the time of the order": "F2b_age_at_order",
    "product list": "F3_product_list",
}


def load_families(questions_file):
    with open(questions_file, encoding="utf-8") as f:
        questions = json.load(f)["questions"]
    # Un type combiné ("period + age ...") va dans F4_combined
    return {q["id"]: TYPE_TO_FAMILY.get(q["type"], "F4_combined") for q in questions}


def compute_accuracy(traces_file, families):
    stats = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "total": 0, "cases": []}))

    # Seule la dernière tentative réelle de chaque (fournisseur, modèle, question) compte, comme dans le TD 1 :
    # une ligne replay ou simulation n'entre jamais dans un taux, et deux routes d'un même modèle restent séparées
    last = {}
    with open(traces_file, mode="r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("nature", "real") != "real":
                continue
            key = (f"{row['provider'].strip()}:{row['model_requested'].strip()}", row.get("case_id", "").strip())
            if key not in last or int(row.get("attempts") or 1) >= int(last[key].get("attempts") or 1):
                last[key] = row

    for (model, case_id), row in last.items():
        family = families.get(case_id, "Unknown")
        stats[model][family]["total"] += 1
        stats[model][family]["cases"].append(case_id)
        # Le verdict du squelette est la source de vérité (il vaut "correct" quand la valeur égale la référence)
        if row.get("verdict", "").strip() == "correct":
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
    parser = argparse.ArgumentParser(description="TD 1 accuracy per question family")
    parser.add_argument("--traces", default=TRACES_FILE, help="traces CSV, default: ../td1/traces-td1.csv")
    parser.add_argument("--questions", default=QUESTIONS_FILE, help="default: ../td1/questions-td1.json")
    args = parser.parse_args()
    print_markdown_report(compute_accuracy(args.traces, load_families(args.questions)))
