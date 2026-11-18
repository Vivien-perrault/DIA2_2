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
