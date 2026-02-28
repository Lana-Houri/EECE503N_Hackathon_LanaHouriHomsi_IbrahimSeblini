# =============================================================================
# [OBJECTIVE 2] DEMAND FORECASTING BY BRANCH
# =============================================================================
# Forecast demand per branch to support inventory and supply chain decisions.
# Uses cleaned monthly sales by branch. We use a simple approach: average
# recent months + optional seasonal factor, stored as next-period forecast.
# =============================================================================

import os
import json
import pandas as pd
import numpy as np

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


def run_demand_forecasting(monthly_sales: pd.DataFrame = None):
    """
    Produce per-branch demand forecast for next period.
    Focus on patterns/ratios (scaled data). Output: demand_forecast.json.
    """
    if monthly_sales is None or (hasattr(monthly_sales, "empty") and monthly_sales.empty):
        try:
            if os.path.exists(config.CLEANED_MONTHLY_SALES_PATH) and os.path.getsize(config.CLEANED_MONTHLY_SALES_PATH) > 10:
                monthly_sales = pd.read_csv(config.CLEANED_MONTHLY_SALES_PATH)
            else:
                monthly_sales = pd.DataFrame()
        except Exception:
            monthly_sales = pd.DataFrame()
    if monthly_sales is None or (hasattr(monthly_sales, "empty") and monthly_sales.empty):
        out = {"forecasts": [], "note": "No monthly sales data."}
        with open(config.DEMAND_FORECAST_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        return out

    # Aggregate total per branch per month (in case of duplicates)
    monthly_sales["total"] = pd.to_numeric(monthly_sales["total"], errors="coerce")
    branch_month = monthly_sales.groupby(["branch", "month", "year"])["total"].sum().reset_index()

    # Simple forecast: average of last 3 months per branch, or overall average
    forecasts = []
    for branch in branch_month["branch"].unique():
        br_df = branch_month[branch_month["branch"] == branch].sort_values(["year", "month"])
        if br_df.empty:
            continue
        # Use numeric month for ordering
        month_order = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                       "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        br_df = br_df.copy()
        br_df["month_num"] = br_df["month"].map(month_order)
        br_df = br_df.sort_values(["year", "month_num"])
        recent = br_df.tail(3)["total"]
        forecast_val = float(recent.mean()) if len(recent) else float(br_df["total"].mean())
        forecasts.append({
            "branch": branch,
            "forecast_next_period": round(forecast_val, 2),
            "unit": "scaled",
            "based_on_months": int(min(3, len(br_df))),
        })

    out = {"forecasts": forecasts, "note": "Values in scaled units; use for relative comparison."}
    with open(config.DEMAND_FORECAST_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out
