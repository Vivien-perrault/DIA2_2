"""DEMO-VOTE : exemple jouet construit (pas une sortie de modèle, pas la base boutique)."""
import sqlite3
from collections import Counter

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE sales (sale_date TEXT, amount_cents INTEGER)")
db.execute("INSERT INTO sales VALUES ('2026-01-01', 100)")

STRICT = ("SELECT COALESCE(SUM(amount_cents), 0) FROM sales "
          "WHERE sale_date > '2026-01-01' AND sale_date < '2026-01-02'")
INCLUSIVE = ("SELECT COALESCE(SUM(amount_cents), 0) FROM sales "
             "WHERE sale_date >= '2026-01-01' AND sale_date < '2026-01-02'")

strict = db.execute(STRICT).fetchone()[0]
inclusive = db.execute(INCLUSIVE).fetchone()[0]
print("variante '>'  :", strict)
print("variante '>=' :", inclusive)

proposals = [strict, strict, inclusive]
reference = 100
value, votes = Counter(proposals).most_common(1)[0]
k = 2
print("propositions  :", proposals)
print(f"vote 2 sur 3  : consensus={votes >= k} valeur={value} votes={votes}")
print("référence     :", reference, "->", "faux consensus" if votes >= k and value != reference else "ok")
