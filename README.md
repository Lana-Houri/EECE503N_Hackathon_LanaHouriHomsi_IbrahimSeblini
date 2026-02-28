# Conut AI Chief of Operations Agent

**AI Engineering Hackathon** – 12-Hour Chief of Operations Agent Challenge  
American University of Beirut | Professor Ammar Mohanna

---

## Business Problem

Conut is a growing sweets and beverages business. This project delivers an **AI-driven Chief of Operations Agent** that turns operational data into actionable decisions for:

1. **Combo optimization** – Optimal product combinations from customer purchasing patterns  
2. **Demand forecasting by branch** – Per-branch demand for inventory and supply chain  
3. **Expansion feasibility** – Whether to open new branches and candidate location criteria  
4. **Shift staffing estimation** – Required employees per shift using demand and attendance  
5. **Coffee and milkshake growth strategy** – Data-driven strategies to grow beverage sales  

The system is **integrated with OpenClaw**: OpenClaw can invoke the API to run demand prediction, staffing recommendations, combo suggestions, and sales strategy queries.

---

## Approach and Architecture

- **End-to-end pipeline**: Data ingestion (report-style CSVs) → cleaning → feature use → modeling/analytics → JSON artifacts.  
- **Reproducibility**: Pinned dependencies in `requirements.txt`; one command to run pipeline and one to start the API.  
- **Operational AI**: A REST API that answers the five business questions from precomputed artifacts.  
- **OpenClaw**: GET endpoints under `/api/*` and `/api/tools/list` for tool discovery; OpenClaw can call these via HTTP.

**Project layout:**

```
Hackathon/
├── config.py                 # Paths and artifact names
├── requirements.txt         # Pinned dependencies
├── run_pipeline.py          # Run full pipeline (ingestion + all 5 objectives)
├── Conut bakery Scaled Data/ # Input CSVs
├── artifacts/               # Cleaned data + JSON outputs (created by pipeline)
├── src/
│   ├── data/
│   │   └── ingestion.py     # Load & clean all report CSVs
│   ├── objectives/          # One module per business objective
│   │   ├── combo_optimization.py
│   │   ├── demand_forecasting.py
│   │   ├── expansion_feasibility.py
│   │   ├── shift_staffing.py
│   │   └── coffee_milkshake_strategy.py
│   └── api/
│       └── app.py           # FastAPI service + OpenClaw endpoints
└── docs/
    └── EXECUTIVE_BRIEF.md   # Summary for PDF export
```

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the pipeline (ingestion + analytics)

From the project root:

```bash
python run_pipeline.py
```

This writes cleaned data and JSON artifacts into `artifacts/`.

### 3. Start the API (for queries and OpenClaw)

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Or:

```bash
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

- **Health**: `GET http://localhost:8000/health`  
- **OpenClaw tools list**: `GET http://localhost:8000/api/tools/list`  
- **Demand forecast**: `GET http://localhost:8000/api/demand_forecast`  
- **Combo recommendations**: `GET http://localhost:8000/api/combo_recommendations`  
- **Staffing**: `GET http://localhost:8000/api/staffing_recommendation`  
- **Expansion**: `GET http://localhost:8000/api/expansion_feasibility`  
- **Coffee/milkshake strategy**: `GET http://localhost:8000/api/coffee_milkshake_strategy`  

### 4. OpenClaw integration

- Point OpenClaw at `http://localhost:8000` and use the paths above as HTTP tools.  
- `GET /api/tools/list` returns tool names and arguments.  
- Example: to get demand prediction, OpenClaw calls `GET /api/demand_forecast`; for staffing, `GET /api/staffing_recommendation`.

---

## Key Results and Recommendations

- **Combos**: Top product pairs and combo suggestions are in `artifacts/combo_recommendations.json` and via `/api/combo_recommendations`.  
- **Demand**: Per-branch next-period forecast (scaled units) in `artifacts/demand_forecast.json` and `/api/demand_forecast`.  
- **Expansion**: Branch metrics and feasibility criteria in `artifacts/expansion_feasibility.json` and `/api/expansion_feasibility`.  
- **Staffing**: Recommended employees per shift per branch in `artifacts/staffing_recommendations.json` and `/api/staffing_recommendation`.  
- **Coffee/milkshake**: Top products and growth strategies in `artifacts/coffee_milkshake_strategy.json` and `/api/coffee_milkshake_strategy`.  

Data is in **scaled units**; use for patterns, ratios, and relative comparison only.

---

## Deliverables

- **Repository**: This repo with the structure above.  
- **README**: This file (problem, approach, how to run, results).  
- **Executive brief**: `docs/EXECUTIVE_BRIEF.md` — export to PDF (max 2 pages) for submission; includes problem framing, top findings, recommended actions, expected impact and risks.  
- **Demo evidence**: Screenshots or short video of OpenClaw invoking the API (e.g. calling `/api/demand_forecast`, `/api/combo_recommendations`, `/api/staffing_recommendation`). Place in `docs/demo/` or link from this README.
