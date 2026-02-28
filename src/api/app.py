
import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Conut Chief of Operations Agent API",
    description="AI-driven operational queries: demand forecast, combos, staffing, expansion, coffee/milkshake strategy. For OpenClaw integration.",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _load_artifact(path, default=None):
    """Load JSON artifact if present; return default otherwise. Tolerates NaN in file."""
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        text = text.replace(": NaN", ": null").replace(": nan", ": null")
        return json.loads(text)
    except Exception:
        return default


@app.get("/api/combo_recommendations", summary="Get optimal product combo suggestions")
def get_combo_recommendations(limit: int = 10):
    """Return top product pairs and combo suggestions from purchasing patterns."""
    data = _load_artifact(config.COMBO_ARTIFACT, {"top_combos": [], "top_pairs": []})
    combos = data.get("top_combos", [])[:limit]
    pairs = data.get("top_pairs", [])[:limit]
    return {"combos": combos, "pairs": pairs, "note": "Based on co-occurrence in orders."}


@app.get("/api/demand_forecast", summary="Get demand forecast by branch")
def get_demand_forecast(branch: str = None):
    """Return demand forecast per branch (scaled units). Optional branch filter."""
    data = _load_artifact(config.DEMAND_FORECAST_ARTIFACT, {"forecasts": []})
    forecasts = data.get("forecasts", [])
    if branch:
        forecasts = [f for f in forecasts if branch.lower() in f.get("branch", "").lower()]
    return {"forecasts": forecasts}


@app.get("/api/expansion_feasibility", summary="Expansion feasibility and branch metrics")
def get_expansion_feasibility():
    """Return branch metrics and feasibility recommendation for new locations."""
    return _load_artifact(config.EXPANSION_ARTIFACT, {"branch_metrics": [], "recommendation": {}})


@app.get("/api/staffing_recommendation", summary="Recommended employees per shift by branch")
def get_staffing_recommendation(branch: str = None):
    """Return recommended employees per shift per branch."""
    data = _load_artifact(config.STAFFING_ARTIFACT, {"recommendations": []})
    recs = data.get("recommendations", [])
    if branch:
        recs = [r for r in recs if branch.lower() in r.get("branch", "").lower()]
    return {"recommendations": recs}


@app.get("/api/coffee_milkshake_strategy", summary="Growth strategies for coffee and milkshakes")
def get_coffee_milkshake_strategy():
    """Return data-driven strategies and top products for coffee and milkshakes."""
    return _load_artifact(config.COFFEE_MILKSHAKE_STRATEGY_ARTIFACT, {"coffee": {}, "milkshake": {}, "growth_strategies": []})


@app.get("/api/tools/list", summary="List available tools for OpenClaw integration")
def list_tools():
    """Return tool names and parameters so OpenClaw can invoke them (e.g. via POST /tools/invoke or HTTP)."""
    return {
        "tools": [
            {"name": "combo_recommendations", "method": "GET", "path": "/api/combo_recommendations", "args": ["limit"]},
            {"name": "demand_forecast", "method": "GET", "path": "/api/demand_forecast", "args": ["branch"]},
            {"name": "expansion_feasibility", "method": "GET", "path": "/api/expansion_feasibility", "args": []},
            {"name": "staffing_recommendation", "method": "GET", "path": "/api/staffing_recommendation", "args": ["branch"]},
            {"name": "coffee_milkshake_strategy", "method": "GET", "path": "/api/coffee_milkshake_strategy", "args": []},
        ],
        "base_url": "http://localhost:8000",
    }


@app.get("/")
def root():
    return {
        "service": "Conut Chief of Operations Agent API",
        "docs": "http://127.0.0.1:8000/docs",
        "health": "http://127.0.0.1:8000/health",
        "api_tools": "http://127.0.0.1:8000/api/tools/list",
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "conut-ops-agent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
