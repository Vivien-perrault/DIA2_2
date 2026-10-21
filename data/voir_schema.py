import sqlite3
from pathlib import Path

chemin = Path("data/boutique.sqlite")
if not chemin.exists():
    raise SystemExit(f"Base introuvable : {chemin.resolve()}  (lance le script depuis le dossier du kit)")

c = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)  # lecture seule
tables = c.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'").fetchall()

for nom, sql in tables:
    print(sql)
    for ligne in c.execute(f'SELECT * FROM "{nom}" LIMIT 3'):
        print("   ", ligne)
    print()