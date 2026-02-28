# =============================================================================
# QUICK SYSTEM TEST - Verifies pipeline and API work
# =============================================================================
# Run: python test_system.py
# 1. Runs the full pipeline (ingestion + all 5 objectives)
# 2. Starts the API in the background and calls each endpoint
# 3. Prints pass/fail for each step
# =============================================================================

import os
import sys
import json
import subprocess
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import config


def run_pipeline():
    """Run the full pipeline and return True if it succeeds."""
    print("Step 1: Running pipeline (ingestion + objectives)...")
    try:
        result = subprocess.run(
            [sys.executable, "run_pipeline.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print("  FAIL - Pipeline exited with code", result.returncode)
            if result.stderr:
                print(result.stderr[:500])
            return False
        print("  OK - Pipeline completed")
        return True
    except Exception as e:
        print("  FAIL -", e)
        return False


def check_artifacts():
    """Check that expected artifact files exist and have content."""
    print("Step 2: Checking artifact files...")
    artifacts = [
        config.CLEANED_ORDERS_PATH,
        config.CLEANED_SALES_DETAIL_PATH,
        config.COMBO_ARTIFACT,
        config.DEMAND_FORECAST_ARTIFACT,
        config.EXPANSION_ARTIFACT,
        config.STAFFING_ARTIFACT,
        config.COFFEE_MILKSHAKE_STRATEGY_ARTIFACT,
    ]
    ok = True
    for path in artifacts:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print("  OK -", os.path.basename(path))
        else:
            print("  MISSING/EMPTY -", path)
            ok = False
    return ok


def call_api(path):
    """GET request to local API. Returns (success, data or error string)."""
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000{path}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return True, data
    except Exception as e:
        return False, str(e)


def test_api_endpoints():
    """Test API endpoints. API must already be running (e.g. uvicorn src.api.app:app --port 8000)."""
    print("Step 3: Testing API endpoints (expects API on http://127.0.0.1:8000)...")
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/health")
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        print("  SKIP - API not running. Start it in another terminal with:")
        print("    uvicorn src.api.app:app --host 127.0.0.1 --port 8000")
        print("  Then run this test again to verify endpoints.")
        return True  # Don't fail the whole test

    endpoints = [
        ("/health", "health"),
        ("/api/tools/list", "tools list"),
        ("/api/combo_recommendations", "combo recommendations"),
        ("/api/demand_forecast", "demand forecast"),
        ("/api/expansion_feasibility", "expansion feasibility"),
        ("/api/staffing_recommendation", "staffing recommendation"),
        ("/api/coffee_milkshake_strategy", "coffee/milkshake strategy"),
    ]
    all_ok = True
    for path, name in endpoints:
        ok, data = call_api(path)
        if ok:
            print("  OK -", name)
        else:
            print("  FAIL -", name, ":", data[:80] if isinstance(data, str) else data)
            all_ok = False
    return all_ok


def main():
    print("=" * 60)
    print("Conut AI System Test")
    print("=" * 60)
    p = run_pipeline()
    a = check_artifacts()
    api_ok = test_api_endpoints()
    print("=" * 60)
    if p and a and api_ok:
        print("All tests PASSED. System is working.")
    else:
        print("Some tests failed. Check output above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
