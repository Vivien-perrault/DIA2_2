# Plan de travail – TD2 Étape 2 : le faux consensus

## Comment utiliser ce plan (à lire en premier, humain ou Claude Code)

1. `git pull` avant de commencer.
2. Chercher la **première étape non cochée** (`- [ ]`) dans la section « Étapes ». **Faire uniquement celle-là.**
3. Tout le contexte nécessaire est dans ce fichier : relire la section « Contexte » et les « Résultats déjà acquis ».
4. Une fois l'étape faite :
   - la cocher (`- [x]`) et ajouter `— fait par <prénom> le <date>` ;
   - reporter les chiffres et faits nouveaux dans « Résultats déjà acquis » pour que la personne suivante les ait ;
   - écrire la partie correspondante du rapport dans `td2/reports/td2.md` ;
   - faire un commit `td2 étape 2.<n> : <résumé>` puis un `git push` (si le push échoue, faire `git pull --rebase` puis repousser).
5. Ne pas commencer l'étape suivante : c'est le tour du membre suivant (rotation Nazim → Personne 2 → Personne 3 → Nazim …).

## Contexte

### Consigne (énoncé TD2, Step 2, résumé)

Chercher dans **toutes** les traces TD1 (les **5** modèles, pas seulement les 3 du panel) un cas où **au moins deux modèles renvoient la même valeur fausse** (verdict `incorrect`, même valeur). Déclarer le panel et le seuil k sur n, puis montrer si cette valeur fausse **gagne le panel fixe 2 sur 3**, **gagne le quorum 3 sur 5** ou est **mise en minorité**. L'analyse va dans le rapport et porte sur un cas SQL exécuté sur `boutique.sqlite`. On utilise notre propre cas si on en a un ; sinon le cas historique DEMO-SQL-C11.

Trois preuves sont exigées :
1. **Identification et verdict des quorums** : identifiant de la question, modèles d'accord, valeur fausse partagée, valeur de référence indépendante (`reference-td1.csv`), résultat des votes 2 sur 3 et 3 sur 5.
2. **Diagnostic de la clause SQL fautive** : les deux requêtes complètes et l'explication exacte de la condition `WHERE` ou `JOIN` qui produit la valeur fausse.
3. **Requête delta de diagnostic** sur `boutique.sqlite` : un `SELECT` exécuté qui liste les `customer_id` (et leur CA HT de commandes) comptés par la référence mais manqués (ou ajoutés à tort) par les requêtes fautives. La somme doit expliquer **l'écart exact en centimes** entre la valeur fausse et la référence.

Livrable : un cas expliqué avec identifiant, source et nature, modèles d'accord, référence, résultats 2 sur 3 et 3 sur 5 déclarés, cause SQL, requête delta exécutée et méthode de vérification indépendante.

Énoncé complet : `td2/enonce-td2-en.md` (section « Step 2 »).

### Fichiers

| Fichier | Rôle |
|---|---|
| `td1/traces-td1.csv` | 102 lignes de traces TD1 (5 modèles × 20 questions, plus 2 relances de gpt-oss-20b). Colonnes utiles : `provider`, `model_requested`, `case_id`, `sql`, `value`, `reference`, `verdict`, `nature`. Les champs `sql` sont multilignes : lire le fichier avec `csv.DictReader` et non avec `cut`/`grep`. Garder la **dernière** ligne par (modèle, question). |
| `td1/reference-td1.csv` | Nos requêtes de référence (`case_id, sql, revenue_cents, checked_by`). |
| `td1/data/boutique.sqlite` | La base. Tables : `orders` (`customer_id`, `product_id`, `quantity_product`, `date`), `product` (`product_id`, `price`), `customers` (`customer_id`, `birth_date`…). CA HT = `SUM(o.quantity_product * p.price)` en centimes. |
| `td2/atelier-vote.py` | Panel fixe 2 sur 3 : `groq openai/gpt-oss-120b`, `openrouter cohere/north-mini-code:free`, `groq qwen/qwen3.8-27b`. Il importe `vote_k_sur_n` depuis `td1/skeleton-multi-llm-en.py`. |
| `td2/reports/td2.md` | **Le rapport** : chaque étape y ajoute sa section. |
| `td2/sql/` | Les scripts et requêtes SQL produits pendant l'étape 2. |

Les 5 modèles TD1 : `openai/gpt-oss-120b` (Groq), `openai/gpt-oss-20b` (Groq), `cohere/north-mini-code:free` (OpenRouter), `qwen/qwen3.8-27b` (Groq), `dots-studio/dots-3-note-preview:free` (OpenRouter). gpt-oss-20b et Dots **ne sont pas** dans le panel fixe.

## Résultats déjà acquis

- **Valeurs fausses partagées trouvées dans nos traces** (dernière tentative par modèle, verdict `incorrect`). On n'a donc **pas besoin** de DEMO-SQL-C11 :

  | Question | gpt-oss-120b | gpt-oss-20b | cohere north-mini | qwen3.8-27b | dots-3-note | Référence |
  |---|---|---|---|---|---|---|
  | **C10** | 558980 ✔ | 558980 ✔ | **119410 ✘** | **119410 ✘** | (sql_invalid) | 558980 |
  | C02 | 590320 ✔ | **0 ✘** | **0 ✘** | 590320 ✔ | **0 ✘** | 590320 |
  | C08 | 605580 ✔ | 605580 ✔ | **0 ✘** | 605580 ✔ | **0 ✘** | 605580 |

- **Cas principal proposé : C10.** Les deux modèles fautifs sont dans le panel fixe, donc 119410 devrait gagner le vote 2 sur 3. Sur les 5 modèles, c'est 2 contre 2 et Dots ne vote pas, donc pas de quorum 3 sur 5 (compté à la main, à confirmer aux étapes 3 et 4). Écart à expliquer : 558980 − 119410 = **439570 centimes**.
- **C02 en contre-exemple** : 0 obtient 3 voix sur 5 et gagne le vote 3 sur 5, alors que le panel 2 sur 3 donne la bonne valeur 590320.
- **DEMO-VOTE fait** (étape 1) : `>` donne 0, `>=` donne 100, propositions `[0, 0, 100]`, le vote 2 sur 3 renvoie 0 alors que la référence vaut 100, donc faux consensus. Script `td2/sql/demo-vote.py`, section 2.0 du rapport.

- **Confirmation dans les traces (étape 2)**. Les 102 lignes donnent 100 dernières tentatives distinctes sur 20 questions et 5 modèles. C02, C08 et C10 sont les seuls cas avec une valeur incorrecte partagée. C10 est retenu. Sa référence indépendante est de 558980 centimes (`checked_by` = Akihito Raffin). Les cinq `cell_id` figurent dans la section 2.1 du rapport.

- **Quorums confirmés par exécution (étapes 3 et 4)**. C10 donne un faux consensus à 119410 centimes en 2 sur 3, puis aucun quorum en 3 sur 5 (2 voix à 119410, 2 à 558980, Dots sans vote). C02 donne le résultat correct de 590320 centimes en 2 sur 3, puis un faux consensus à 0 en 3 sur 5. Voir les sections 2.2 et 2.3 du rapport.

- **Diagnostic SQL confirmé (étapes 5 et 6)**. Les trois requêtes C10 exécutées sur `boutique.sqlite` donnent 119410 (Cohere), 119410 (Qwen) et 558980 (référence), en centimes. Les deux modèles omettent les commandes de l’année du 26e anniversaire passées avant celui-ci. La seconde branche de Qwen cible un âge de 23 ans et sélectionne zéro ligne dans cette base. Voir les sections 2.4 et 2.5 du rapport.

- **Delta vérifié (étapes 7 et 8)**. Pour chaque modèle, les mêmes quatre clients expliquent les 439570 centimes manquants : C004 (150260), C005 (150240), C007 (118740) et C022 (20330). Aucun CA HT n’a été ajouté à tort. Baptiste a confirmé les montants par un calcul Python sur les trois CSV source. Voir le [SQL](td2/sql/delta-C10.sql) et la section 2.6 du rapport.

- **DEMO-SQL-C11 rejoué (étape 9)**. M1 et M2 renvoient 0 sur `boutique.sqlite` ; la référence C11 vaut 446690 (`checked_by` = Chandra R S SUKUMAR). M1 teste un seul jour (`birth_date = '2001-12-01'`, aucun client), M2 une fenêtre vide (`<= 2026-12-01` et `>= 2027-12-01`). Fenêtre correcte : `2000-12-02 <= birth_date <= 2001-12-01`. La requête `td2/sql/delta-C11.sql` liste 6 clients (C001, C002, C003, C006, C008, C009) pour 446690 centimes, soit tout l'écart. Dans notre lot, seul Cohere renvoie 0 sur C11 : c'est une erreur isolée, pas un faux consensus. Voir la section 2.7 du rapport.

## Étapes

### Partie 0 – Mécanisme (exemple jouet, pas un cas d'analyse)

- [x] **Étape 1 – DEMO-VOTE** — fait par Nazim le 2026-11-18
  Table jouet d'une ligne (2026-01-01, 100 centimes). Comparer `sale_date > '2026-01-01'` et `>=`, avec la borne `< '2026-01-02'`. Expliquer la borne, puis le vote `[0, 0, 100]` en 2 sur 3 face à la référence 100. Le marquer comme exemple construit.

### Partie A – Identification et verdict des quorums

- [x] **Étape 2 – Confirmer le cas dans les traces** — fait par Baptiste le 2026-11-18
  Relire `td1/traces-td1.csv` sur les 5 modèles (dernière tentative par modèle) et vérifier le tableau des « Résultats déjà acquis ». Valider C10 comme cas principal, ou argumenter un autre choix. Noter dans le rapport (section 2.1) : identifiant, modèles d'accord, valeur fausse, référence (`td1/reference-td1.csv`, colonne `checked_by` comprise), nature `real` (exécuté pendant notre TD1). Ajouter les `cell_id` concernés.

- [x] **Étape 3 – Quorum 2 sur 3 (panel fixe)** — fait par Baptiste le 2026-11-18
  Déclarer n = 3 (les 3 modèles de `td2/atelier-vote.py`) et k = 2. Lancer `python td2/atelier-vote.py`, ou appeler `vote_k_sur_n` sur C10 (et C02). Noter consensus, valeur et votes, puis comparer à la référence.

- [x] **Étape 4 – Quorum 3 sur 5 (les 5 modèles TD1)** — fait par Baptiste le 2026-11-18
  Déclarer n = 5 et k = 3. Une cellule `sql_invalid` ou une valeur vide ne compte pas comme un vote. Pour C10 et C02 : la valeur fausse gagne-t-elle, est-elle mise en minorité, ou n'y a-t-il pas de quorum ? Tableau récapitulatif `question | 2 sur 3 | 3 sur 5 | référence` dans le rapport.

### Partie B – Diagnostic de la clause SQL fautive

- [x] **Étape 5 – Récupérer et exécuter les requêtes** — fait par Baptiste le 2026-11-18
  Extraire de `traces-td1.csv` les **requêtes complètes** de cohere north-mini et qwen3.8-27b sur C10, ainsi que notre référence. Les sauvegarder dans `td2/sql/C10-cohere.sql`, `C10-qwen.sql` et `C10-reference.sql`. Les exécuter sur `td1/data/boutique.sqlite` et vérifier qu'on retrouve 119410 / 119410 / 558980.

- [x] **Étape 6 – Expliquer la condition WHERE / JOIN fautive** — fait par Baptiste le 2026-11-18
  Comparer chaque requête clause par clause avec la référence. Quelle condition `WHERE`/`JOIN` réduit le résultat ? Expliquer **quelle fenêtre ou quel ensemble de lignes** chaque requête teste réellement, face à ce que demande la question. Les deux modèles font-ils la **même** erreur, ou deux erreurs différentes qui tombent sur la même valeur ?

### Partie C – Requête delta de diagnostic

- [x] **Étape 7 – Écrire et exécuter la requête delta** — fait par Baptiste le 2026-11-18
  `SELECT` sur `boutique.sqlite` qui liste les `customer_id` et leur CA HT comptés par la référence mais manqués (ou ajoutés à tort) par les requêtes fautives. Piste : ensemble des lignes de la référence `EXCEPT` celui de la requête fautive, puis `GROUP BY customer_id`. Fichier `td2/sql/delta-C10.sql`, sortie collée dans le rapport.

- [x] **Étape 8 – Vérifier que le delta explique tout l'écart** — fait par Baptiste le 2026-11-18
  `SUM(delta)` doit valoir exactement **439570** centimes (558980 − 119410). Ajouter une méthode de vérification indépendante : requête réécrite à la main, ou calcul Python sur les lignes brutes. Noter qui a vérifié.

### Partie D – Cas historique DEMO-SQL-C11 (facultatif)

- [x] **Étape 9 – C11 en complément** — fait par Nazim le 2026-11-18
  Exécuter M1 et M2 (texte complet dans `td2/enonce-td2-en.md`) : les deux renvoient 0. M1 teste seulement `birth_date = '2001-12-01'`. M2 exige `birth_date <= '2026-12-01'` **et** `birth_date >= '2027-12-01'`, une fenêtre vide. La fenêtre correcte pour « exactement 25 ans au 2026-12-01 » est `'2000-12-02' <= birth_date <= '2001-12-01'`. Écrire la requête qui liste ces clients et leur CA ; la somme doit égaler notre référence C11. Le marquer comme **cas historique rejoué**.

### Partie E – Rédaction

- [ ] **Étape 10 – Finaliser la section dans `td2/reports/td2.md`**
  Vérifier que le livrable contient : identifiant, source et nature, modèles d'accord, référence, résultats 2 sur 3 et 3 sur 5, cause SQL, requête delta exécutée avec sa sortie, méthode de vérification indépendante, liens vers les traces et les fichiers SQL.

- [ ] **Étape 11 – Relecture croisée**
  Relancer chaque requête citée et vérifier chaque chiffre du rapport. Vérifier que DEMO-VOTE (et C11 s'il est fait) sont bien étiquetés comme exemple construit ou rejoué.

- [ ] **Étape 12 – Contributions et commit final**
  Ajouter la contribution de chaque membre pour l'étape 2 dans le rapport, puis commit et push.
