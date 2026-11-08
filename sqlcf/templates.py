"""Question templates for four bug families.

Each template: NL question variants, gold SQL, paraphrased-gold SQL (FN probes),
named bug mutants (FP probes), an independent pandas implementation (gold checker),
and the parameter names it is instantiated over.

F1 duplicate-sensitive counts | F2 join fan-out | F3 missing business filters
F4 superseded/corrected records (held out: test split only)
"""
import itertools
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from .db import CATEGORIES, CITIES, TIERS, YEARS

VOCAB = {"city": CITIES, "year": YEARS, "category": CATEGORIES, "tier": TIERS}


@dataclass
class Template:
    id: str
    family: str
    split: str  # train | test
    questions: list[str]
    sql: str
    paraphrases: list[str]
    mutants: dict[str, str]
    pandas: Callable[[dict, dict], list[tuple]]
    params: list[str]
    ordered: bool = False
    nondeterministic_paraphrases: list[str] = field(default_factory=list)  # tie probes only

    def grid(self):
        for vals in itertools.product(*(VOCAB[p] for p in self.params)):
            yield dict(zip(self.params, vals))


# ---------- pandas helpers (independent of the SQL) ----------
def _y(s, y):
    return s.astype(str).str[:4] == str(y)


def _iv(T):
    i = T["order_items"]
    return i.assign(v=i.quantity * i.unit_price)


def _cust(T, city):
    c = T["customers"]
    return c.loc[c.city == city, "customer_id"]


def _sum(s):
    return None if len(s) == 0 else int(s.sum())  # SQL SUM over no rows is NULL


def _ids(s):
    return [(int(v),) for v in pd.unique(s)]


def _cur_tier(T):
    return T["tier_history"].sort_values("valid_from").groupby("customer_id").tail(1)


def _io(T):  # items with order columns
    return _iv(T).merge(T["orders"], on="order_id")


def _iop(T):  # items with order + product columns
    return _io(T).merge(T["products"], on="product_id")


def _active(df):
    return df.status != "cancelled"


# ---------- pandas implementations ----------
def pd_f1_ordered_customers(T, p):
    o = T["orders"]
    return [(o[o.customer_id.isin(_cust(T, p["city"]))].customer_id.nunique(),)]


def pd_f1_products_sold(T, p):
    m = _iop(T)
    return [(m[(m.category == p["category"]) & _y(m.order_date, p["year"])].product_id.nunique(),)]


def pd_f1_customer_list(T, p):
    m = _iop(T)
    return _ids(m[(m.category == p["category"]) & m.customer_id.isin(_cust(T, p["city"]))].customer_id)


def pd_f1_paying_customers(T, p):
    m = T["payments"].merge(T["orders"], on="order_id")
    return [(m[_y(m.paid_date, p["year"]) & m.customer_id.isin(_cust(T, p["city"]))].customer_id.nunique(),)]


def pd_f1_category_buyers(T, p):
    m = _iop(T)
    return [(m[(m.category == p["category"]) & _y(m.order_date, p["year"])].customer_id.nunique(),)]


def pd_f2_paid_for_category(T, p):
    m = _iop(T)
    ids = m[(m.category == p["category"]) & _y(m.order_date, p["year"])].order_id
    pay = T["payments"]
    return [(_sum(pay[pay.order_id.isin(ids)].amount),)]


def pd_f2_item_value_paid(T, p):
    m = _io(T)
    m = m[m.customer_id.isin(_cust(T, p["city"])) & _y(m.order_date, p["year"])
          & m.order_id.isin(T["payments"].order_id)]
    return [(_sum(m.v),)]


def pd_f2_refunded_category(T, p):
    m = _iop(T)
    r = T["refunds"]
    return [(_sum(r[r.order_id.isin(m[m.category == p["category"]].order_id)].amount),)]


def pd_f2_units_paid(T, p):
    pay = T["payments"]
    ids = pay[_y(pay.paid_date, p["year"])].order_id
    m = _iop(T)
    return [(_sum(m[(m.category == p["category"]) & m.order_id.isin(ids)].quantity),)]


def _gross_slice(T, p):
    m = _io(T)
    return m[_active(m) & m.customer_id.isin(_cust(T, p["city"])) & _y(m.order_date, p["year"])]


def pd_f3_gross_revenue(T, p):
    return [(_sum(_gross_slice(T, p).v),)]


def pd_f3_active_orders(T, p):
    o = T["orders"]
    return [(int((_active(o) & o.customer_id.isin(_cust(T, p["city"])) & _y(o.order_date, p["year"])).sum()),)]


def pd_f3_net_revenue(T, p):
    g = _sum(_gross_slice(T, p).v)
    if g is None:
        return [(None,)]
    o = T["orders"]
    ids = o[_active(o) & o.customer_id.isin(_cust(T, p["city"])) & _y(o.order_date, p["year"])].order_id
    r = T["refunds"]
    return [(g - int(r[r.order_id.isin(ids)].amount.sum()),)]


def pd_f3_top_customers(T, p):
    m = _io(T)
    m = m[_active(m) & m.customer_id.isin(_cust(T, p["city"]))]
    g = m.groupby("customer_id").v.sum().reset_index()
    g = g.sort_values(["v", "customer_id"], ascending=[False, True]).head(3)
    return [(int(a), int(b)) for a, b in zip(g.customer_id, g.v)]


def pd_f3_avg_order(T, p):
    s = _gross_slice(T, p).groupby("order_id").v.sum()
    return [(None if s.empty else float(s.mean()),)]


def _cur_in_city(T, p):
    c = _cur_tier(T)
    return c[(c.tier == p["tier"]) & c.customer_id.isin(_cust(T, p["city"]))]


def pd_f4_current_tier_count(T, p):
    return [(len(_cur_in_city(T, p)),)]


def pd_f4_current_tier_list(T, p):
    return _ids(_cur_in_city(T, p).customer_id)


def pd_f4_net_invoice(T, p):
    o = T["orders"]
    ids = o[(o.status == "shipped") & o.customer_id.isin(_cust(T, p["city"])) & _y(o.order_date, p["year"])].order_id
    i = _iv(T)
    items = _sum(i[i.order_id.isin(ids)].v)
    if items is None:
        return [(None,)]
    a = T["invoice_adjustments"]
    return [(items + int(a[a.order_id.isin(ids)].amount.sum()),)]


def pd_f4_revenue_by_current_tier(T, p):
    m = _gross_slice(T, p).merge(_cur_tier(T)[["customer_id", "tier"]], on="customer_id")
    g = m.groupby("tier").v.sum()
    return [(t, int(v)) for t, v in g.items()]


# ---------- SQL fragments ----------
IOP = ("FROM order_items oi JOIN orders o ON o.order_id = oi.order_id "
       "JOIN products p ON p.product_id = oi.product_id")
YR = "substr(o.order_date, 1, 4) = '{year}'"
CITY_JOIN = "JOIN customers c ON c.customer_id = o.customer_id"
LATEST = "t.valid_from = (SELECT MAX(t2.valid_from) FROM tier_history t2 WHERE t2.customer_id = t.customer_id)"
GROSS = (f"SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id "
         f"{CITY_JOIN} WHERE c.city = '{{city}}' AND {{status}} AND {YR}")
REFUNDS = (f"SELECT COALESCE(SUM(r.amount), 0) FROM refunds r JOIN orders o ON o.order_id = r.order_id "
           f"{CITY_JOIN} WHERE c.city = '{{city}}' AND {{status}} AND {YR}")
ACTIVE = "o.status <> 'cancelled'"


def _g(status):  # pre-fill the status slot, keep {city}/{year} for later .format
    return GROSS.replace("{status}", status), REFUNDS.replace("{status}", status)


TEMPLATES: list[Template] = [
    # ---------------- F1 duplicate-sensitive counts ----------------
    Template(
        "F1_ordered_customers", "F1", "train",
        ["How many distinct customers from {city} have placed at least one order (of any status)?",
         "Count the customers based in {city} who have ever placed an order, whatever its status."],
        f"SELECT COUNT(DISTINCT o.customer_id) FROM orders o {CITY_JOIN} WHERE c.city = '{{city}}'",
        ["SELECT COUNT(*) FROM customers c WHERE c.city = '{city}' AND EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)",
         "SELECT COUNT(*) FROM (SELECT DISTINCT customer_id FROM orders WHERE customer_id IN (SELECT customer_id FROM customers WHERE city = '{city}'))"],
        {"count_rows": f"SELECT COUNT(*) FROM orders o {CITY_JOIN} WHERE c.city = '{{city}}'",
         "all_customers": "SELECT COUNT(*) FROM customers WHERE city = '{city}'"},
        pd_f1_ordered_customers, ["city"]),
    Template(
        "F1_products_sold", "F1", "train",
        ["How many different {category} products were ordered in {year} (orders of any status)?",
         "In {year}, how many distinct products from the {category} category appeared in orders, counting every order status?"],
        f"SELECT COUNT(DISTINCT oi.product_id) {IOP} WHERE p.category = '{{category}}' AND {YR}",
        ["SELECT COUNT(*) FROM products p WHERE p.category = '{category}' AND p.product_id IN (SELECT oi.product_id FROM order_items oi JOIN orders o ON o.order_id = oi.order_id WHERE o.order_date LIKE '{year}-%')"],
        {"count_rows": f"SELECT COUNT(*) {IOP} WHERE p.category = '{{category}}' AND {YR}",
         "count_orders": f"SELECT COUNT(DISTINCT oi.order_id) {IOP} WHERE p.category = '{{category}}' AND {YR}"},
        pd_f1_products_sold, ["category", "year"]),
    Template(
        "F1_customer_list", "F1", "train",
        ["List the IDs of customers from {city} who have ordered at least one {category} product.",
         "Which customers (by customer_id) based in {city} have bought something from the {category} category?"],
        f"SELECT DISTINCT o.customer_id {IOP} {CITY_JOIN} WHERE c.city = '{{city}}' AND p.category = '{{category}}'",
        ["SELECT c.customer_id FROM customers c WHERE c.city = '{city}' AND EXISTS (SELECT 1 FROM orders o JOIN order_items oi ON oi.order_id = o.order_id JOIN products p ON p.product_id = oi.product_id WHERE o.customer_id = c.customer_id AND p.category = '{category}')",
         f"SELECT o.customer_id {IOP} {CITY_JOIN} WHERE c.city = '{{city}}' AND p.category = '{{category}}' GROUP BY o.customer_id"],
        {"no_distinct": f"SELECT o.customer_id {IOP} {CITY_JOIN} WHERE c.city = '{{city}}' AND p.category = '{{category}}'"},
        pd_f1_customer_list, ["city", "category"]),
    Template(
        "F1_paying_customers", "F1", "train",
        ["How many distinct customers from {city} made at least one payment in {year} (by payment date)?",
         "Count the customers in {city} who paid anything during {year}, using the payment date."],
        f"SELECT COUNT(DISTINCT o.customer_id) FROM payments pay JOIN orders o ON o.order_id = pay.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND substr(pay.paid_date, 1, 4) = '{{year}}'",
        ["SELECT COUNT(*) FROM customers c WHERE c.city = '{city}' AND EXISTS (SELECT 1 FROM payments pay JOIN orders o ON o.order_id = pay.order_id WHERE o.customer_id = c.customer_id AND pay.paid_date BETWEEN '{year}-01-01' AND '{year}-12-31')"],
        {"count_rows": f"SELECT COUNT(*) FROM payments pay JOIN orders o ON o.order_id = pay.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND substr(pay.paid_date, 1, 4) = '{{year}}'",
         "count_orders": f"SELECT COUNT(DISTINCT pay.order_id) FROM payments pay JOIN orders o ON o.order_id = pay.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND substr(pay.paid_date, 1, 4) = '{{year}}'"},
        pd_f1_paying_customers, ["city", "year"]),
    Template(
        "F1_category_buyers", "F1", "test",
        ["How many distinct customers bought a {category} product in {year}? Count orders of any status."],
        f"SELECT COUNT(DISTINCT o.customer_id) {IOP} WHERE p.category = '{{category}}' AND {YR}",
        ["SELECT COUNT(*) FROM customers c WHERE EXISTS (SELECT 1 FROM orders o JOIN order_items oi ON oi.order_id = o.order_id JOIN products p ON p.product_id = oi.product_id WHERE o.customer_id = c.customer_id AND p.category = '{category}' AND o.order_date LIKE '{year}-%')"],
        {"count_rows": f"SELECT COUNT(*) {IOP} WHERE p.category = '{{category}}' AND {YR}",
         "count_orders": f"SELECT COUNT(DISTINCT o.order_id) {IOP} WHERE p.category = '{{category}}' AND {YR}"},
        pd_f1_category_buyers, ["category", "year"]),

    # ---------------- F2 join fan-out ----------------
    Template(
        "F2_paid_for_category", "F2", "train",
        ["What is the total amount paid (sum of payments) for orders placed in {year} that contain at least one {category} product?",
         "Sum the payments received for {year} orders that include any {category} item."],
        f"SELECT SUM(pay.amount) FROM payments pay JOIN orders o ON o.order_id = pay.order_id WHERE {YR} AND pay.order_id IN (SELECT oi.order_id FROM order_items oi JOIN products p ON p.product_id = oi.product_id WHERE p.category = '{{category}}')",
        [f"SELECT SUM(pay.amount) FROM payments pay JOIN (SELECT DISTINCT oi.order_id {IOP} WHERE p.category = '{{category}}' AND o.order_date LIKE '{{year}}-%') x ON x.order_id = pay.order_id"],
        {"join_fanout": f"SELECT SUM(pay.amount) FROM payments pay JOIN orders o ON o.order_id = pay.order_id JOIN order_items oi ON oi.order_id = o.order_id JOIN products p ON p.product_id = oi.product_id WHERE {YR} AND p.category = '{{category}}'"},
        pd_f2_paid_for_category, ["category", "year"]),
    Template(
        "F2_item_value_paid", "F2", "train",
        ["What is the total item value (quantity × unit price) of orders placed in {year} by customers from {city} that have at least one payment?",
         "For customers in {city}, add up quantity times unit price over the items of their {year} orders that have received a payment."],
        f"SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND {YR} AND EXISTS (SELECT 1 FROM payments pay WHERE pay.order_id = o.order_id)",
        [f"SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND {YR} AND o.order_id IN (SELECT order_id FROM payments)"],
        {"join_fanout": f"SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id {CITY_JOIN} JOIN payments pay ON pay.order_id = o.order_id WHERE c.city = '{{city}}' AND {YR}"},
        pd_f2_item_value_paid, ["city", "year"]),
    Template(
        "F2_refunded_category", "F2", "train",
        ["What is the total refunded amount for orders that contain at least one {category} product?",
         "Add up all refunds issued on orders that include any {category} item."],
        "SELECT SUM(r.amount) FROM refunds r WHERE r.order_id IN (SELECT oi.order_id FROM order_items oi JOIN products p ON p.product_id = oi.product_id WHERE p.category = '{category}')",
        ["SELECT SUM(r.amount) FROM refunds r WHERE EXISTS (SELECT 1 FROM order_items oi JOIN products p ON p.product_id = oi.product_id WHERE oi.order_id = r.order_id AND p.category = '{category}')"],
        {"join_fanout": "SELECT SUM(r.amount) FROM refunds r JOIN order_items oi ON oi.order_id = r.order_id JOIN products p ON p.product_id = oi.product_id WHERE p.category = '{category}'"},
        pd_f2_refunded_category, ["category"]),
    Template(
        "F2_units_paid", "F2", "test",
        ["How many units of {category} products were in orders that received a payment in {year} (by payment date)?"],
        "SELECT SUM(oi.quantity) FROM order_items oi JOIN products p ON p.product_id = oi.product_id WHERE p.category = '{category}' AND oi.order_id IN (SELECT pay.order_id FROM payments pay WHERE substr(pay.paid_date, 1, 4) = '{year}')",
        ["SELECT SUM(oi.quantity) FROM order_items oi JOIN products p ON p.product_id = oi.product_id WHERE p.category = '{category}' AND EXISTS (SELECT 1 FROM payments pay WHERE pay.order_id = oi.order_id AND pay.paid_date LIKE '{year}-%')"],
        {"join_fanout": "SELECT SUM(oi.quantity) FROM order_items oi JOIN products p ON p.product_id = oi.product_id JOIN payments pay ON pay.order_id = oi.order_id WHERE p.category = '{category}' AND substr(pay.paid_date, 1, 4) = '{year}'"},
        pd_f2_units_paid, ["category", "year"]),

    # ---------------- F3 missing business filters ----------------
    Template(
        "F3_gross_revenue", "F3", "train",
        ["What was the gross revenue from customers in {city} in {year}?",
         "Compute {year} gross revenue for customers based in {city}."],
        _g(ACTIVE)[0],
        [_g("o.status IN ('placed', 'shipped')")[0]],
        {"no_status_filter": _g("1 = 1")[0], "shipped_only": _g("o.status = 'shipped'")[0]},
        pd_f3_gross_revenue, ["city", "year"]),
    Template(
        "F3_active_orders", "F3", "train",
        ["How many active orders did customers from {city} place in {year}?",
         "Count the {year} orders from {city} customers that are active."],
        f"SELECT COUNT(*) FROM orders o {CITY_JOIN} WHERE c.city = '{{city}}' AND {ACTIVE} AND {YR}",
        [f"SELECT COUNT(o.order_id) FROM orders o {CITY_JOIN} WHERE c.city = '{{city}}' AND o.status IN ('placed', 'shipped') AND o.order_date LIKE '{{year}}-%'"],
        {"no_status_filter": f"SELECT COUNT(*) FROM orders o {CITY_JOIN} WHERE c.city = '{{city}}' AND {YR}"},
        pd_f3_active_orders, ["city", "year"]),
    Template(
        "F3_net_revenue", "F3", "train",
        ["What was the net revenue from customers in {city} in {year}?",
         "Compute net revenue for {year} from customers based in {city}."],
        f"SELECT ({_g(ACTIVE)[0]}) - ({_g(ACTIVE)[1]})",
        [f"SELECT SUM(x.gross) - SUM(x.ref) FROM (SELECT o.order_id, (SELECT SUM(i.quantity * i.unit_price) FROM order_items i WHERE i.order_id = o.order_id) AS gross, (SELECT COALESCE(SUM(r.amount), 0) FROM refunds r WHERE r.order_id = o.order_id) AS ref FROM orders o {CITY_JOIN} WHERE c.city = '{{city}}' AND {ACTIVE} AND {YR}) x"],
        {"missing_refunds": _g(ACTIVE)[0],
         "no_status_filter": f"SELECT ({_g('1 = 1')[0]}) - ({_g('1 = 1')[1]})"},
        pd_f3_net_revenue, ["city", "year"]),
    Template(
        "F3_top_customers", "F3", "train",
        ["Who are the top 3 customers from {city} by gross revenue? Return customer_id and gross revenue, highest first.",
         "List the three {city} customers with the highest gross revenue (customer_id, revenue), in descending order of revenue."],
        f"SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue FROM orders o JOIN order_items oi ON oi.order_id = o.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND {ACTIVE} GROUP BY o.customer_id ORDER BY revenue DESC, o.customer_id LIMIT 3",
        [f"SELECT c.customer_id, SUM(oi.quantity * oi.unit_price) FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items oi ON oi.order_id = o.order_id WHERE c.city = '{{city}}' AND o.status IN ('placed', 'shipped') GROUP BY c.customer_id ORDER BY 2 DESC, 1 LIMIT 3"],
        {"no_status_filter": f"SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue FROM orders o JOIN order_items oi ON oi.order_id = o.order_id {CITY_JOIN} WHERE c.city = '{{city}}' GROUP BY o.customer_id ORDER BY revenue DESC, o.customer_id LIMIT 3"},
        pd_f3_top_customers, ["city"], ordered=True,
        nondeterministic_paraphrases=[f"SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue FROM orders o JOIN order_items oi ON oi.order_id = o.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND o.status IN ('placed', 'shipped') GROUP BY o.customer_id ORDER BY revenue DESC LIMIT 3"]),
    Template(
        "F3_avg_order", "F3", "test",
        ["What is the average gross value of active orders placed in {year} by customers in {city}? An order's gross value is the sum of quantity × unit price over its items."],
        f"SELECT AVG(t.v) FROM (SELECT o.order_id, SUM(oi.quantity * oi.unit_price) AS v FROM orders o JOIN order_items oi ON oi.order_id = o.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND {ACTIVE} AND {YR} GROUP BY o.order_id) t",
        [f"SELECT CAST(SUM(oi.quantity * oi.unit_price) AS REAL) / COUNT(DISTINCT o.order_id) FROM orders o JOIN order_items oi ON oi.order_id = o.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND o.status IN ('placed', 'shipped') AND {YR}"],
        {"no_status_filter": f"SELECT AVG(t.v) FROM (SELECT o.order_id, SUM(oi.quantity * oi.unit_price) AS v FROM orders o JOIN order_items oi ON oi.order_id = o.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND {YR} GROUP BY o.order_id) t",
         "item_level_avg": f"SELECT AVG(oi.quantity * oi.unit_price) FROM orders o JOIN order_items oi ON oi.order_id = o.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND {ACTIVE} AND {YR}"},
        pd_f3_avg_order, ["city", "year"]),

    # ---------------- F4 superseded / corrected records (held out) ----------------
    Template(
        "F4_current_tier_count", "F4", "test",
        ["How many customers from {city} are currently in the {tier} tier?"],
        f"SELECT COUNT(*) FROM tier_history t JOIN customers c ON c.customer_id = t.customer_id WHERE c.city = '{{city}}' AND t.tier = '{{tier}}' AND {LATEST}",
        ["SELECT COUNT(*) FROM (SELECT th.customer_id, th.tier, ROW_NUMBER() OVER (PARTITION BY th.customer_id ORDER BY th.valid_from DESC) AS rn FROM tier_history th) x JOIN customers c ON c.customer_id = x.customer_id WHERE x.rn = 1 AND x.tier = '{tier}' AND c.city = '{city}'"],
        {"any_row": "SELECT COUNT(DISTINCT t.customer_id) FROM tier_history t JOIN customers c ON c.customer_id = t.customer_id WHERE c.city = '{city}' AND t.tier = '{tier}'",
         "first_row": "SELECT COUNT(*) FROM tier_history t JOIN customers c ON c.customer_id = t.customer_id WHERE c.city = '{city}' AND t.tier = '{tier}' AND t.valid_from = (SELECT MIN(t2.valid_from) FROM tier_history t2 WHERE t2.customer_id = t.customer_id)"},
        pd_f4_current_tier_count, ["city", "tier"]),
    Template(
        "F4_current_tier_list", "F4", "test",
        ["List the IDs of customers from {city} whose current tier is {tier}."],
        f"SELECT t.customer_id FROM tier_history t JOIN customers c ON c.customer_id = t.customer_id WHERE c.city = '{{city}}' AND t.tier = '{{tier}}' AND {LATEST}",
        ["SELECT x.customer_id FROM (SELECT th.customer_id, th.tier, ROW_NUMBER() OVER (PARTITION BY th.customer_id ORDER BY th.valid_from DESC) AS rn FROM tier_history th) x JOIN customers c ON c.customer_id = x.customer_id WHERE x.rn = 1 AND x.tier = '{tier}' AND c.city = '{city}'"],
        {"any_row": "SELECT DISTINCT t.customer_id FROM tier_history t JOIN customers c ON c.customer_id = t.customer_id WHERE c.city = '{city}' AND t.tier = '{tier}'"},
        pd_f4_current_tier_list, ["city", "tier"]),
    Template(
        "F4_net_invoice", "F4", "test",
        ["What is the total net invoice amount of shipped orders placed in {year} by customers from {city}?"],
        f"SELECT (SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND o.status = 'shipped' AND {YR}) + (SELECT COALESCE(SUM(a.amount), 0) FROM invoice_adjustments a JOIN orders o ON o.order_id = a.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND o.status = 'shipped' AND {YR})",
        [f"SELECT SUM(pay.amount) FROM payments pay JOIN orders o ON o.order_id = pay.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND o.status = 'shipped' AND {YR}"],
        {"ignore_adjustments": f"SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id {CITY_JOIN} WHERE c.city = '{{city}}' AND o.status = 'shipped' AND {YR}"},
        pd_f4_net_invoice, ["city", "year"]),
    Template(
        "F4_revenue_by_current_tier", "F4", "test",
        ["For each current customer tier, what was the gross revenue from customers in {city} in {year}? Return tier and revenue."],
        f"SELECT t.tier, SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id {CITY_JOIN} JOIN tier_history t ON t.customer_id = o.customer_id WHERE c.city = '{{city}}' AND {ACTIVE} AND {YR} AND {LATEST} GROUP BY t.tier",
        [f"SELECT x.tier, SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id {CITY_JOIN} JOIN (SELECT th.customer_id, th.tier, ROW_NUMBER() OVER (PARTITION BY th.customer_id ORDER BY th.valid_from DESC) AS rn FROM tier_history th) x ON x.customer_id = o.customer_id AND x.rn = 1 WHERE c.city = '{{city}}' AND {ACTIVE} AND {YR} GROUP BY x.tier"],
        {"all_tier_rows": f"SELECT t.tier, SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON o.order_id = oi.order_id {CITY_JOIN} JOIN tier_history t ON t.customer_id = o.customer_id WHERE c.city = '{{city}}' AND {ACTIVE} AND {YR} GROUP BY t.tier"},
        pd_f4_revenue_by_current_tier, ["city", "year"]),
]

BY_ID = {t.id: t for t in TEMPLATES}
assert len(BY_ID) == len(TEMPLATES)
