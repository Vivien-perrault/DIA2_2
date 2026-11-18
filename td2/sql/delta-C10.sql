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
