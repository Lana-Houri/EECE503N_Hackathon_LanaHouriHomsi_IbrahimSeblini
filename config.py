# =============================================================================
# CONUT AI CHIEF OF OPERATIONS AGENT - CONFIGURATION
# =============================================================================
# Central config for data paths and constants. Used by ingestion, pipeline, and API.
# =============================================================================

import os

# -----------------------------------------------------------------------------
# PATHS - Data folder and artifact outputs for the pipeline
# -----------------------------------------------------------------------------
# Base directory: project root (where this config.py lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder containing the scaled Conut bakery CSVs (report-style exports)
DATA_DIR = os.path.join(BASE_DIR, "Conut bakery Scaled Data")

# Folder where pipeline saves cleaned data and model artifacts (for reproducibility)
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# Specific artifact files used by the API at inference time
CLEANED_ORDERS_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_orders.csv")
CLEANED_SALES_DETAIL_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_sales_detail.csv")
CLEANED_MONTHLY_SALES_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_monthly_sales.csv")
CLEANED_ATTENDANCE_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_attendance.csv")
CLEANED_ITEMS_GROUPS_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_items_by_group.csv")
CLEANED_AVG_SALES_MENU_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_avg_sales_menu.csv")
CLEANED_TAX_BRANCH_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_tax_by_branch.csv")

# Demand forecasting model artifact (e.g. simple seasonal model or last-known values)
DEMAND_FORECAST_ARTIFACT = os.path.join(ARTIFACTS_DIR, "demand_forecast.json")
# Combo optimization: top combos and item pairs
COMBO_ARTIFACT = os.path.join(ARTIFACTS_DIR, "combo_recommendations.json")
# Expansion: branch metrics and feasibility scores
EXPANSION_ARTIFACT = os.path.join(ARTIFACTS_DIR, "expansion_feasibility.json")
# Staffing: recommended employees per shift/branch
STAFFING_ARTIFACT = os.path.join(ARTIFACTS_DIR, "staffing_recommendations.json")
# Coffee & milkshake strategy summary
COFFEE_MILKSHAKE_STRATEGY_ARTIFACT = os.path.join(ARTIFACTS_DIR, "coffee_milkshake_strategy.json")
