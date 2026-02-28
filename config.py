
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Conut bakery Scaled Data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

CLEANED_ORDERS_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_orders.csv")
CLEANED_SALES_DETAIL_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_sales_detail.csv")
CLEANED_MONTHLY_SALES_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_monthly_sales.csv")
CLEANED_ATTENDANCE_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_attendance.csv")
CLEANED_ITEMS_GROUPS_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_items_by_group.csv")
CLEANED_AVG_SALES_MENU_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_avg_sales_menu.csv")
CLEANED_TAX_BRANCH_PATH = os.path.join(ARTIFACTS_DIR, "cleaned_tax_by_branch.csv")

DEMAND_FORECAST_ARTIFACT = os.path.join(ARTIFACTS_DIR, "demand_forecast.json")
COMBO_ARTIFACT = os.path.join(ARTIFACTS_DIR, "combo_recommendations.json")
EXPANSION_ARTIFACT = os.path.join(ARTIFACTS_DIR, "expansion_feasibility.json")
STAFFING_ARTIFACT = os.path.join(ARTIFACTS_DIR, "staffing_recommendations.json")
COFFEE_MILKSHAKE_STRATEGY_ARTIFACT = os.path.join(ARTIFACTS_DIR, "coffee_milkshake_strategy.json")
