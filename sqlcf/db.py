"""Seeded retail database generator (sizes S/M/L) and business-rule assertions.

Rows live in a plain dict {table: list[tuple]} so counterfactual edits (cf.py) can
operate on Python data and every written DB is re-checked with `check_rules`.
Money is INTEGER rupees so SUMs are exact in SQLite and pandas.
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

SIZES = {"S": 50, "M": 500, "L": 5000}
CITIES = ["Delhi", "Mumbai", "Pune", "Jaipur", "Kochi", "Indore", "Surat", "Nagpur"]
CATEGORIES = ["books", "electronics", "grocery", "toys", "apparel", "home"]
TIERS = ["bronze", "silver", "gold"]
YEARS = [2024, 2025]
END = date(2025, 12, 31)
_FIRST = "Aarav Diya Kabir Meera Rohan Isha Vivaan Anaya Arjun Sara Reyansh Myra Ishaan Kiara Aditya Tara".split()
_LAST = "Sharma Iyer Khan Patel Reddy Das Nair Gupta Singh Mehta Bose Rao".split()

SCHEMA = """
CREATE TABLE customers(customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL, signup_date TEXT NOT NULL);
CREATE TABLE products(product_id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, list_price INTEGER NOT NULL);
CREATE TABLE orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(customer_id), order_date TEXT NOT NULL, status TEXT NOT NULL CHECK (status IN ('placed','shipped','cancelled')));
CREATE TABLE order_items(order_item_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(order_id), product_id INTEGER NOT NULL REFERENCES products(product_id), quantity INTEGER NOT NULL, unit_price INTEGER NOT NULL);
CREATE TABLE payments(payment_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(order_id), amount INTEGER NOT NULL, paid_date TEXT NOT NULL);
CREATE TABLE refunds(refund_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(order_id), amount INTEGER NOT NULL, refund_date TEXT NOT NULL);
CREATE TABLE tier_history(tier_history_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(customer_id), tier TEXT NOT NULL, valid_from TEXT NOT NULL);
CREATE TABLE invoice_adjustments(adjustment_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(order_id), amount INTEGER NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE INDEX ix_orders_customer ON orders(customer_id);
CREATE INDEX ix_items_order ON order_items(order_id);
CREATE INDEX ix_payments_order ON payments(order_id);
CREATE INDEX ix_refunds_order ON refunds(order_id);
CREATE INDEX ix_tier_customer ON tier_history(customer_id);
CREATE INDEX ix_adj_order ON invoice_adjustments(order_id);
"""
TABLES = ["customers", "products", "orders", "order_items", "payments", "refunds",
          "tier_history", "invoice_adjustments"]

# Shown to the agent in its system prompt; templates follow these definitions.
GLOSSARY = """\
- An order is *active* unless its status is 'cancelled'. Only shipped orders are paid; placed orders are not paid yet.
- Gross revenue = sum of quantity * unit_price over the items of active orders.
- Net revenue = gross revenue minus refunds on those orders.
- A customer's current tier is their tier_history row with the latest valid_from.
- The net invoice amount of an order = its item total plus the sum of its invoice_adjustments.
- "In <year>" refers to order_date unless the question says otherwise."""


def _d(x: date) -> str:
    return x.isoformat()


def _rand_date(rng: random.Random, lo: date, hi: date) -> date:
    return lo + timedelta(days=rng.randint(0, max(0, (hi - lo).days)))


def _split(rng: random.Random, total: int, parts: int) -> list[int]:
    """Split a positive int into `parts` positive ints (parts <= total)."""
    cuts = sorted(rng.sample(range(1, total), parts - 1))
    return [b - a for a, b in zip([0] + cuts, cuts + [total])]


def add_order(rows: dict, rng: random.Random, customer_id: int, signup: str, status: str,
              products: list[tuple], ids: dict, year: int | None = None, must: tuple | None = None) -> None:
    """Append one consistent order (items, payments, adjustments, refunds) to rows.
    year: date the order inside that year; must: product that must be one of the lines."""
    lo = max(date.fromisoformat(signup), date(year or 2024, 1, 1))
    hi = date(year, 12, 31) if year else END
    if lo > hi:
        return
    od = _rand_date(rng, lo, hi)
    oid = ids["orders"] = ids["orders"] + 1
    rows["orders"].append((oid, customer_id, _d(od), status))
    total = 0
    picks = rng.sample(products, rng.choice([1, 1, 2, 2, 3, 4]))
    if must is not None and must not in picks:
        picks[0] = must
    for p in picks:
        qty = rng.choice([1, 1, 1, 2, 2, 3])
        price = p[3] if rng.random() < 0.7 else p[3] * 9 // 10
        iid = ids["order_items"] = ids["order_items"] + 1
        rows["order_items"].append((iid, oid, p[0], qty, price))
        total += qty * price
    if status != "shipped":
        return
    if rng.random() < 0.1:
        adj = rng.choice([-1, 1]) * max(1, total * rng.randint(1, 8) // 100)
        aid = ids["invoice_adjustments"] = ids["invoice_adjustments"] + 1
        rows["invoice_adjustments"].append((aid, oid, adj, "discount" if adj < 0 else "correction", _d(od)))
        total += adj
    n = 1 if total < 3 or rng.random() < 0.75 else rng.choice([2, 2, 3])
    for amt in _split(rng, total, n):
        pid = ids["payments"] = ids["payments"] + 1
        rows["payments"].append((pid, oid, amt, _d(_rand_date(rng, od, min(END, od + timedelta(days=60))))))
    if rng.random() < 0.12:
        rid = ids["refunds"] = ids["refunds"] + 1
        rows["refunds"].append((rid, oid, rng.randint(1, total), _d(_rand_date(rng, od, END))))


def add_customer(rows: dict, rng: random.Random, ids: dict, signup_hi: date = date(2024, 12, 31),
                 city: str | None = None) -> tuple:
    cid = ids["customers"] = ids["customers"] + 1
    signup = _rand_date(rng, date(2023, 1, 1), signup_hi)
    c = (cid, f"{rng.choice(_FIRST)} {rng.choice(_LAST)}", rng.choice(CITIES), _d(signup))
    if city:
        c = c[:2] + (city,) + c[3:]
    rows["customers"].append(c)
    tier, when = rng.choice(TIERS[:2]), signup
    for k in range(rng.choice([1, 1, 2, 3])):
        if k:
            when = _rand_date(rng, when + timedelta(days=1), END)
            if when >= END:
                break
            tier = rng.choice([t for t in TIERS if t != tier])
        tid = ids["tier_history"] = ids["tier_history"] + 1
        rows["tier_history"].append((tid, cid, tier, _d(when)))
    return c


def generate(size: str, seed: int) -> dict:
    rng = random.Random(seed)
    n = SIZES[size]
    rows = {t: [] for t in TABLES}
    ids = {t: 0 for t in TABLES}
    for pid in range(1, max(20, n // 10) + 1):
        cat = rng.choice(CATEGORIES)
        rows["products"].append((pid, f"{cat}-{pid:04d}", cat, rng.randint(5, 500) * 10))
    ids["products"] = len(rows["products"])
    for _ in range(n):
        c = add_customer(rows, rng, ids)
        for _ in range(rng.choices([0, 1, 2, 3, 4, 5], [15, 25, 25, 15, 12, 8])[0]):
            st = rng.choices(["shipped", "placed", "cancelled"], [65, 20, 15])[0]
            add_order(rows, rng, c[0], c[3], st, rows["products"], ids)
    return rows


def next_ids(rows: dict) -> dict:
    return {t: max((r[0] for r in rows[t]), default=0) for t in TABLES}


def write(rows: dict, path: Path, insert_seed: int | None = None) -> Path:
    """Write rows to a fresh SQLite file; optionally shuffle insert order per table."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    rng = random.Random(insert_seed)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    for t in TABLES:
        data = list(rows[t])
        if insert_seed is not None:
            rng.shuffle(data)
        if data:
            con.executemany(f"INSERT INTO {t} VALUES ({','.join('?' * len(data[0]))})", data)
    con.commit()
    bad = check_rules(con)
    con.close()
    if bad:
        raise AssertionError(f"{path.name}: business rules violated: {bad}")
    return path


_RULES = {
    "fk": "SELECT COUNT(*) FROM pragma_foreign_key_check",
    "order_without_items": "SELECT COUNT(*) FROM orders o WHERE NOT EXISTS (SELECT 1 FROM order_items i WHERE i.order_id=o.order_id)",
    "unshipped_paid_or_refunded": """SELECT COUNT(*) FROM orders o WHERE o.status<>'shipped' AND (
        EXISTS (SELECT 1 FROM payments p WHERE p.order_id=o.order_id) OR EXISTS (SELECT 1 FROM refunds r WHERE r.order_id=o.order_id)
        OR EXISTS (SELECT 1 FROM invoice_adjustments a WHERE a.order_id=o.order_id))""",
    "shipped_payment_mismatch": """SELECT COUNT(*) FROM orders o WHERE o.status='shipped' AND
        COALESCE((SELECT SUM(amount) FROM payments p WHERE p.order_id=o.order_id), 0) <>
        (SELECT SUM(quantity*unit_price) FROM order_items i WHERE i.order_id=o.order_id)
        + COALESCE((SELECT SUM(amount) FROM invoice_adjustments a WHERE a.order_id=o.order_id), 0)""",
    "refund_exceeds_paid": """SELECT COUNT(*) FROM orders o WHERE
        (SELECT COALESCE(SUM(amount),0) FROM refunds r WHERE r.order_id=o.order_id) >
        (SELECT COALESCE(SUM(amount),0) FROM payments p WHERE p.order_id=o.order_id)""",
    "nonpositive_amounts": """SELECT (SELECT COUNT(*) FROM order_items WHERE quantity<=0 OR unit_price<=0)
        + (SELECT COUNT(*) FROM payments WHERE amount<=0) + (SELECT COUNT(*) FROM refunds WHERE amount<=0)""",
    "tier_first_not_signup": """SELECT COUNT(*) FROM customers c WHERE
        (SELECT MIN(valid_from) FROM tier_history t WHERE t.customer_id=c.customer_id) IS NOT c.signup_date""",
    "tier_dup_valid_from": "SELECT COUNT(*) FROM (SELECT 1 FROM tier_history GROUP BY customer_id, valid_from HAVING COUNT(*)>1)",
    "order_before_signup": "SELECT COUNT(*) FROM orders o JOIN customers c USING(customer_id) WHERE o.order_date < c.signup_date",
    "payment_or_refund_before_order": """SELECT (SELECT COUNT(*) FROM payments p JOIN orders o USING(order_id) WHERE p.paid_date < o.order_date)
        + (SELECT COUNT(*) FROM refunds r JOIN orders o USING(order_id) WHERE r.refund_date < o.order_date)""",
}


def check_rules(con: sqlite3.Connection) -> dict:
    """Return {rule: violation_count} for every violated business rule (empty = valid)."""
    out = {k: con.execute(q).fetchone()[0] for k, q in _RULES.items()}
    return {k: v for k, v in out.items() if v}


if __name__ == "__main__":
    import sys, tempfile
    with tempfile.TemporaryDirectory() as d:
        for size in "SML":
            r = generate(size, 1)
            assert generate(size, 1) == r, "generator not deterministic"
            write(r, Path(d) / f"{size}.db", insert_seed=7)
            print(size, {t: len(v) for t, v in r.items()}, file=sys.stderr)
    print("db.py self-check ok")
