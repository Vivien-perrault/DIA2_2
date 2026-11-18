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