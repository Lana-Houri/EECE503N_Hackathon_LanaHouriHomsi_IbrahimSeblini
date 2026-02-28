# =============================================================================
# DATA INGESTION & CLEANING - Conut Bakery Scaled Data
# =============================================================================
# Pipeline stage 1: Load report-style CSVs, strip headers/page markers,
# normalize numeric columns. Saves cleaned tables to artifacts/ for downstream
# feature engineering and modeling.
# =============================================================================

import os
import re
import csv
import pandas as pd
import sys

# Add project root so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


def _clean_numeric(val):
    """Convert report-style numbers (e.g. '2,116,800.0') to float. Used across cleaning."""
    if val is None or (isinstance(val, str) and val.strip() in ("", "-")):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


# -----------------------------------------------------------------------------
# [OBJECTIVE 1 - COMBO OPTIMIZATION] + [OBJECTIVE 5 - COFFEE/MILKSHAKE]
# Sales by customer in detail (line items) - used for product pairs and beverage analysis
# -----------------------------------------------------------------------------
def load_and_clean_sales_detail():
    """
    Load REP_S_00502.csv: line-item sales per customer.
    Report has: title rows, repeated 'Full Name,Qty,Description,Price' headers,
    'Branch :X', 'Person_XXXX' as customer name, then lines with ,Qty,Description,Price, 'Total :' rows.
    We output one row per line item: customer_name, description, qty, price.
    """
    path = os.path.join(config.DATA_DIR, "REP_S_00502.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["customer_name", "description", "qty", "price"])

    rows = []
    current_customer = None
    header_pattern = re.compile(r"^\s*Full Name\s*,", re.IGNORECASE)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n\r")
            parts = [p.strip() for p in line.split(",")]
            # Skip report title and date/page lines
            if not parts or "Page" in line or "From Date" in line or "Sales by customer" in line:
                continue
            if header_pattern.match(line) or line.startswith("Branch ") or "Branch :" in line:
                continue
            # Customer name row: starts with Person_
            if len(parts) >= 1 and re.match(r"^Person_\d+", str(parts[0])):
                current_customer = parts[0]
                continue
            if "Total :" in line or (len(parts) >= 2 and str(parts[1]).strip() == "" and "Total" in str(parts[0])):
                continue
            # Data row: often first col empty, then qty, description, price
            if current_customer is None:
                continue
            if len(parts) >= 4:
                qty_val = _clean_numeric(parts[1])
                desc = parts[2].strip() if len(parts) > 2 else ""
                price_val = _clean_numeric(parts[3])
                if desc and desc != "Total :" and qty_val is not None:
                    rows.append({"customer_name": current_customer, "description": desc, "qty": qty_val, "price": price_val})

    df = pd.DataFrame(rows)
    df = df[df["qty"] != 0].copy()  # drop zero-qty lines (cancellations)
    df.to_csv(config.CLEANED_SALES_DETAIL_PATH, index=False)
    return df


# -----------------------------------------------------------------------------
# [OBJECTIVE 1 - COMBO] Customer orders summary (first/last order, total, order count)
# -----------------------------------------------------------------------------
def load_and_clean_customer_orders():
    """
    Load rep_s_00150.csv: Customer Name, First Order, Last Order, Total, No. of Orders.
    Report has repeated headers every page; we keep rows where first column is Person_XXXX.
    """
    path = os.path.join(config.DATA_DIR, "rep_s_00150.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["customer_name", "first_order", "last_order", "total", "num_orders"])

    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n\r")
            if "Customer Name" in line and "Address" in line:
                continue
            if "Page " in line or "From Date" in line or "Conut -" in line and "," in line and line.count(",") > 3:
                # Likely title/date line
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 8:
                continue
            first = parts[0]
            if not re.match(r"^Person_\d+", first):
                continue
            # Columns: 0=Name, 2=Phone, 3=First Order, 5=Last Order, 7=Total, 8=No. of Orders
            first_order = parts[3] if len(parts) > 3 else ""
            last_order = parts[5] if len(parts) > 5 else ""
            total = _clean_numeric(parts[7]) if len(parts) > 7 else None
            num_orders = _clean_numeric(parts[8]) if len(parts) > 8 else None
            if num_orders is not None and num_orders >= 0:
                rows.append({
                    "customer_name": first,
                    "first_order": first_order,
                    "last_order": last_order,
                    "total": total,
                    "num_orders": int(num_orders) if num_orders == num_orders else 0,
                })

    df = pd.DataFrame(rows)
    df.to_csv(config.CLEANED_ORDERS_PATH, index=False)
    return df


# -----------------------------------------------------------------------------
# [OBJECTIVE 2 - DEMAND FORECASTING] + [OBJECTIVE 3 - EXPANSION]
# Monthly sales by branch - time series for demand and branch performance
# -----------------------------------------------------------------------------
def load_and_clean_monthly_sales():
    """
    Load rep_s_00334_1_SMRY.csv: Branch Name, Month, Year, Total.
    Uses csv.reader so quoted numbers like "554,074,782.88" parse correctly.
    """
    path = os.path.join(config.DATA_DIR, "rep_s_00334_1_SMRY.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["branch", "month", "year", "total"])

    rows = []
    current_branch = None
    month_order = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                   "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        for parts in reader:
            if not parts:
                continue
            first = parts[0].strip() if parts else ""
            if "Branch Name:" in first:
                current_branch = first.replace("Branch Name:", "").strip()
                continue
            if "Page" in first or "Year:" in first or "Total for" in first or "Total by Branch" in first or "Grand Total" in first:
                continue
            if "REP_S_" in first or "Copyright" in first:
                continue
            if len(parts) < 4:
                continue
            month_str = first
            year_val = _clean_numeric(parts[2].strip() if len(parts) > 2 else None)
            total_val = _clean_numeric(parts[3].strip() if len(parts) > 3 else None)
            if month_str in month_order and year_val is not None and total_val is not None and current_branch:
                rows.append({
                    "branch": current_branch,
                    "month": month_str,
                    "year": int(year_val),
                    "total": total_val,
                })

    df = pd.DataFrame(rows)
    df.to_csv(config.CLEANED_MONTHLY_SALES_PATH, index=False)
    return df


# -----------------------------------------------------------------------------
# [OBJECTIVE 4 - SHIFT STAFFING] Time and attendance - punch in/out, duration per employee/branch
# -----------------------------------------------------------------------------
def load_and_clean_attendance():
    """
    Load REP_S_00461.csv: EMP ID, NAME, Branch, PUNCH IN date/time, PUNCH OUT, Work Duration.
    We extract: employee_id, employee_name, branch, punch_in_date, punch_out_date, duration_hours.
    """
    path = os.path.join(config.DATA_DIR, "REP_S_00461.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["employee_id", "branch", "punch_in_date", "duration_hours"])

    rows = []
    current_emp_id = None
    current_name = None
    current_branch = None

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n\r")
            if "EMP ID :" in line:
                try:
                    current_emp_id = line.split("EMP ID :")[1].split(",")[0].strip()
                except IndexError:
                    pass
                continue
            if "NAME :" in line:
                try:
                    current_name = line.split("NAME :")[1].strip()
                except IndexError:
                    pass
                continue
            if "Main Street" in line or "Conut Jnah" in line or "Conut - Tyre" in line or "Conut," in line:
                current_branch = line.split(",")[0].strip() or current_branch
                continue
            if "PUNCH IN" in line or "Total :" in line or "Time &" in line or "From Date" in line:
                continue
            try:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 5:
                    # Format: date_in, time_in, date_out, time_out, duration (e.g. 11.58.21 = 11h58m21s)
                    date_in = parts[0]
                    time_in = parts[1]
                    date_out = parts[2]
                    time_out = parts[3]
                    dur_str = parts[4] if len(parts) > 4 else ""
                    if re.match(r"\d{2}-[A-Za-z]{3}-\d{2}", date_in) and dur_str:
                        # Parse duration H:MM:SS to hours
                        dur_parts = dur_str.replace(".", ":").split(":")
                        try:
                            h = int(dur_parts[0])
                            m = int(dur_parts[1]) if len(dur_parts) > 1 else 0
                            s = int(dur_parts[2]) if len(dur_parts) > 2 else 0
                            duration_hours = h + m / 60 + s / 3600
                        except (ValueError, IndexError):
                            duration_hours = None
                        if duration_hours is not None and current_emp_id and current_branch:
                            rows.append({
                                "employee_id": current_emp_id,
                                "employee_name": current_name,
                                "branch": current_branch,
                                "punch_in_date": date_in,
                                "duration_hours": round(duration_hours, 2),
                            })
            except Exception:
                pass

    df = pd.DataFrame(rows)
    df.to_csv(config.CLEANED_ATTENDANCE_PATH, index=False)
    return df


# -----------------------------------------------------------------------------
# [OBJECTIVE 5 - COFFEE AND MILKSHAKE STRATEGY] Sales by items and groups
# -----------------------------------------------------------------------------
def load_and_clean_items_by_group():
    """
    Load rep_s_00191_SMRY.csv: Description, Qty, Total Amount by Division/Group.
    Uses csv.reader so quoted amounts like "2,860,540.50" parse correctly.
    """
    path = os.path.join(config.DATA_DIR, "rep_s_00191_SMRY.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["description", "division", "group", "qty", "total_amount"])

    rows = []
    current_division = None
    current_group = None
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        for parts in reader:
            if not parts:
                continue
            first = parts[0].strip() if parts else ""
            if "Page " in first or "Description" in first and "Barcode" in str(parts):
                continue
            if "Branch:" in first:
                continue
            if "Division:" in first:
                current_division = first.replace("Division:", "").strip()
                continue
            if "Group:" in first:
                current_group = first.replace("Group:", "").strip()
                continue
            if "Total by" in first:
                continue
            if len(parts) < 4:
                continue
            desc = first
            qty = _clean_numeric(parts[2].strip() if len(parts) > 2 else None)
            total = _clean_numeric(parts[3].strip() if len(parts) > 3 else None)
            if qty is not None and desc and not desc.startswith("Total"):
                rows.append({
                    "description": desc,
                    "division": current_division or "",
                    "group": current_group or "",
                    "qty": qty,
                    "total_amount": total,
                })

    df = pd.DataFrame(rows)
    df.to_csv(config.CLEANED_ITEMS_GROUPS_PATH, index=False)
    return df


# -----------------------------------------------------------------------------
# [OBJECTIVE 3 - EXPANSION] + general metrics - Average sales by menu (branch/channel)
# -----------------------------------------------------------------------------
def load_and_clean_avg_sales_menu():
    """Load rep_s_00435_SMRY.csv: Menu Name (branch/channel), # Cust, Sales, Avg Customer."""
    path = os.path.join(config.DATA_DIR, "rep_s_00435_SMRY.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["menu_name", "branch", "channel", "num_cust", "sales", "avg_customer"])

    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n\r")
            if "Menu Name" in line or "Copyright" in line or "Total :" in line and "Total By" not in line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 4:
                continue
            menu = parts[0]
            num_cust = _clean_numeric(parts[1])
            sales = _clean_numeric(parts[2])
            avg_cust = _clean_numeric(parts[3])
            if menu and num_cust is not None and "Total" not in menu:
                rows.append({
                    "menu_name": menu,
                    "num_cust": num_cust,
                    "sales": sales,
                    "avg_customer": avg_cust,
                })

    df = pd.DataFrame(rows)
    # Infer branch from menu name (e.g. "Conut - Tyre", "Conut Jnah")
    df["branch"] = df["menu_name"].apply(lambda x: x if any(b in str(x) for b in ["Conut", "Main Street"]) else "")
    df["channel"] = df["menu_name"].apply(lambda x: "DELIVERY" if "DELIVERY" in str(x).upper() else "TABLE" if "TABLE" in str(x).upper() else "TAKE AWAY" if "TAKE AWAY" in str(x).upper() else "")
    df.to_csv(config.CLEANED_AVG_SALES_MENU_PATH, index=False)
    return df


# -----------------------------------------------------------------------------
# [OBJECTIVE 3 - EXPANSION] Tax summary by branch - proxy for branch size/revenue
# -----------------------------------------------------------------------------
def load_and_clean_tax_by_branch():
    """Load REP_S_00194_SMRY.csv: Branch Name, Tax Total. Format: 'Branch Name:  X' then 'Total By Branch,...,number'."""
    path = os.path.join(config.DATA_DIR, "REP_S_00194_SMRY.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["branch", "tax_total"])

    rows = []
    current_branch = None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n\r")
            if "Branch Name:" in line:
                current_branch = line.replace("Branch Name:", "").strip()
                continue
            if "Total By Branch" in line and current_branch:
                parts = [p.strip().replace('"', "") for p in line.split(",")]
                for p in parts:
                    tax_val = _clean_numeric(p)
                    if tax_val is not None and tax_val > 0:
                        rows.append({"branch": current_branch, "tax_total": tax_val})
                        break
                current_branch = None
                continue

    df = pd.DataFrame(rows).drop_duplicates(subset=["branch"])
    df.to_csv(config.CLEANED_TAX_BRANCH_PATH, index=False)
    return df


# -----------------------------------------------------------------------------
# RUN ALL INGESTION - Called by run_pipeline.py
# -----------------------------------------------------------------------------
def run_ingestion():
    """Run all load_and_clean_* steps and save artifacts. Returns dict of dataframes."""
    os.makedirs(config.ARTIFACTS_DIR, exist_ok=True)
    result = {}
    result["orders"] = load_and_clean_customer_orders()
    result["sales_detail"] = load_and_clean_sales_detail()
    result["monthly_sales"] = load_and_clean_monthly_sales()
    result["attendance"] = load_and_clean_attendance()
    result["items_by_group"] = load_and_clean_items_by_group()
    result["avg_sales_menu"] = load_and_clean_avg_sales_menu()
    result["tax_by_branch"] = load_and_clean_tax_by_branch()
    return result


if __name__ == "__main__":
    run_ingestion()
    print("Ingestion done. Artifacts in", config.ARTIFACTS_DIR)
