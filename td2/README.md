# TD 2 – Le quorum, puis la règle de routage

Sous-groupe **DIA2_2** (Majeure DIA, ESILV). Séance 2, 18 novembre 2026.
Énoncé : [enonce-td2-en.md](enonce-td2-en.md). Rapport : [reports/td2.md](reports/td2.md).

> **Squelette en cours de séance.** Les sections marquées _À compléter_ seront remplies une fois les livrables correspondants poussés.

## Données d'entrée

Le TD 2 ne fait **aucun nouvel appel réseau**. Il réutilise les traces réelles du TD 1 :

- [../td1/traces-td1.csv](../td1/traces-td1.csv) : 102 appels, 5 modèles × 20 questions ;
- [../td1/reference-td1.csv](../td1/reference-td1.csv) : les 20 références vérifiées ;
- [../td1/data/boutique.sqlite](../td1/data/boutique.sqlite) : la base, inchangée.

## État des livrables

| # | Livrable (énoncé) | État | Où |
|---|---|---|---|
| 1 | `vote_k_sur_n` complété | Fait | [../td1/skeleton-multi-llm-en.py](../td1/skeleton-multi-llm-en.py) (voir « Points ouverts ») |
| 2 | Tableau des 20 décisions du vote | _À compléter_ | _À compléter_ |
| 3 | Faux consensus commenté (C10, contre-exemple C02, compléments DEMO-VOTE et DEMO-SQL-C11) | En cours : étapes 1 à 9 du plan faites, 10 à 12 restantes | [reports/td2.md](reports/td2.md), [sql/](sql/), plan [../PLAN-TD2-ETAPE2.md](../PLAN-TD2-ETAPE2.md) |
| 4 | Règle de routage d'une page, justifiée par les cellules du TD 1 | _À compléter_ | _À compléter_ |
| 5 | Sorties du simulateur, avant et après adaptation | _À compléter_ | _À compléter_ |
| 6 | Prompts, s'ils ont changé depuis le TD 1 | Inchangés : aucun nouvel appel | [../td1/prompts-en.md](../td1/prompts-en.md) |

## Faux consensus : résumé

| Question | Panel 2 sur 3 (GPT-OSS 120B, Cohere, Qwen) | 5 modèles, 3 sur 5 | Référence |
|---|---|---|---:|
| **C10** | consensus **faux** à 119 410 (Cohere + Qwen) | abstention (2 contre 2) | 558 980 |
| C02 | correct à 590 320 | consensus **faux** à 0 | 590 320 |

Cause et preuve de C10 : [reports/td2.md](reports/td2.md), sections 2.4 à 2.6, et [sql/delta-C10.sql](sql/delta-C10.sql).

## Règle de routage

_À compléter : une ligne par famille (période, âge à une date, âge à la commande, produits, combinaisons), avec le premier modèle appelé, la vérification retenue selon l'usage, la conduite si le modèle est indisponible, et la cellule du TD 1 qui justifie chaque ligne._

## Fichiers du dossier

| Fichier | Rôle |
|---|---|
| [atelier-vote.py](atelier-vote.py) | Exerce `vote_k_sur_n` sur 4 exemples synthétiques, puis sur les traces réelles avec le panel fixe 2 sur 3. Modifié pour chercher le squelette dans `../td1/`. |
| [atelier-routage.py](atelier-routage.py) | Simulateur de routage, 7 scénarios, ressources fictives, sans appel réseau |
| [sql/demo-vote.py](sql/demo-vote.py) | DEMO-VOTE : exemple construit `[0, 0, 100]` |
| [sql/](sql/) `C10-*.sql`, `delta-C10.sql` | Requêtes C10 des modèles et de la référence, requête delta |
| [sql/](sql/) `C11-*.sql`, `delta-C11.sql` | Cas historique rejoué DEMO-SQL-C11 |
| [reports/td2.md](reports/td2.md) | Rapport de séance |

## Reproduire

Depuis ce dossier, avec l'environnement virtuel à la racine du dépôt :

```powershell
..\.venv\Scripts\Activate.ps1
python atelier-vote.py                                          # 4 exemples synthétiques
python atelier-vote.py --traces ../td1/traces-td1.csv --case C10  # une question réelle (remplacer C10)
python sql/demo-vote.py                                         # DEMO-VOTE
python atelier-routage.py                                       # les 7 scénarios du simulateur
```

## Vérifications croisées

| Quoi | Vérifié par | Trace écrite |
|---|---|---|
| Delta C10 = 439 570 centimes | Baptiste Marseille, recalcul Python sur les CSV | [reports/td2.md](reports/td2.md), section 2.6 |
| Relecture complète du faux consensus | _À compléter (étape 11 du plan)_ | _À compléter_ |
| Tableau des 20 décisions | _À compléter_ | _À compléter_ |
| Règle de routage | _À compléter_ | _À compléter_ |

## Contributions

| Membre | Contribution TD 2 |
|---|---|
| Nazim Yacine | Plan de l'étape 2 ; DEMO-VOTE (étape 1) ; DEMO-SQL-C11 (étape 9) |
| Baptiste Marseille | `vote_k_sur_n` ; étapes 2 à 8 du plan (cas C10, quorums, requêtes, diagnostic, delta et sa vérification) |
| Ismaël Wane | Réorganisation du dépôt en `td1/`, `td2/`, `td3/` ; adaptation de `atelier-vote.py` |
| Antonin Charron | Schéma d'architecture du projet |
| _À compléter_ | Règle de routage et simulateur |
| _À compléter_ | Tableau des 20 décisions |

Un assistant de code IA est utilisé en aller-retour, par petits prompts successifs ; ses sorties sont vérifiées manuellement au sein du sous-groupe.

## Points ouverts

- `vote_k_sur_n` est codé dans `td1/skeleton-multi-llm-en.py`, que `atelier-vote.py` importe : c'est du travail du TD 2 situé dans le dossier du TD 1. Le prompt du squelette, lui, est inchangé.
- Tableau des 20 décisions du vote à produire.
- Règle de routage et sorties du simulateur à intégrer.
