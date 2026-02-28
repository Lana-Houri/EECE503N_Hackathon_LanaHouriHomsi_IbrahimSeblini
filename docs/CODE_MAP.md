# Code Map – Which Snippets Belong to What

Use this to find where each **business objective** and **pipeline stage** is implemented.

---

## Pipeline stages

| Stage | Where | What it does |
|-------|--------|---------------|
| **Data ingestion** | `src/data/ingestion.py` | Reads Conut CSVs from `Conut bakery Scaled Data/` |
| **Cleaning** | Same file, each `load_and_clean_*` function | Strips report headers, normalizes numbers, writes to `artifacts/*.csv` |
| **Feature use / analytics** | `src/objectives/*.py` | Each objective uses cleaned CSVs and produces JSON |
| **Inference / reporting** | `src/api/app.py` | API loads JSON artifacts and returns answers to queries |
| **Run pipeline** | `run_pipeline.py` | Calls ingestion then all 5 objectives in order |

---

## Business objectives → files and functions

| # | Objective | Ingestion (data used) | Analytics | API endpoint |
|---|-----------|------------------------|-----------|---------------|
| 1 | **Combo optimization** | `load_and_clean_sales_detail()` | `src/objectives/combo_optimization.py` → `run_combo_optimization()` | `GET /api/combo_recommendations` |
| 2 | **Demand forecasting by branch** | `load_and_clean_monthly_sales()` | `src/objectives/demand_forecasting.py` → `run_demand_forecasting()` | `GET /api/demand_forecast` |
| 3 | **Expansion feasibility** | `load_and_clean_monthly_sales()`, `load_and_clean_tax_by_branch()`, `load_and_clean_avg_sales_menu()` | `src/objectives/expansion_feasibility.py` → `run_expansion_feasibility()` | `GET /api/expansion_feasibility` |
| 4 | **Shift staffing estimation** | `load_and_clean_attendance()` | `src/objectives/shift_staffing.py` → `run_shift_staffing()` | `GET /api/staffing_recommendation` |
| 5 | **Coffee and milkshake growth strategy** | `load_and_clean_items_by_group()`, `load_and_clean_sales_detail()` | `src/objectives/coffee_milkshake_strategy.py` → `run_coffee_milkshake_strategy()` | `GET /api/coffee_milkshake_strategy` |

---

## OpenClaw integration

- **Tool list**: `GET /api/tools/list` – returns tool names and paths so OpenClaw can call them.
- **Base URL**: Run API with `uvicorn src.api.app:app --host 0.0.0.0 --port 8000`; then base URL is `http://localhost:8000`.
- Each objective has a GET endpoint under `/api/`; OpenClaw can invoke these as HTTP tools.

---

## Config and artifacts

- **Paths**: `config.py` – `DATA_DIR`, `ARTIFACTS_DIR`, and all `*_PATH` / `*_ARTIFACT` constants.
- **Artifacts written by pipeline**:  
  `artifacts/cleaned_*.csv`, `artifacts/combo_recommendations.json`, `artifacts/demand_forecast.json`, `artifacts/expansion_feasibility.json`, `artifacts/staffing_recommendations.json`, `artifacts/coffee_milkshake_strategy.json`.
