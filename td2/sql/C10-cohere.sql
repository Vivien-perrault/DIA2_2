SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE CAST(strftime('%Y', o.date) - strftime('%Y', c.birth_date) AS INTEGER) = 25
  AND CAST(strftime('%m-%d', o.date) >= CAST(strftime('%m-%d', c.birth_date) AS TEXT) AS INTEGER) = 1;