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

Sortie exécutée (vote `vote_k_sur_n` de l'étape 1, dans `td2/skeleton-multi-llm-en.py`) :

```json
{"case": "C10", "nature": "real", "n": 3, "k": 2, "decision": {"consensus": true, "value": 119410, "votes": 2, "models": ["openrouter:cohere/north-mini-code:free", "groq:qwen/qwen3.8-27b"]}, "reference": 558980, "matches_reference": false}
{"case": "C02", "nature": "real", "n": 3, "k": 2, "decision": {"consensus": true, "value": 590320, "votes": 2, "models": ["groq:openai/gpt-oss-120b", "groq:qwen/qwen3.8-27b"]}, "reference": 590320, "matches_reference": true}
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

Requête Cohere North Mini Code (`openrouter:cohere/north-mini-code:free:C10`), telle que renvoyée par le modèle :

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE CAST(strftime('%Y', o.date) - strftime('%Y', c.birth_date) AS INTEGER) = 25
  AND CAST(strftime('%m-%d', o.date) >= CAST(strftime('%m-%d', c.birth_date) AS TEXT) AS INTEGER) = 1;
```

Requête Qwen 3.8-27B (`groq:qwen/qwen3.8-27b:C10`), telle que renvoyée par le modèle :

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (
    (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
    AND (strftime('%m', o.date) || strftime('%d', o.date)) >= (strftime('%m', c.birth_date) || strftime('%d', c.birth_date))
)
OR (
    (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 24
    AND (strftime('%m', o.date) || strftime('%d', o.date)) < (strftime('%m', c.birth_date) || strftime('%d', c.birth_date))
);
```

Requête de référence C10 (`td1/reference-td1.csv`) :

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id JOIN customers c ON o.customer_id = c.customer_id WHERE date(c.birth_date, '+25 years') <= date(o.date) AND date(c.birth_date, '+26 years') > date(o.date)
```

### 2.5 Diagnostic de la clause WHERE

C10 demande le chiffre d’affaires HT des commandes passées quand le client avait exactement 25 ans. Les trois requêtes additionnent `o.quantity_product * p.price` et font les mêmes jointures internes sur `customer_id` et `product_id`. La référence filtre par date de commande, du 25e anniversaire inclus au 26e anniversaire exclu, avec `date(c.birth_date, '+25 years') <= date(o.date)` et `date(o.date) < date(c.birth_date, '+26 years')`.

- **Cohere** exige un écart de 25 entre les années civiles et un mois-jour de commande supérieur ou égal au mois-jour de naissance. Cette condition couvre le 25e anniversaire jusqu’à la fin de l’année civile. Elle exclut les commandes passées l’année civile suivante avant le 26e anniversaire, où l’écart entre les années vaut 26 et le mois-jour est inférieur.
- **Qwen** reprend la même condition dans sa première branche, en comparant le mois et le jour concaténés au format `MMDD`. Sa seconde branche exige un écart de 24 entre les années et un mois-jour de commande inférieur à celui de naissance. Cela correspond à un âge de 23 ans révolus. Pour couvrir le début de l’année du 26e anniversaire, cette branche devrait tester un écart de 26 en conservant la comparaison stricte du mois-jour.

Les deux modèles omettent donc la même période. Qwen ajoute un filtre qui pourrait sélectionner des commandes de clients âgés de 23 ans. Sur cette base, l’exécution séparée de cette branche retourne zéro ligne de commande, tandis que sa première branche en retourne 14 pour 119 410 centimes. Cela explique pourquoi les deux requêtes donnent la même valeur.

### 2.6 Delta par client et vérification indépendante

La [requête delta C10](../sql/delta-C10.sql) a été exécutée sur `boutique.sqlite` ouverte en lecture seule. Elle compare, pour chaque ligne de commande, le filtre de la référence aux filtres de Cohere et de Qwen, puis cumule le CA HT manquant et ajouté par client. Le delta soustrait le CA HT ajouté au CA HT manquant. Les deux modèles donnent la même sortie par client. Dans la CTE `classified`, `in_cohere` et `in_qwen` reprennent la condition `WHERE` de chaque modèle : écart d'années civiles et comparaison du mois-jour. La comparaison `'%m-%d'` donne le même ordre que la concaténation `MMDD` de Qwen. `in_reference` reprend la condition de la référence.

```sql
WITH order_lines AS (
    SELECT o.customer_id,
           o.quantity_product * p.price AS revenue_cents,
           date(o.date) AS order_date, c.birth_date,
           strftime('%Y', o.date) - strftime('%Y', c.birth_date) AS year_gap,
           strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date)
               AS birthday_reached
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN product p ON o.product_id = p.product_id
),
classified AS (
    SELECT *,
           date(birth_date, '+25 years') <= order_date
               AND order_date < date(birth_date, '+26 years') AS in_reference,
           year_gap = 25 AND birthday_reached AS in_cohere,
           (year_gap = 25 AND birthday_reached)
               OR (year_gap = 24 AND NOT birthday_reached) AS in_qwen
    FROM order_lines
),
delta_lines AS (
    SELECT customer_id, 'Cohere' AS model,
           (in_reference - in_cohere) * revenue_cents AS delta_cents
    FROM classified
    WHERE in_reference <> in_cohere
    UNION ALL
    SELECT customer_id, 'Qwen' AS model,
           (in_reference - in_qwen) * revenue_cents AS delta_cents
    FROM classified
    WHERE in_reference <> in_qwen
)
SELECT model, customer_id,
       SUM(CASE WHEN delta_cents > 0 THEN delta_cents ELSE 0 END) AS missing_cents,
       -SUM(CASE WHEN delta_cents < 0 THEN delta_cents ELSE 0 END) AS extra_cents,
       SUM(delta_cents) AS delta_cents
FROM delta_lines
GROUP BY model, customer_id
ORDER BY model, customer_id;
```

Sortie (identique pour `model = 'Cohere'` et `model = 'Qwen'`) :

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

```sql
-- DEMO-SQL-C11, cas historique rejoué (lot pilote de septembre 2026, pas notre lot TD1)
-- Requête M1, openai/gpt-oss-20b (Groq), telle que fournie dans l'énoncé TD2
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date = '2001-12-01';
```

```sql
-- DEMO-SQL-C11, cas historique rejoué (lot pilote de septembre 2026, pas notre lot TD1)
-- Requête M2, cohere/north-mini-code:free (OpenRouter), telle que fournie dans l'énoncé TD2
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE CAST(strftime('%Y-%m-%d', '2026-12-01') AS TEXT) >= c.birth_date
  AND CAST(strftime('%Y-%m-%d', '2026-12-01', '+1 year') AS TEXT) <= c.birth_date;
```

Les deux modèles s'accordent sur la même valeur fausse, 0. Avec deux propositions identiques, un vote 2 sur 3 les validerait si le troisième membre du panel répondait autrement. L'écart à expliquer est de **446 690 − 0 = 446 690 centimes**.

**Fenêtre requise.** Avoir exactement 25 ans au 2026-12-01, c'est avoir passé son 25e anniversaire sans avoir encore atteint le 26e, soit `date(birth_date, '+25 years') <= '2026-12-01' < date(birth_date, '+26 years')`. Cela correspond à **`'2000-12-02' <= birth_date <= '2001-12-01'`**, une fenêtre d'un an. La référence applique exactement cette condition.

**Fenêtre testée par M1.** `c.birth_date = '2001-12-01'` ne retient que les clients dont le 25e anniversaire tombe **le jour même** de la date de référence. La fenêtre d'un an est réduite à un seul jour. Aucun client de la base n'est né le 2001-12-01, d'où 0 ligne. `COALESCE` transforme ensuite le `NULL` de `SUM` en un 0 qui ne signale rien d'anormal.

**Fenêtre testée par M2.** Les deux conditions se réduisent à `birth_date <= '2026-12-01'` **et** `birth_date >= '2027-12-01'`, qui sont contradictoires : la fenêtre est **vide**, quelles que soient les données. M2 compare la date de naissance directement à la date de référence, sans retrancher 25 ans. Le `+1 year` déplace en plus la seconde borne dans le mauvais sens. Les `CAST(strftime(...))` ne changent rien, puisque les dates sont déjà au format texte `YYYY-MM-DD`.

Les deux erreurs sont **différentes** : un seul jour pour M1, une fenêtre vide pour M2. Elles produisent pourtant la même valeur, parce que toute fenêtre qui ne contient aucun client donne 0 avec `COALESCE`. L'accord sur 0 ne prouve donc pas une cause commune. C'est la valeur par défaut de deux filtres faux.

**Requête de diagnostic** ([`delta-C11.sql`](../sql/delta-C11.sql)), exécutée sur `boutique.sqlite`. Elle liste les clients âgés de 25 ans au 2026-12-01 et le CA HT de leurs commandes. Les colonnes `counted_by_m1` et `counted_by_m2` rejouent les filtres de M1 et de M2 sur chaque client.

```sql
-- DEMO-SQL-C11 : clients âgés d'exactement 25 ans au 2026-12-01 et CA HT de toutes leurs commandes.
-- Fenêtre requise : 25e anniversaire <= 2026-12-01 < 26e anniversaire,
-- soit 2000-12-02 <= birth_date <= 2001-12-01.
-- M1 et M2 renvoient 0 : chaque ligne ci-dessous est donc manquée par les deux,
-- et la somme de la colonne revenue_cents doit égaler la référence C11 (446690).
SELECT c.customer_id,
       c.birth_date,
       COUNT(*) AS order_lines,
       SUM(o.quantity_product * p.price) AS revenue_cents,
       (c.birth_date = '2001-12-01') AS counted_by_m1,
       ('2026-12-01' >= c.birth_date AND '2027-12-01' <= c.birth_date) AS counted_by_m2
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE date(c.birth_date, '+25 years') <= '2026-12-01'
  AND date(c.birth_date, '+26 years') >  '2026-12-01'
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;
```

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

### 2.8 Synthèse du livrable

| Élément exigé | Contenu | Où |
|---|---|---|
| Identifiant | **C10** : CA HT des commandes passées quand le client avait exactement 25 ans | 2.1 |
| Source et nature | Lot TD1 de l’équipe, nature `real`, exécuté sur `boutique.sqlite`. DEMO-VOTE est un **exemple construit** (2.0) et DEMO-SQL-C11 un **cas historique rejoué** (2.7). Ces deux cas restent hors des comptes de notre lot. | 2.0, 2.1, 2.7 |
| Modèles d’accord | `openrouter:cohere/north-mini-code:free` et `groq:qwen/qwen3.8-27b`, tous deux à **119 410 centimes** | 2.1 |
| Référence indépendante | **558 980 centimes**, [`reference-td1.csv`](../../td1/reference-td1.csv), `checked_by` = Akihito Raffin | 2.1 |
| Quorum 2 sur 3 (panel fixe) | 119 410, 2 voix : **faux consensus** | 2.2 |
| Quorum 3 sur 5 (5 modèles TD1) | **Aucun quorum** : 2 voix contre 2, Dots sans vote (`sql_invalid`) | 2.3 |
| Contre-exemple | C02 : correct en 2 sur 3 (590 320), faux consensus à 0 en 3 sur 5 | 2.2, 2.3 |
| Cause SQL | Le filtre `WHERE` remplace l’âge révolu par « écart d’années civiles = 25 et anniversaire atteint ». Il oublie les commandes de l’année civile suivante passées avant le 26e anniversaire. La seconde branche de Qwen vise 23 ans et ne sélectionne aucune ligne. | 2.5 |
| Requêtes complètes | [Cohere](../sql/C10-cohere.sql), [Qwen](../sql/C10-qwen.sql), [référence](../sql/C10-reference.sql) | 2.4 |
| Requête delta exécutée | [`delta-C10.sql`](../sql/delta-C10.sql) : C004, C005, C007 et C022, soit **439 570 centimes** manquants, 0 ajouté | 2.6 |
| Vérification indépendante | Calcul Python sur les CSV source (Baptiste), puis relecture croisée complète par script (Akihito) | 2.6, 2.9 |
| Traces | [`td1/traces-td1.csv`](../../td1/traces-td1.csv), `cell_id` listés en 2.1 | 2.1 |

**Méthode de contrôle qui détecte l’erreur partagée.** Le vote ne la détecte pas : en 2 sur 3, il valide 119 410. Deux contrôles la détectent :

1. **Comparaison à une référence indépendante** écrite et vérifiée par un humain, avec une autre formulation de l’âge (`date(birth_date, '+25 years') <= date(o.date) < date(birth_date, '+26 years')`). L’écart de 439 570 centimes apparaît aussitôt.
2. **Requête delta par client**, qui localise l’écart. Les quatre clients manqués ont tous des commandes passées entre le 1er janvier et leur 26e anniversaire. Cela désigne la clause fautive sans relire les requêtes.

Un panel élargi (3 sur 5) ne fait que **signaler un doute** sur C10, sans majorité. Ce doute peut déclencher une escalade vers ces contrôles, mais ne donne pas la bonne valeur. Sur C02, le même élargissement **crée** au contraire un faux consensus. Changer de panel est donc un contrôle candidat, pas une garantie.

### 2.9 Relecture croisée

Le script [`td2/sql/relecture.py`](../sql/relecture.py) relance chaque requête et chaque vote des sections 2.0 à 2.7. Il compare chaque résultat au chiffre écrit dans le rapport. La base est ouverte en lecture seule et le vote utilise `vote_k_sur_n` du squelette TD1.

```sh
python td2/sql/relecture.py
```

Les **36 contrôles** sont conformes. Ils couvrent :

- DEMO-VOTE : 0 et 100, puis le vote `[0, 0, 100]` qui renvoie 0 avec 2 voix ;
- les traces : 102 lignes, 100 dernières tentatives, nature `real`, les trois valeurs fausses partagées (C02, C08, C10), les cinq valeurs C10 et les `cell_id` cités ;
- les références C02, C10 et C11, avec leur `checked_by` ;
- les quatre votes (C10 et C02, en 2 sur 3 et en 3 sur 5) ;
- les trois requêtes C10, et la requête de référence relue directement dans le CSV ;
- les deux branches de Qwen : 14 lignes pour 119 410 centimes, puis 0 ligne ;
- le delta C10 par client pour chaque modèle (somme 439 570), recalculé aussi en Python sur les CSV sans SQL ;
- la commande `atelier-vote.py` citée en 2.2, relancée telle quelle sur C10 et C02 ;
- M1, M2, la référence C11 et les six lignes de `delta-C11.sql` (60 lignes de commande, 446 690 centimes), puis les valeurs C11 de notre lot.

**Étiquetage.** La section 2.0 porte la mention « exemple construit » et la section 2.7 la mention « cas historique rejoué ». Ni l’un ni l’autre n’entre dans les comptes de notre lot.

**Point relevé et corrigé.** La commande `python td2/atelier-vote.py --traces td1/traces-td1.csv --case C10`, citée en 2.2, échouait. La copie locale `td2/skeleton-multi-llm-en.py` (commit `1967886`, étape 1) a priorité sur le squelette TD1, et elle cherchait `sandbox_sqlite.py` seulement dans `td2/`, d'où un `FileNotFoundError`. Un troisième emplacement, `../td1/sandbox_sqlite.py`, a été ajouté à `RESOURCES["sandbox"]`. La commande relancée avec le `vote_k_sur_n` de l'étape 1 redonne les sorties de 2.2. `relecture.py` vérifie ce résultat.

### 2.10 Contributions à l’étape 2

| Membre | Étapes du plan | Contribution |
|---|---|---|
| Nazim Yacine | 1 et 9 | Plan de travail, DEMO-VOTE (script et section 2.0), rejeu de DEMO-SQL-C11 avec les requêtes M1, M2 et `delta-C11.sql` (section 2.7). Après la relecture : correction du chemin `sandbox_sqlite.py` pour relancer `atelier-vote.py`, et ajout des requêtes complètes dans le rapport (2.2, 2.4, 2.6, 2.7, 2.9) |
| Baptiste Marseille | 2 à 8 | Confirmation du cas C10 dans les traces, quorums 2 sur 3 et 3 sur 5, extraction et exécution des requêtes C10, diagnostic du `WHERE`, requête delta et vérification Python sur les CSV (sections 2.1 à 2.6) |
| Akihito Raffin | 10 à 12 | Synthèse du livrable et méthode de contrôle (2.8), script de relecture croisée et vérification de tous les chiffres (2.9), contributions et commit final (2.10). Auteur de la vérification de la référence C10 au TD1 |

---

## Étape 3 – La règle de routage

### 3.1 Règle de routage sur une page (par famille de questions)

> **Portée et limite (CM 2, § 23 ; énoncé TD 2, § 10).** Les taux ci-dessous sont mesurés sur les 20 questions de notre lot TD 1 ([`model-question-comparison-en.csv`](../../td1/model-question-comparison-en.csv), [`five-model-summary-en.csv`](../../td1/five-model-summary-en.csv)) et les prix viennent du [portefeuille](../../td3/portefeuille-modeles-2026-09-28.csv). Vingt questions soutiennent une hypothèse spécifique au lot, et non un taux d'erreur général, un classement permanent ou une garantie d'erreur du quorum.

#### Principes généraux (CM 2, § 26–32)
1. **Séparer difficulté et enjeu** : la famille de question fixe le niveau minimal d'éligibilité du modèle ; l'enjeu (tableau de bord interne, chiffre affiché au client, montant versé) fixe la vérification requise avant livraison.
2. **Filtrer d'abord, prendre le moins cher ensuite** : on filtre d'abord les ressources par niveau (taux TD 1), disponibilité et budget, puis on retient la moins chère. Un modèle gratuit insuffisant reste exclu.
3. **Contrainte de cohérence sur la vérification (`none`)** : appeler un seul modèle gratuit sans vérification supplémentaire (`none`, contrôle de format uniquement) n'est admissible **que** pour un *tableau de bord interne* (faible enjeu) **et** sur une famille où ce modèle atteint **100 %** dans notre tableau TD 1. Dès qu'un modèle a fait au moins une erreur sur la famille au TD 1, ou dès que le chiffre est affiché au client ou gouverne un paiement, un quorum ou une vérification déterministe est obligatoire. La vérification reste toujours attachée à la **requête**, y compris sur les routes de repli (CM 2, § 37).

#### Règle par famille de questions

| Famille (cellules TD 1) | Taux exacts TD 1 (`correct / cas`) | 1er modèle appelé (le moins cher éligible) | Vérification selon l'usage (interne / client / paiement) | Conduite si le 1er modèle est indisponible |
|---|---|---|---|---|
| **F1 – Période**<br>`C01, C04, C05, C06, C07, C20` (6 cas) | • `gpt-oss-120b` : **6/6 (100 %)**<br>• `gpt-oss-20b` : **6/6 (100 %)** (`C20` réussi au 2e essai)<br>• `cohere/north-mini-code:free` : **6/6 (100 %)**<br>• `qwen3.8-27b` : **6/6 (100 %)**<br>• `dots-3-note-preview:free` : **6/6 (100 %)** | `openai/gpt-oss-20b#groq` (gratuit, 0 USD, G5, 6/6 sur `C01, C04–C07, C20`) | • **Interne** : `none` (format seul, 100 % au TD 1)<br>• **Client** : quorum **2 sur 3** (panel fixe) ou vérif déterministe<br>• **Paiement** : quorum **3 sur 5** + vérif déterministe / revue humaine | 1. Passer au modèle gratuit suivant à 100 % sur un autre fournisseur (`cohere/north-mini-code:free#openrouter` ou `qwen/qwen3.8-27b#groq`, 0 USD).<br>2. Si quotas gratuits épuisés et requête différable (`can_wait`) : **`defer`** jusqu'au renouvellement (re-vérifier la dispo au réveil).<br>3. Si urgent et budget autorisé : `openai/gpt-oss-120b#openrouter` (G4, 0,15 / 0,60 USD par 1M tokens).<br>4. Sinon : **`abstain`**. |
| **F2 – Âge révolu à une date**<br>`C02, C08, C09, C11` (4 cas) | • `gpt-oss-120b` : **4/4 (100 %)**<br>• `qwen3.8-27b` : **4/4 (100 %)**<br>• `gpt-oss-20b` : **3/4 (75 %)** (`C02` faux)<br>• `dots-3-note-preview:free` : **1/4 (25 %)** (`C11` ok ; `C02, C08, C09` faux)<br>• `cohere/north-mini-code:free` : **0/4 (0 %)** (`C02, C08, C11` faux ; `C09` `sql_invalid`) | `qwen/qwen3.8-27b#groq` (gratuit, 0 USD, G5, 4/4 sur `C02, C08, C09, C11`) | • **Interne** : `none` uniquement avec `qwen3.8-27b` ou `gpt-oss-120b` (100 % au TD 1) ; **interdit** si repli sur `gpt-oss-20b` (75 % $\rightarrow$ vérif déterministe obligatoire)<br>• **Client** : vérif déterministe des bornes SQL (car en 3 sur 5 sur `C02`, faux consensus à 0)<br>• **Paiement** : vérif déterministe + revue humaine | 1. Basculer sur l'autre modèle gratuit à 100 % : `openai/gpt-oss-120b#groq` (0 USD, 4/4).<br>2. Si quota Groq épuisé et requête différable : **`defer`**.<br>3. Si urgent et budget autorisé : `openai/gpt-oss-120b#openrouter` (0,15 / 0,60 USD/1M). *Exclure Cohere et Dots (0 % et 25 %).*<br>4. Sinon : **`abstain`**. |
| **F2b – Âge à la commande**<br>`C10` (1 cas) | • `gpt-oss-120b` : **1/1 (100 %)**<br>• `gpt-oss-20b` : **1/1 (100 %)**<br>• `cohere/north-mini-code:free` : **0/1 (0 %)** (`C10` faux)<br>• `qwen3.8-27b` : **0/1 (0 %)** (`C10` faux)<br>• `dots-3-note-preview:free` : **0/1 (0 %)** (`C10` `sql_invalid`) | `openai/gpt-oss-120b#groq` (gratuit, 0 USD, G5, 1/1 sur `C10`, sans limite TPM 8 000) | • **Interne** : `none` admissible uniquement avec `gpt-oss-120b` ou `gpt-oss-20b` (1/1 au TD 1, mais échantillon $n=1$ fragile : vérif SQL recommandée)<br>• **Client** : **vérif déterministe obligatoire** (le panel 2 sur 3 produit un faux consensus à 119 410 sur `C10`, § 2.2)<br>• **Paiement** : vérif déterministe + revue humaine | 1. Basculer sur `openai/gpt-oss-20b#groq` (0 USD, 1/1 sur `C10`, avec politique de retry sur limite TPM).<br>2. Si quota Groq épuisé et requête différable : **`defer`**.<br>3. Si urgent et budget autorisé : `openai/gpt-oss-120b#openrouter` (0,15 / 0,60 USD/1M). *Exclure Qwen, Cohere et Dots (0/1).*<br>4. Sinon : **`abstain`**. |
| **F3 – Liste de produits**<br>`C03, C12, C13, C14` (4 cas) | • `gpt-oss-120b` : **4/4 (100 %)**<br>• `gpt-oss-20b` : **4/4 (100 %)**<br>• `cohere/north-mini-code:free` : **4/4 (100 %)**<br>• `qwen3.8-27b` : **4/4 (100 %)**<br>• `dots-3-note-preview:free` : **4/4 (100 %)** | `openai/gpt-oss-20b#groq` (gratuit, 0 USD, G5, 4/4 sur `C03, C12–C14`) | • **Interne** : `none` (format seul, 100 % au TD 1)<br>• **Client** : quorum **2 sur 3** (panel fixe) ou vérif déterministe<br>• **Paiement** : quorum **3 sur 5** + vérif déterministe / revue humaine | 1. Passer au modèle gratuit suivant à 100 % sur un autre fournisseur (`cohere/north-mini-code:free#openrouter` ou `qwen/qwen3.8-27b#groq`, 0 USD).<br>2. Si quotas gratuits épuisés et requête différable : **`defer`**.<br>3. Si urgent et budget autorisé : `openai/gpt-oss-120b#openrouter` (0,15 / 0,60 USD/1M).<br>4. Sinon : **`abstain`**. |
| **Combinaisons**<br>`C15, C16, C17, C18, C19` (5 cas) | • `gpt-oss-120b` : **5/5 (100 %)**<br>• `gpt-oss-20b` : **5/5 (100 %)** (`C19` réussi au 2e essai)<br>• `cohere/north-mini-code:free` : **2/5 (40 %)** (`C16, C18` ok)<br>• `qwen3.8-27b` : **2/5 (40 %)** (`C16, C18` ok)<br>• `dots-3-note-preview:free` : **2/5 (40 %)** (`C16, C19` ok) | `openai/gpt-oss-120b#groq` (gratuit, 0 USD, G5, 5/5 au 1er essai sur `C15–C19`) | • **Interne** : `none` admissible uniquement avec `gpt-oss-120b` ou `gpt-oss-20b` (5/5 au TD 1)<br>• **Client** : **vérif déterministe obligatoire** (Cohere et Qwen échouent sur `C15, C17, C19`, donc le 2 sur 3 échoue)<br>• **Paiement** : vérif déterministe + revue humaine | 1. Basculer sur `openai/gpt-oss-20b#groq` (0 USD, 5/5, avec retry si limite TPM).<br>2. Si quota Groq épuisé et requête différable : **`defer`**.<br>3. Si urgent et budget autorisé : `openai/gpt-oss-120b#openrouter` (0,15 / 0,60 USD/1M). *Exclure Cohere, Qwen et Dots (40 %).*<br>4. Sinon : **`abstain`**. |

