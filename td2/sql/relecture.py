#!/usr/bin/env python3
"""TD2 étape 2.11 : relecture croisée. Relance chaque requête et chaque vote cités
dans td2/reports/td2.md (sections 2.0 à 2.7) et compare au chiffre écrit dans le rapport.

    python td2/sql/relecture.py          # depuis la racine du dépôt

La base est ouverte en lecture seule. Le vote utilise `vote_k_sur_n` du squelette TD1
(td1/skeleton-multi-llm-en.py), comme le prévoit atelier-vote.py.
"""
import csv
import importlib.util
import sqlite3
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "td1" / "data" / "boutique.sqlite"
SQL = ROOT / "td2" / "sql"
FAILS = []


def check(label, got, expected):
    ok = got == expected
    if not ok:
        FAILS.append(label)
    print(f"[{'OK' if ok else 'ÉCART'}] {label} : obtenu {got!r}, rapport {expected!r}")


def load_vote():
    sys.path.insert(0, str(ROOT / "td1"))
    path = ROOT / "td1" / "skeleton-multi-llm-en.py"
    spec = importlib.util.spec_from_file_location("skeleton_td1", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda props, k: module.Orchestrateur.vote_k_sur_n(None, props, k)


def proposals(last, case, members):
    out = []
    for provider, model in members:
        row = last.get((provider, model, case), {})
        valid = row.get("verdict") in {"correct", "incorrect"} and row.get("value", "") != ""
        out.append(SimpleNamespace(provider=provider, model_requested=model,
                                   value=int(row["value"]) if valid else None,
                                   verdict="executed" if valid else "error"))
    return out


def main():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    scalar = lambda q: con.execute(q).fetchone()[0]

    # 2.0 DEMO-VOTE (exemple construit, table jouet en mémoire)
    toy = sqlite3.connect(":memory:")
    toy.execute("CREATE TABLE sales (sale_date TEXT, amount_cents INTEGER)")
    toy.execute("INSERT INTO sales VALUES ('2026-01-01', 100)")
    q = "SELECT COALESCE(SUM(amount_cents), 0) FROM sales WHERE sale_date {} '2026-01-01' AND sale_date < '2026-01-02'"
    gt, ge = toy.execute(q.format(">")).fetchone()[0], toy.execute(q.format(">=")).fetchone()[0]
    check("2.0 DEMO-VOTE variante >", gt, 0)
    check("2.0 DEMO-VOTE variante >=", ge, 100)
    vote = load_vote()
    demo = [SimpleNamespace(provider=f"p{i}", model_requested="m", value=v, verdict="executed")
            for i, v in enumerate([gt, gt, ge])]
    r = vote(demo, 2)
    check("2.0 DEMO-VOTE vote 2 sur 3", (r["consensus"], r["value"], r["votes"]), (True, 0, 2))

    # 2.1 Traces : dernière tentative par (provider, modèle, question)
    with (ROOT / "td1" / "traces-td1.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    last = {}
    for row in rows:
        last[(row["provider"], row["model_requested"], row["case_id"])] = row
    check("2.1 lignes de traces", len(rows), 102)
    check("2.1 dernières tentatives", len(last), 100)
    check("2.1 natures", {r["nature"] for r in rows}, {"real"})
    shared = {}
    for (p, m, c), row in last.items():
        if row["verdict"] == "incorrect" and row["value"] != "":
            shared.setdefault((c, int(row["value"])), []).append(m)
    shared = {k: len(v) for k, v in shared.items() if len(v) >= 2}
    check("2.1 valeurs fausses partagées", shared, {("C02", 0): 3, ("C08", 0): 2, ("C10", 119410): 2})
    c10 = {m: (last[(p, m, "C10")]["value"], last[(p, m, "C10")]["verdict"]) for (p, m, c) in last if c == "C10"}
    check("2.1 valeurs C10", c10, {
        "openai/gpt-oss-120b": ("558980", "correct"), "openai/gpt-oss-20b": ("558980", "correct"),
        "cohere/north-mini-code:free": ("119410", "incorrect"), "qwen/qwen3.8-27b": ("119410", "incorrect"),
        "dots-studio/dots-3-note-preview:free": ("", "sql_invalid")})
    cited = {"groq:openai/gpt-oss-120b:C10", "groq:openai/gpt-oss-20b:C10", "openrouter:cohere/north-mini-code:free:C10",
             "groq:qwen/qwen3.8-27b:C10", "openrouter:dots-studio/dots-3-note-preview:free:C10",
             "openrouter:cohere/north-mini-code:free:C11"}
    check("2.1/2.7 cell_id cités présents", cited <= {r["cell_id"] for r in rows}, True)
    with (ROOT / "td1" / "reference-td1.csv").open(encoding="utf-8", newline="") as f:
        ref = {r["case_id"]: r for r in csv.DictReader(f)}
    check("2.1 référence C10", (int(ref["C10"]["revenue_cents"]), ref["C10"]["checked_by"]), (558980, "Akihito Raffin"))

    # 2.2 et 2.3 Quorums
    panel3 = [("groq", "openai/gpt-oss-120b"), ("openrouter", "cohere/north-mini-code:free"), ("groq", "qwen/qwen3.8-27b")]
    panel5 = panel3 + [("groq", "openai/gpt-oss-20b"), ("openrouter", "dots-studio/dots-3-note-preview:free")]
    for case, k, panel, expected in [("C10", 2, panel3, (True, 119410, 2)), ("C02", 2, panel3, (True, 590320, 2)),
                                     ("C10", 3, panel5, (False, None, 2)), ("C02", 3, panel5, (True, 0, 3))]:
        r = vote(proposals(last, case, panel), k)
        check(f"2.2/2.3 {case} vote {k} sur {len(panel)}", (r["consensus"], r["value"], r["votes"]), expected)
    check("2.3 référence C02", int(ref["C02"]["revenue_cents"]), 590320)

    # 2.2 Commande atelier-vote.py citée telle quelle (vote de l'étape 1, copie td2 du squelette)
    import json, subprocess
    for case, expected in [("C10", (True, 119410, 2)), ("C02", (True, 590320, 2))]:
        out = subprocess.run([sys.executable, str(ROOT / "td2" / "atelier-vote.py"), "--traces",
                              str(ROOT / "td1" / "traces-td1.csv"), "--case", case],
                             capture_output=True, text=True, cwd=ROOT)
        d = json.loads(out.stdout)["decision"] if out.returncode == 0 else {}
        check(f"2.2 atelier-vote.py {case}", (d.get("consensus"), d.get("value"), d.get("votes")), expected)

    # 2.4 Requêtes C10
    for name, expected in [("C10-cohere.sql", 119410), ("C10-qwen.sql", 119410), ("C10-reference.sql", 558980)]:
        check(f"2.4 {name}", scalar((SQL / name).read_text(encoding="utf-8")), expected)
    check("2.4 référence CSV réexécutée", scalar(ref["C10"]["sql"]), 558980)

    # 2.5 Branches de Qwen exécutées séparément
    base = ("SELECT COUNT(*), COALESCE(SUM(o.quantity_product * p.price), 0) FROM orders o "
            "JOIN customers c ON o.customer_id = c.customer_id JOIN product p ON o.product_id = p.product_id WHERE ")
    md = "(strftime('%m', {0}) || strftime('%d', {0}))"
    gap = "(strftime('%Y', o.date) - strftime('%Y', c.birth_date))"
    b1 = f"{gap} = 25 AND {md.format('o.date')} >= {md.format('c.birth_date')}"
    b2 = f"{gap} = 24 AND {md.format('o.date')} < {md.format('c.birth_date')}"
    check("2.5 Qwen branche 1 (lignes, centimes)", con.execute(base + b1).fetchone(), (14, 119410))
    check("2.5 Qwen branche 2 (lignes, centimes)", con.execute(base + b2).fetchone(), (0, 0))

    # 2.6 Delta C10
    delta = con.execute((SQL / "delta-C10.sql").read_text(encoding="utf-8")).fetchall()
    expected_rows = [("C004", 150260, 0, 150260), ("C005", 150240, 0, 150240),
                     ("C007", 118740, 0, 118740), ("C022", 20330, 0, 20330)]
    for model in ("Cohere", "Qwen"):
        got = [tuple(r[1:]) for r in delta if r[0] == model]
        check(f"2.6 delta C10 {model}", got, expected_rows)
        check(f"2.6 somme delta {model}", sum(r[3] for r in got), 558980 - 119410)

    # 2.6 Vérification indépendante en Python sur les CSV source (sans SQL)
    data = ROOT / "td1" / "data"
    read = lambda n: list(csv.DictReader((data / n).open(encoding="utf-8", newline="")))
    price = {r["product_id"]: int(r["price"]) for r in read("product.csv")}
    birth = {r["customer_id"]: date.fromisoformat(r["birth_date"][:10]) for r in read("customers.csv")}
    totals = {"ref": 0, "cohere": 0, "qwen": 0}
    per_client = {}
    for o in read("orders.csv"):
        d, b = date.fromisoformat(o["date"][:10]), birth[o["customer_id"]]
        cents = int(o["quantity_product"]) * price[o["product_id"]]
        reached = (d.month, d.day) >= (b.month, b.day)
        age = d.year - b.year - (0 if reached else 1)
        in_ref = age == 25
        in_coh = d.year - b.year == 25 and reached
        in_qwen = in_coh or (d.year - b.year == 24 and not reached)
        totals["ref"] += cents * in_ref
        totals["cohere"] += cents * in_coh
        totals["qwen"] += cents * in_qwen
        if in_ref and not in_coh:
            per_client[o["customer_id"]] = per_client.get(o["customer_id"], 0) + cents
    check("2.6 Python CSV totaux", totals, {"ref": 558980, "cohere": 119410, "qwen": 119410})
    check("2.6 Python CSV delta par client", per_client, {r[0]: r[3] for r in expected_rows})

    # 2.7 DEMO-SQL-C11 (cas historique rejoué)
    check("2.7 M1", scalar((SQL / "C11-M1-gpt-oss-20b.sql").read_text(encoding="utf-8")), 0)
    check("2.7 M2", scalar((SQL / "C11-M2-cohere.sql").read_text(encoding="utf-8")), 0)
    check("2.7 référence C11", (scalar(ref["C11"]["sql"]), int(ref["C11"]["revenue_cents"]), ref["C11"]["checked_by"]),
          (446690, 446690, "Chandra R S SUKUMAR"))
    d11 = con.execute((SQL / "delta-C11.sql").read_text(encoding="utf-8")).fetchall()
    check("2.7 delta C11", [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in d11], [
        ("C001", "2001-09-25", 18, 135000, 0, 0), ("C002", "2001-09-24", 6, 25920, 0, 0),
        ("C003", "2001-09-26", 6, 47900, 0, 0), ("C006", "2001-11-30", 10, 77450, 0, 0),
        ("C008", "2001-05-15", 11, 99090, 0, 0), ("C009", "2001-03-10", 9, 61330, 0, 0)])
    check("2.7 somme delta C11", (sum(r[2] for r in d11), sum(r[3] for r in d11)), (60, 446690))
    c11 = {m: last[(p, m, "C11")]["value"] for (p, m, c) in last if c == "C11"}
    check("2.7 lot TD1 sur C11", sorted(c11.values()), ["0", "446690", "446690", "446690", "446690"])
    check("2.7 Cohere C11", c11["cohere/north-mini-code:free"], "0")

    print(f"\n{'Tout est conforme' if not FAILS else f'{len(FAILS)} écart(s) : ' + ', '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
