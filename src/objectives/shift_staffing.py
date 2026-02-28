
import os
import json
import pandas as pd
import numpy as np

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


def run_shift_staffing(attendance: pd.DataFrame = None, monthly_sales: pd.DataFrame = None):
    """
    Estimate required employees per shift per branch.
    Logic: use historical attendance (hours per branch) and demand (sales) to
    derive ratio; recommend staff count per branch for typical shift.
    """
    if attendance is None or attendance.empty:
        if os.path.exists(config.CLEANED_ATTENDANCE_PATH):
            attendance = pd.read_csv(config.CLEANED_ATTENDANCE_PATH)
        else:
            return {"recommendations": [], "message": "No attendance data."}

    attendance["duration_hours"] = pd.to_numeric(attendance["duration_hours"], errors="coerce")
    branch_hours = attendance.groupby("branch").agg({
        "duration_hours": "sum",
        "employee_id": "nunique",
    }).reset_index()
    branch_hours.columns = ["branch", "total_hours", "unique_employees"]

    branch_hours["avg_hours_per_employee"] = branch_hours["total_hours"] / branch_hours["unique_employees"].replace(0, np.nan)
    hours_per_shift = 8.0
    branch_hours["estimated_shifts_per_period"] = branch_hours["total_hours"] / hours_per_shift
    branch_hours["recommended_employees_per_shift"] = (
        branch_hours["unique_employees"] * branch_hours["avg_hours_per_employee"] / hours_per_shift
    ).round(1)
    branch_hours["recommended_employees_per_shift"] = branch_hours["recommended_employees_per_shift"].clip(lower=1)

    recommendations = []
    for _, row in branch_hours.iterrows():
        recommendations.append({
            "branch": row["branch"],
            "recommended_employees_per_shift": float(row["recommended_employees_per_shift"]),
            "observed_employees_in_data": int(row["unique_employees"]),
            "total_hours_observed": round(float(row["total_hours"]), 2),
            "note": "Based on historical attendance; scale with demand if needed.",
        })

    out = {"recommendations": recommendations, "shift_hours_assumed": hours_per_shift}
    with open(config.STAFFING_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out
