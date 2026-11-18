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
