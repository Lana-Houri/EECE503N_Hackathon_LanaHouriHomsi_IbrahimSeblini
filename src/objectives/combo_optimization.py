
import os
import json
import pandas as pd
from collections import defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


def _normalize_product(desc):
    """Normalize product name for grouping (strip extra spaces, optional: map variants)."""
    if not isinstance(desc, str):
        return ""
    return desc.strip()


def run_combo_optimization(sales_detail: pd.DataFrame = None):
    """
    Compute frequently bought-together pairs and top combo suggestions.
    Uses co-occurrence in same order (same customer_name in sales_detail = same order context).
    """
    if sales_detail is None or sales_detail.empty:
        if os.path.exists(config.CLEANED_SALES_DETAIL_PATH):
            sales_detail = pd.read_csv(config.CLEANED_SALES_DETAIL_PATH)
        else:
            return {"top_pairs": [], "top_combos": [], "message": "No sales detail data."}

    orders = sales_detail.groupby("customer_name")["description"].apply(
        lambda x: [_normalize_product(d) for d in x.dropna().unique() if _normalize_product(d)]
    ).to_dict()

    pair_counts = defaultdict(int)
    for products in orders.values():
        products = [p for p in products if p]
        for i in range(len(products)):
            for j in range(i + 1, len(products)):
                a, b = products[i], products[j]
                if a != b:
                    pair_counts[(min(a, b), max(a, b))] += 1

    sorted_pairs = sorted(pair_counts.items(), key=lambda x: -x[1])[:30]
    top_pairs = [{"item_a": a, "item_b": b, "count": c} for (a, b), c in sorted_pairs]

    combo_suggestions = []
    for (a, b), c in sorted_pairs[:15]:
        combo_suggestions.append({"combo": f"{a} + {b}", "co_occurrence_count": c})

    out = {
        "top_pairs": top_pairs,
        "top_combos": combo_suggestions,
        "num_orders_analyzed": len(orders),
    }
    with open(config.COMBO_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out
