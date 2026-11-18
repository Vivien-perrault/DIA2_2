# TD 2 – Rapport

## Étape 2 – Le faux consensus

### 2.0 Mécanisme illustré : DEMO-VOTE (exemple construit)

> **Nature : matériel pédagogique construit.** Ces valeurs et requêtes ne sont ni des sorties de modèles ni des réponses sur `boutique.sqlite`. Script : [`td2/sql/demo-vote.py`](../sql/demo-vote.py).

Table jouet d'une seule ligne : vente du `2026-01-01`, montant `100` centimes. Période demandée : du 1er janvier **inclus** au 2 janvier **exclu**.

| Variante | Condition | Résultat |
|---|---|---|
| Propositions 1 et 2 | `sale_date > '2026-01-01' AND sale_date < '2026-01-02'` | **0** |
| Proposition 3 | `sale_date >= '2026-01-01' AND sale_date < '2026-01-02'` | **100** |

Toutes utilisent `COALESCE(SUM(amount_cents), 0)`.

**Explication de la borne.** La seule vente a lieu exactement à `'2026-01-01'`. Avec `>`, la borne inférieure est **stricte**, donc la vente faite à la borne est exclue. La fenêtre testée est `]2026-01-01 ; 2026-01-02[` au lieu de `[2026-01-01 ; 2026-01-02[`. Aucune ligne ne correspond, et `COALESCE` transforme le `NULL` de `SUM` sur zéro ligne en `0`. Le résultat est donc un 0 « propre », qui ne déclenche aucune erreur.

**Vote contre référence.** Propositions `[0, 0, 100]`, seuil **k = 2 sur n = 3** : la valeur `0` obtient 2 voix et atteint le quorum, donc le vote renvoie **0**. La référence indépendante vaut **100**. C'est un **faux consensus** : deux propositions qui partagent la même erreur de borne battent la seule bonne réponse. Le vote mesure l'accord entre les modèles, pas la justesse. Une erreur corrélée (même clause fautive) passe donc le quorum.

Sortie exécutée :

```
variante '>'  : 0
variante '>=' : 100
propositions  : [0, 0, 100]
vote 2 sur 3  : consensus=True valeur=0 votes=2
référence     : 100 -> faux consensus
```

### 2.1 Identification du cas C10 dans les traces TD1

Les [traces TD1](../../td1/traces-td1.csv) contiennent 102 lignes. La dernière ligne par triplet `(provider, model_requested, case_id)` donne 100 résultats pour 20 questions et 5 modèles. En regroupant par question et par valeur les résultats non vides de verdict `incorrect`, on trouve trois accords sur une valeur fausse. C02 compte trois résultats à 0 centime (gpt-oss-20b, Cohere et Dots). C08 en compte deux à 0 centime (Cohere et Dots). C10 en compte deux à 119 410 centimes (Cohere et Qwen).

C10 est le cas principal. Les deux modèles qui donnent 119 410 centimes appartiennent au panel fixe, ce qui permet de comparer cet accord dans le panel et dans l’ensemble des cinq modèles. Les traces portent toutes la nature `real` et proviennent des exécutions du TD1 sur `boutique.sqlite`. La [référence indépendante](../../td1/reference-td1.csv) indique **558 980 centimes** pour C10, avec `checked_by` renseigné à **Akihito Raffin**. L’écart est de **439 570 centimes**.

| Fournisseur et modèle | `cell_id` | Valeur (centimes) | Verdict |
|---|---|---:|---|
| Groq · gpt-oss-120b | `groq:openai/gpt-oss-120b:C10` | 558 980 | `correct` |
| Groq · gpt-oss-20b | `groq:openai/gpt-oss-20b:C10` | 558 980 | `correct` |
| OpenRouter · Cohere north-mini-code | `openrouter:cohere/north-mini-code:free:C10` | **119 410** | `incorrect` |
| Groq · Qwen 3.8-27B | `groq:qwen/qwen3.8-27b:C10` | **119 410** | `incorrect` |
| OpenRouter · Dots 3 Note | `openrouter:dots-studio/dots-3-note-preview:free:C10` | — | `sql_invalid` |

### 2.2 Quorum de 2 sur 3

Le [panel fixe](../atelier-vote.py) comprend Groq gpt-oss-120b, OpenRouter Cohere North Mini Code et Groq Qwen 3.8-27B (`n = 3`, `k = 2`). Le script a été exécuté depuis la racine du dépôt sur les traces réelles des deux questions.

```sh
python td2/atelier-vote.py --traces td1/traces-td1.csv --case C10
python td2/atelier-vote.py --traces td1/traces-td1.csv --case C02
```

Pour C10, Cohere et Qwen votent pour 119 410 centimes et gpt-oss-120b vote pour 558 980. Le quorum donne 119 410 avec deux voix, un faux consensus. Pour C02, gpt-oss-120b et Qwen votent pour 590 320 centimes et Cohere vote pour 0. Le quorum donne 590 320 avec deux voix, conformément à la référence.

### 2.3 Quorum de 3 sur 5

Le panel ajoute Groq gpt-oss-20b et OpenRouter Dots 3 Note (`n = 5`, `k = 3`). Le même `vote_k_sur_n` a été exécuté sur les dernières tentatives des cinq modèles. Une cellule `sql_invalid` ou une valeur vide conserve sa place dans le panel et ne donne aucune voix. Une valeur numérique de 0 issue d’une requête exécutée compte comme une voix.

Pour C10, gpt-oss-120b et gpt-oss-20b votent pour 558 980, Cohere et Qwen pour 119 410, et Dots ne vote pas. Les deux valeurs sont à égalité avec deux voix chacune et aucune n’atteint le quorum. Pour C02, gpt-oss-20b, Cohere et Dots donnent trois voix à 0. Les deux autres voix, de gpt-oss-120b et Qwen, vont à 590 320. Le quorum donne 0, un faux consensus.

| Question | 2 sur 3 | 3 sur 5 | Référence (centimes) |
|---|---|---|---:|
| C10 | 119 410, 2 voix, faux consensus | Aucun quorum, 2 voix par valeur et 1 sans vote | 558 980 |
| C02 | 590 320, 2 voix, consensus correct | 0, 3 voix, faux consensus | 590 320 |

### 2.4 Requêtes C10 exécutées sur SQLite

Les requêtes complètes ont été extraites de la dernière tentative de chaque modèle dans les [traces TD1](../../td1/traces-td1.csv) et de la ligne C10 du [fichier de référence](../../td1/reference-td1.csv). Les trois fichiers ont été exécutés avec Python et SQLite sur `td1/data/boutique.sqlite`, ouverte en lecture seule.

| Requête complète | Résultat (centimes) |
|---|---:|
| [Cohere North Mini Code](../sql/C10-cohere.sql) | 119 410 |
| [Qwen 3.8-27B](../sql/C10-qwen.sql) | 119 410 |
| [Référence C10](../sql/C10-reference.sql) | 558 980 |

### 2.5 Diagnostic de la clause WHERE

C10 demande le chiffre d’affaires HT des commandes passées quand le client avait exactement 25 ans. Les trois requêtes additionnent `o.quantity_product * p.price` et font les mêmes jointures internes sur `customer_id` et `product_id`. La référence filtre par date de commande, du 25e anniversaire inclus au 26e anniversaire exclu, avec `date(c.birth_date, '+25 years') <= date(o.date)` et `date(o.date) < date(c.birth_date, '+26 years')`.

- **Cohere** exige un écart de 25 entre les années civiles et un mois-jour de commande supérieur ou égal au mois-jour de naissance. Cette condition couvre le 25e anniversaire jusqu’à la fin de l’année civile. Elle exclut les commandes passées l’année civile suivante avant le 26e anniversaire, où l’écart entre les années vaut 26 et le mois-jour est inférieur.
- **Qwen** reprend la même condition dans sa première branche, en comparant le mois et le jour concaténés au format `MMDD`. Sa seconde branche exige un écart de 24 entre les années et un mois-jour de commande inférieur à celui de naissance. Cela correspond à un âge de 23 ans révolus. Pour couvrir le début de l’année du 26e anniversaire, cette branche devrait tester un écart de 26 en conservant la comparaison stricte du mois-jour.

Les deux modèles omettent donc la même période. Qwen ajoute un filtre qui pourrait sélectionner des commandes de clients âgés de 23 ans. Sur cette base, l’exécution séparée de cette branche retourne zéro ligne de commande, tandis que sa première branche en retourne 14 pour 119 410 centimes. Cela explique pourquoi les deux requêtes donnent la même valeur.

### 2.6 Delta par client et vérification indépendante

La [requête delta C10](../sql/delta-C10.sql) a été exécutée sur `boutique.sqlite` ouverte en lecture seule. Elle compare, pour chaque ligne de commande, le filtre de la référence aux filtres de Cohere et de Qwen, puis cumule le CA HT manquant et ajouté par client. Le delta soustrait le CA HT ajouté au CA HT manquant. Les deux modèles donnent la même sortie par client.

| `customer_id` | CA HT manquant (centimes) | CA HT ajouté (centimes) | Delta (centimes) |
|---|---:|---:|---:|
| C004 | 150 260 | 0 | 150 260 |
| C005 | 150 240 | 0 | 150 240 |
| C007 | 118 740 | 0 | 118 740 |
| C022 | 20 330 | 0 | 20 330 |
| **Total par modèle** | **439 570** | **0** | **439 570** |

Pour chaque modèle, la somme des deltas vaut exactement **558 980 − 119 410 = 439 570 centimes**.

Baptiste a vérifié le résultat en Python sur les [trois CSV source](../../td1/data) `orders.csv`, `customers.csv` et `product.csv`. Pour chaque ligne, il a calculé l’âge révolu comme l’écart entre les années civiles diminué d’un an si la commande précède l’anniversaire dans l’année, puis multiplié la quantité par le prix unitaire. Le calcul retient les clients de 25 ans pour la référence, le sous-ensemble dont l’écart d’années est 25 pour Cohere, et ajoute à ce sous-ensemble les clients de 23 ans dont l’écart d’années est 24 pour Qwen. Il retrouve les trois totaux et les quatre deltas par client pour chacun des modèles.

### 2.7 Cas historique rejoué : DEMO-SQL-C11 (complément)

> **Nature : cas historique rejoué.** Les requêtes M1 et M2 viennent du lot pilote de septembre 2026 et sont reproduites telles que l'énoncé TD2 les donne. Ce ne sont **pas** des traces de notre lot TD1. On les a seulement réexécutées sur `td1/data/boutique.sqlite`, ouverte en lecture seule. Notre cas principal reste C10.

**Question C11** : CA HT, en centimes, de toutes les commandes des clients âgés d'**exactement 25 ans** à la date de référence 2026-12-01.

| Requête | Modèle d'origine | Résultat (centimes) |
|---|---|---:|
| [M1](../sql/C11-M1-gpt-oss-20b.sql) | openai/gpt-oss-20b (Groq) | **0** |
| [M2](../sql/C11-M2-cohere.sql) | cohere/north-mini-code:free (OpenRouter) | **0** |
| Référence C11 ([`reference-td1.csv`](../../td1/reference-td1.csv), `checked_by` = Chandra R S SUKUMAR) | — | **446 690** |

Les deux modèles s'accordent sur la même valeur fausse, 0. Avec deux propositions identiques, un vote 2 sur 3 les validerait si le troisième membre du panel répondait autrement. L'écart à expliquer est de **446 690 − 0 = 446 690 centimes**.

**Fenêtre requise.** Avoir exactement 25 ans au 2026-12-01, c'est avoir passé son 25e anniversaire sans avoir encore atteint le 26e, soit `date(birth_date, '+25 years') <= '2026-12-01' < date(birth_date, '+26 years')`. Cela correspond à **`'2000-12-02' <= birth_date <= '2001-12-01'`**, une fenêtre d'un an. La référence applique exactement cette condition.

**Fenêtre testée par M1.** `c.birth_date = '2001-12-01'` ne retient que les clients dont le 25e anniversaire tombe **le jour même** de la date de référence. La fenêtre d'un an est réduite à un seul jour. Aucun client de la base n'est né le 2001-12-01, d'où 0 ligne. `COALESCE` transforme ensuite le `NULL` de `SUM` en un 0 qui ne signale rien d'anormal.

**Fenêtre testée par M2.** Les deux conditions se réduisent à `birth_date <= '2026-12-01'` **et** `birth_date >= '2027-12-01'`, qui sont contradictoires : la fenêtre est **vide**, quelles que soient les données. M2 compare la date de naissance directement à la date de référence, sans retrancher 25 ans. Le `+1 year` déplace en plus la seconde borne dans le mauvais sens. Les `CAST(strftime(...))` ne changent rien, puisque les dates sont déjà au format texte `YYYY-MM-DD`.

Les deux erreurs sont **différentes** : un seul jour pour M1, une fenêtre vide pour M2. Elles produisent pourtant la même valeur, parce que toute fenêtre qui ne contient aucun client donne 0 avec `COALESCE`. L'accord sur 0 ne prouve donc pas une cause commune. C'est la valeur par défaut de deux filtres faux.

**Requête de diagnostic** ([`delta-C11.sql`](../sql/delta-C11.sql)), exécutée sur `boutique.sqlite`. Elle liste les clients âgés de 25 ans au 2026-12-01 et le CA HT de leurs commandes. Les colonnes `counted_by_m1` et `counted_by_m2` rejouent les filtres de M1 et de M2 sur chaque client.

| `customer_id` | `birth_date` | Lignes de commande | CA HT (centimes) | Compté par M1 | Compté par M2 |
|---|---|---:|---:|:-:|:-:|
| C001 | 2001-09-25 | 18 | 135 000 | 0 | 0 |
| C002 | 2001-09-24 | 6 | 25 920 | 0 | 0 |
| C003 | 2001-09-26 | 6 | 47 900 | 0 | 0 |
| C006 | 2001-11-30 | 10 | 77 450 | 0 | 0 |
| C008 | 2001-05-15 | 11 | 99 090 | 0 | 0 |
| C009 | 2001-03-10 | 9 | 61 330 | 0 | 0 |
| **Total** | | **60** | **446 690** | | |

La somme vaut exactement la référence : ces six clients expliquent **tout** l'écart avec 0. Aucun d'eux n'est retenu par M1 ni par M2, et aucun client n'est ajouté à tort. Bornes de la fenêtre : C007 (né le 2000-11-30) a eu 26 ans le 2026-11-30 et est **exclu** à raison. C006 (né le 2001-11-30) a eu 25 ans le même jour et est **inclus**. C014 (né le 2001-12-08) n'aura 25 ans qu'après la date de référence.

**Vérification indépendante.** La somme de la requête de diagnostic (446 690), qui groupe par client, a été comparée à la valeur de la requête de référence de `reference-td1.csv`, réexécutée sur la base (446 690), puis à la valeur stockée dans le CSV (446 690). Les clients situés aux bornes de la fenêtre ont été vérifiés un par un.

**Lien avec notre lot TD1.** Sur C11, notre lot donne 446 690 (correct) pour gpt-oss-120b, gpt-oss-20b, Qwen et Dots. Seul Cohere ([`openrouter:cohere/north-mini-code:free:C11`](../../td1/traces-td1.csv)) renvoie 0. Sa requête contient `c.birth_date > '2025-12-01'`, qui ne retient que des clients nés dans l'année précédant la date de référence : même famille d'erreur que M2, avec une date de naissance comparée à la date de référence sans retrancher 25 ans. Ce 0 reste **isolé** dans notre lot, ce n'est donc pas un faux consensus. Les quatre bonnes réponses l'emportent en 2 sur 3 comme en 3 sur 5.
