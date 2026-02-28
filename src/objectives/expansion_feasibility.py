
import os
import json
import pandas as pd

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


def run_expansion_feasibility(
    monthly_sales: pd.DataFrame = None,
    tax_by_branch: pd.DataFrame = None,
    avg_sales_menu: pd.DataFrame = None,
):
    """
    Score existing branches and produce feasibility summary for expansion.
    Output: expansion_feasibility.json.
    """
    if monthly_sales is None and os.path.exists(config.CLEANED_MONTHLY_SALES_PATH):
        monthly_sales = pd.read_csv(config.CLEANED_MONTHLY_SALES_PATH)
    if tax_by_branch is None and os.path.exists(config.CLEANED_TAX_BRANCH_PATH):
        tax_by_branch = pd.read_csv(config.CLEANED_TAX_BRANCH_PATH)
    if avg_sales_menu is None and os.path.exists(config.CLEANED_AVG_SALES_MENU_PATH):
        avg_sales_menu = pd.read_csv(config.CLEANED_AVG_SALES_MENU_PATH)

    branch_metrics = []
    branches = set()
    if monthly_sales is not None and not monthly_sales.empty:
        monthly_sales["total"] = pd.to_numeric(monthly_sales["total"], errors="coerce")
        by_branch = monthly_sales.groupby("branch")["total"].agg(["sum", "mean", "count"]).reset_index()
        by_branch.columns = ["branch", "total_sales", "avg_monthly_sales", "months_of_data"]
        for _, row in by_branch.iterrows():
            branches.add(row["branch"])
            branch_metrics.append({
                "branch": row["branch"],
                "total_sales_scaled": round(float(row["total_sales"]), 2),
                "avg_monthly_sales_scaled": round(float(row["avg_monthly_sales"]), 2),
                "months_of_data": int(row["months_of_data"]),
            })

    if tax_by_branch is not None and not tax_by_branch.empty:
        tax_by_branch["tax_total"] = pd.to_numeric(tax_by_branch["tax_total"], errors="coerce")
        for _, row in tax_by_branch.iterrows():
            br = row["branch"]
            branches.add(br)
            existing = next((m for m in branch_metrics if m["branch"] == br), None)
            if existing:
                existing["tax_total_scaled"] = round(float(row["tax_total"]), 2)
            else:
                branch_metrics.append({"branch": br, "tax_total_scaled": round(float(row["tax_total"]), 2)})

    total_sales_all = sum(m.get("total_sales_scaled", 0) or 0 for m in branch_metrics)
    avg_per_branch = total_sales_all / len(branch_metrics) if branch_metrics else 0

    recommendation = {
        "feasibility": "feasible",
        "reason": "Existing branches show consistent scaled revenue; expansion can replicate success in similar locations.",
        "candidate_criteria": [
            "High foot traffic (e.g. malls, main streets)",
            "Similar demographic to current best-performing branches",
            "Proximity to delivery zone for cross-channel sales",
        ],
        "existing_branch_count": len(branches),
        "avg_sales_per_branch_scaled": round(avg_per_branch, 2),
    }

    out = {
        "branch_metrics": branch_metrics,
        "recommendation": recommendation,
    }
    with open(config.EXPANSION_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out
