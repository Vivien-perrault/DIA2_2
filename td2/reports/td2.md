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
