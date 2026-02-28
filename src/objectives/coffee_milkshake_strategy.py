
import os
import json
import math
import pandas as pd

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


def _is_coffee(desc):
    desc = str(desc).upper()
    return "COFFEE" in desc or "ESPRESSO" in desc or "CAPPUCCINO" in desc or "LATTE" in desc or "MOCHA" in desc or "FRAPPE" in desc


def _is_milkshake(desc):
    desc = str(desc).upper()
    return "MILKSHAKE" in desc or "SHAKE" in desc


def run_coffee_milkshake_strategy(items_by_group: pd.DataFrame = None, sales_detail: pd.DataFrame = None):
    """
    Analyze coffee and milkshake performance and output growth strategies.
    """
    if items_by_group is None or items_by_group.empty:
        if os.path.exists(config.CLEANED_ITEMS_GROUPS_PATH):
            items_by_group = pd.read_csv(config.CLEANED_ITEMS_GROUPS_PATH)
        else:
            items_by_group = pd.DataFrame()

    if sales_detail is None or sales_detail.empty and os.path.exists(config.CLEANED_SALES_DETAIL_PATH):
        sales_detail = pd.read_csv(config.CLEANED_SALES_DETAIL_PATH)

    strategies = []
    coffee_items = []
    milkshake_items = []

    if not items_by_group.empty:
        items_by_group["qty"] = pd.to_numeric(items_by_group["qty"], errors="coerce")
        items_by_group["total_amount"] = pd.to_numeric(items_by_group["total_amount"], errors="coerce")
        for _, row in items_by_group.iterrows():
            d = str(row.get("description", ""))
            q = row.get("qty") or 0
            t = row.get("total_amount") or 0
            if _is_coffee(d):
                coffee_items.append({"description": d, "qty": q, "total_amount": t})
            elif _is_milkshake(d):
                milkshake_items.append({"description": d, "qty": q, "total_amount": t})

    if not sales_detail.empty:
        sales_detail["qty"] = pd.to_numeric(sales_detail["qty"], errors="coerce")
        sales_detail["price"] = pd.to_numeric(sales_detail["price"], errors="coerce")
        for _, row in sales_detail.iterrows():
            d = str(row.get("description", ""))
            if _is_coffee(d) and not any(x["description"] == d for x in coffee_items):
                coffee_items.append({"description": d, "qty": row["qty"], "total_amount": row.get("price", 0) * row["qty"]})
            elif _is_milkshake(d) and not any(x["description"] == d for x in milkshake_items):
                milkshake_items.append({"description": d, "qty": row["qty"], "total_amount": row.get("price", 0) * row["qty"]})

    from collections import defaultdict
    c_totals = defaultdict(lambda: {"qty": 0, "total_amount": 0})
    for x in coffee_items:
        c_totals[x["description"]]["qty"] += x.get("qty", 0)
        c_totals[x["description"]]["total_amount"] += x.get("total_amount", 0)
    m_totals = defaultdict(lambda: {"qty": 0, "total_amount": 0})
    for x in milkshake_items:
        m_totals[x["description"]]["qty"] += x.get("qty", 0)
        m_totals[x["description"]]["total_amount"] += x.get("total_amount", 0)

    top_coffee = sorted(c_totals.items(), key=lambda x: -x[1]["qty"])[:10]
    top_milkshake = sorted(m_totals.items(), key=lambda x: -x[1]["qty"])[:10]

    strategies.append("Bundle coffee with popular pastries (use combo optimization pairs) to increase basket size.")
    strategies.append("Promote milkshakes during peak warm hours; run limited-time flavors to drive trials.")
    strategies.append("Highlight top-selling coffee items (e.g. CAFFE LATTE, DOUBLE ESPRESSO) on menu and delivery.")
    strategies.append("Cross-sell milkshakes with chimney/conut items where combos are strong.")
    strategies.append("Use scaled volume and revenue ratios to allocate inventory and marketing spend across branches.")

    def _sanitize(val):
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        if isinstance(val, (int, float)):
            return round(val, 2) if isinstance(val, float) else val
        return val

    out = {
        "coffee": {"top_products_by_qty": [{"description": k, "qty": _sanitize(v["qty"]), "total_amount": _sanitize(v["total_amount"])} for k, v in top_coffee]},
        "milkshake": {"top_products_by_qty": [{"description": k, "qty": _sanitize(v["qty"]), "total_amount": _sanitize(v["total_amount"])} for k, v in top_milkshake]},
        "growth_strategies": strategies,
    }
    with open(config.COFFEE_MILKSHAKE_STRATEGY_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out
