import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

# --- DATA INGESTION & CLEANING ---
from src.data.ingestion import run_ingestion

# --- OBJECTIVES (modeling/analytics) ---
from src.objectives.combo_optimization import run_combo_optimization
from src.objectives.demand_forecasting import run_demand_forecasting
from src.objectives.expansion_feasibility import run_expansion_feasibility
from src.objectives.shift_staffing import run_shift_staffing
from src.objectives.coffee_milkshake_strategy import run_coffee_milkshake_strategy


def main():
    print("Conut AI Pipeline: Ingestion + Cleaning...")
    data = run_ingestion()
    print("  Orders:", len(data.get("orders", [])))
    print("  Sales detail:", len(data.get("sales_detail", [])))
    print("  Monthly sales:", len(data.get("monthly_sales", [])))
    print("  Attendance:", len(data.get("attendance", [])))

    print("\n[OBJECTIVE 1] Combo optimization...")
    run_combo_optimization(data.get("sales_detail"))

    print("[OBJECTIVE 2] Demand forecasting by branch...")
    run_demand_forecasting(data.get("monthly_sales"))

    print("[OBJECTIVE 3] Expansion feasibility...")
    run_expansion_feasibility(
        data.get("monthly_sales"),
        data.get("tax_by_branch"),
        data.get("avg_sales_menu"),
    )

    print("[OBJECTIVE 4] Shift staffing estimation...")
    run_shift_staffing(data.get("attendance"), data.get("monthly_sales"))

    print("[OBJECTIVE 5] Coffee & milkshake growth strategy...")
    run_coffee_milkshake_strategy(data.get("items_by_group"), data.get("sales_detail"))

    print("\nPipeline complete. Artifacts in:", config.ARTIFACTS_DIR)


if __name__ == "__main__":
    main()
