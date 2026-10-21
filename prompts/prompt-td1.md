# Prompt used in TD 1

The prompt is the one in `skeleton-multi-llm-en.py` (`SYSTEM_PROMPT`, `USER_PROMPT_TEMPLATE`), **unchanged from the kit**: the file's SHA-256 matches `manifest.json`. It was identical for all five models. `{schema}` is replaced by the content of [`schema.sql`](../schema.sql), and `{question}` by the text of the question in `questions-td1.json`.

The fingerprint `prompt_sha256` in each trace is the SHA-256 of `SYSTEM_PROMPT + "\n" + user message`. There is one fingerprint per question, the same for all five models (20 distinct fingerprints in `traces-td1.csv`). We recomputed the 20 fingerprints from this text, `schema.sql` and `questions-td1.json`: all 20 match the traces.

## System message (verbatim)

````text
You write SQLite queries for a small e-commerce database. Reply with exactly one SQLite SELECT statement and nothing else: no explanation, no comments, no markdown other than an optional ```sql fence.
````

## User message template (verbatim)

```text
Schema (SQLite):
{schema}

Conventions (binding):
- product.price is the unit price in euro cents, excluding VAT (an integer). Revenue excluding VAT is SUM(quantity_product * price), an integer number of cents.
- orders holds order lines: one row per (order_id, product_id). All lines of an order share the same customer_id and the same date.
- orders.date and customers.insert_date are UTC timestamps stored as text 'YYYY-MM-DD HH:MM:SS'. customers.birth_date is a date stored as text 'YYYY-MM-DD'. Compare them as text or with SQLite date functions.
- A period "from S to E" is closed on the left and open on the right: date >= S AND date < E.
- A customer's age on a day D is the number of completed years: someone born on B is N years old on D when the N-th anniversary of B is on or before D and the (N+1)-th anniversary is after D. "Exactly 25 years old" means completed age 25 on that day, computed from month and day, never from the year difference alone.
- Unless the question says "at the time of the order", ages are computed on the reference date given in the question.
- The query must return exactly one row and one column named revenue_cents. When no order line matches, return 0 (use COALESCE), not NULL.
- Use only the tables above. One SELECT statement, nothing else.

Question: {question}
```

## Schema inserted in `{schema}` (`schema.sql`)

```sql
-- Prototype orchestrator, ESILV "Next-Generation AI" (task 1572).
-- Three tables, exactly as specified. Prices are euro cents excluding VAT.
-- orders.date and customers.insert_date: UTC timestamps 'YYYY-MM-DD HH:MM:SS'.
-- customers.birth_date: date 'YYYY-MM-DD'.
CREATE TABLE product (
    product_id TEXT PRIMARY KEY,
    price INTEGER NOT NULL CHECK (price >= 0)
);
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    insert_date TEXT NOT NULL,
    birth_date TEXT NOT NULL
);
CREATE TABLE orders (
    date TEXT NOT NULL,
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    product_id TEXT NOT NULL REFERENCES product(product_id),
    quantity_product INTEGER NOT NULL CHECK (quantity_product > 0),
    PRIMARY KEY (order_id, product_id)
);
```
