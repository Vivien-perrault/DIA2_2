-- DEMO-SQL-C11, cas historique rejoué (lot pilote de septembre 2026, pas notre lot TD1)
-- Requête M1, openai/gpt-oss-20b (Groq), telle que fournie dans l'énoncé TD2
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date = '2001-12-01';
