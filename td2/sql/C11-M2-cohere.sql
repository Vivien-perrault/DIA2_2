-- DEMO-SQL-C11, cas historique rejoué (lot pilote de septembre 2026, pas notre lot TD1)
-- Requête M2, cohere/north-mini-code:free (OpenRouter), telle que fournie dans l'énoncé TD2
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE CAST(strftime('%Y-%m-%d', '2026-12-01') AS TEXT) >= c.birth_date
  AND CAST(strftime('%Y-%m-%d', '2026-12-01', '+1 year') AS TEXT) <= c.birth_date;
