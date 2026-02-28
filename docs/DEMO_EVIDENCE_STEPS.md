# Steps to Capture Demo Evidence (Screenshots)

Use these steps to create screenshots (or a short video) showing your Conut API being invoked and returning results. Save screenshots in **`docs/demo/`**.

---

## Prerequisites

- Pipeline has been run at least once (`python run_pipeline.py` or `py run_pipeline.py`) so `artifacts/` contains JSON files.
- You have a terminal and a browser (or OpenClaw, if provided by the course).

---

## Option A: Using Swagger UI (FastAPI docs)

This works without OpenClaw and clearly shows the API and OpenClaw-ready endpoints.

### Step 1: Start the API

In a terminal, from the project root:

```bash
py -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Or, if `python` works on your system:

```bash
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Leave this terminal open. You should see something like: `Uvicorn running on http://0.0.0.0:8000`.

---

### Step 2: Open the API docs

In your browser go to:

**http://localhost:8000/docs**

You should see the Swagger UI with all endpoints listed.

**Screenshot 1:** Capture the full docs page showing the list of endpoints (e.g. `/api/tools/list`, `/api/demand_forecast`, `/api/combo_recommendations`, etc.).  
Save as: `docs/demo/01_api_docs.png`

---

### Step 3: Call the tools list (OpenClaw discovery)

1. In Swagger UI, find **GET /api/tools/list** and click **Try it out**.
2. Click **Execute**.
3. Check the response (list of tools and `base_url`).

**Screenshot 2:** Full window or the response panel showing the JSON with `tools` and `base_url`.  
Save as: `docs/demo/02_tools_list.png`

---

### Step 4: Call demand forecast

1. Find **GET /api/demand_forecast** → **Try it out** → **Execute**.
2. Confirm the response shows `forecasts` (per-branch forecast).

**Screenshot 3:** Response body with forecasts.  
Save as: `docs/demo/03_demand_forecast.png`

---

### Step 5: Call combo recommendations

1. Find **GET /api/combo_recommendations** → **Try it out** → (optional: set `limit` to 5) → **Execute**.
2. Confirm the response shows `combos` and `pairs`.

**Screenshot 4:** Response with combos/pairs.  
Save as: `docs/demo/04_combo_recommendations.png`

---

### Step 6: Call staffing recommendation

1. Find **GET /api/staffing_recommendation** → **Try it out** → **Execute**.
2. Confirm the response shows `recommendations` per branch.

**Screenshot 5:** Response with staffing recommendations.  
Save as: `docs/demo/05_staffing_recommendation.png`

---

### Step 7: (Optional) Expansion and coffee/milkshake

- **GET /api/expansion_feasibility** → Execute → screenshot → `docs/demo/06_expansion_feasibility.png`
- **GET /api/coffee_milkshake_strategy** → Execute → screenshot → `docs/demo/07_coffee_milkshake_strategy.png`

---

## Option B: Using the browser address bar

If Swagger is slow or you prefer a minimal demo:

1. Start the API (same as Step 1 above).
2. Open these URLs in the browser one by one and screenshot each response:
   - http://localhost:8000/api/tools/list  
   - http://localhost:8000/api/demand_forecast  
   - http://localhost:8000/api/combo_recommendations  
   - http://localhost:8000/api/staffing_recommendation  

Save each screenshot as above (e.g. `02_tools_list.png`, `03_demand_forecast.png`, etc.) in `docs/demo/`.

---

## Option C: If you have OpenClaw

1. Start the Conut API (Step 1 above).
2. Configure OpenClaw to use base URL: `http://localhost:8000` and the paths from `GET /api/tools/list`.
3. In OpenClaw, run queries such as:
   - “What is the demand forecast?”
   - “Give me combo recommendations.”
   - “What staffing do you recommend?”
4. Take screenshots that show:
   - OpenClaw’s interface with the query.
   - The response from your API (or OpenClaw’s summary of it).

Save in `docs/demo/` with names like `openclaw_demand.png`, `openclaw_combos.png`, `openclaw_staffing.png`.

---

## Checklist before submission

- [ ] All screenshots (or video) are in **`docs/demo/`** (or linked from the README).
- [ ] At least one screenshot shows **tool discovery** (`/api/tools/list`).
- [ ] At least one screenshot shows an **operational result** (e.g. demand forecast, combos, or staffing).
- [ ] README or submission mentions where to find the demo evidence (e.g. “See `docs/demo/`”).

---

## Quick reference – API base URL and endpoints

| Endpoint | Purpose |
|----------|--------|
| `GET /health` | Health check |
| `GET /api/tools/list` | OpenClaw tool discovery |
| `GET /api/demand_forecast` | Demand forecast by branch |
| `GET /api/combo_recommendations` | Combo suggestions |
| `GET /api/staffing_recommendation` | Staffing per branch |
| `GET /api/expansion_feasibility` | Expansion feasibility |
| `GET /api/coffee_milkshake_strategy` | Coffee/milkshake strategy |

Base URL: **http://localhost:8000**
