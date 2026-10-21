SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o JOIN product p ON o.product_id = p.product_id
WHERE o.product_id IN ('a', 'b', 'c')
  AND o.date >= '2026-10-01 00:00:00'
  AND o.date < '2026-12-01 00:00:00'
