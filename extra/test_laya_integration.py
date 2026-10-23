"""
extra/test_laya_integration.py — DeliverAI Laya Model Integration & Multi-Corridor Test Suite
Validates the local Laya Decision Engine (ModernBERT-421M) across diverse Indian logistics corridors.
"""

import os
import sys
import time

# Auto-forward to venv if run from system python
_venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    import subprocess
    _res = subprocess.run([_venv_python] + sys.argv)
    sys.exit(_res.returncode)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.slm_router import decide_model_with_slm


def run_tests():
    test_scenarios = [
        {
            "name": "Adverse Weather Monsoon Corridor",
            "origin": "Mumbai Port Trust",
            "destination": "Pune Logistics Park",
            "dist": 148.5,
            "traffic": "HEAVY",
            "weather": "RAIN",
            "w_data": {"temperature_celsius": 23, "precipitation_mm": 22.0},
            "legs": [{"leg": i, "distance_km": 25.0, "weather": "HEAVY_RAIN"} for i in range(1, 7)]
        },
        {
            "name": "Low-Visibility Winter Fog Corridor",
            "origin": "Amritsar Highway Terminal",
            "destination": "Delhi NCR Logistics Hub",
            "dist": 450.0,
            "traffic": "MODERATE",
            "weather": "FOG",
            "w_data": {"temperature_celsius": 11, "precipitation_mm": 0.0},
            "legs": [{"leg": i, "distance_km": 25.0, "weather": "FOG"} for i in range(1, 19)]
        },
        {
            "name": "National Long-Haul Freight Corridor",
            "origin": "Kolkata Freight Hub",
            "destination": "Delhi International Cargo Terminal",
            "dist": 1530.0,
            "traffic": "MODERATE",
            "weather": "CLEAR",
            "w_data": {"temperature_celsius": 29, "precipitation_mm": 0.0},
            "legs": [{"leg": i, "distance_km": 25.0, "weather": "CLEAR"} for i in range(1, 62)]
        },
        {
            "name": "Hyperlocal Intra-City Courier Corridor",
            "origin": "Connaught Place, New Delhi",
            "destination": "Noida Sector 62",
            "dist": 18.5,
            "traffic": "HEAVY",
            "weather": "CLEAR",
            "w_data": {"temperature_celsius": 27, "precipitation_mm": 0.0},
            "legs": [{"leg": 1, "distance_km": 18.5, "weather": "CLEAR"}]
        }
    ]

    print("\n" + "=" * 80)
    print("   DELIVERAI — LAYA DECISION ENGINE MULTI-CORRIDOR TEST SUITE")
    print("   Model: convaiinnovations/laya-typed-decisions (ModernBERT-large 421M)")
    print("=" * 80)

    total_time = 0.0
    for idx, sc in enumerate(test_scenarios, 1):
        t0 = time.time()
        res = decide_model_with_slm(
            origin=sc["origin"],
            destination=sc["destination"],
            distance_km=sc["dist"],
            traffic_level=sc["traffic"],
            weather_condition=sc["weather"],
            weather_data=sc["w_data"],
            legs=sc["legs"]
        )
        elapsed_ms = (time.time() - t0) * 1000
        total_time += elapsed_ms

        model_name = res["chosen_model"].upper()
        conf_pct = res.get("confidence_pct", "N/A")
        print(f"\n[Scenario {idx}] {sc['name']}")
        print(f"  • Corridor:       {sc['origin']} ➔ {sc['destination']} ({sc['dist']:.1f} km)")
        print(f"  • Conditions:     {sc['weather']} weather | {sc['traffic']} traffic")
        print(f"  • Engine Source:  {res['source']}")
        print(f"  • Chosen Model:   {model_name} ({conf_pct}% confidence)")
        print(f"  • Technical Reason: {res['reason']}")
        print(f"  • Leg Breakdown:  {len(res.get('leg_assignments', []))} legs dynamically routed")
        print(f"  • Inference Time: {elapsed_ms:.1f} ms")
        print("-" * 80)

    avg_time = total_time / len(test_scenarios)
    print(f"\n✓ ALL 4 CORRIDOR TESTS COMPLETED SUCCESSFULLY!")
    print(f"  • Average Inference Latency: {avg_time:.1f} ms per corridor")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_tests()
