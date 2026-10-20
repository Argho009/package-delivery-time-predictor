"""
main.py — Single Entry Point to Launch the Entire DeliverAI System
Run with:
    python main.py

What this script does:
1. Sets up backend Python path & environment.
2. Ensures database & trained ML models are ready (auto-seeds & trains if missing).
3. Launches the Flask Web Application at http://127.0.0.1:5000.
4. Opens your default web browser automatically.
"""

import os
import sys

# ── 1. Windows C-Runtime & OpenMP Stability Environment Variables ───
# Must be set BEFORE any C/C++ DLLs (Torch, XGBoost, CatBoost, LightGBM, Scipy) load
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["LOKY_MAX_CPU_COUNT"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONWARNINGS"] = "ignore"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ── Auto-forward to project venv if invoked from system Python ───
_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    import subprocess
    while True:
        try:
            _res = subprocess.run([_venv_python] + sys.argv, env=os.environ)
            if _res.returncode == 0:
                sys.exit(0)
            print(f"[main] Subprocess exited with code {_res.returncode}. Restarting in 2s...")
            import time
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n[!] Server stopped by user.")
            sys.exit(0)

import time
import threading
import traceback
import webbrowser
import logging
import faulthandler

_crash_log_file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_dump.log"), "a", encoding="utf-8")
faulthandler.enable(file=_crash_log_file)

# Ensure backend directory is on sys.path
ROOT_DIR    = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ["PYTHONPATH"] = BACKEND_DIR

import warnings
warnings.filterwarnings("ignore")
try:
    import joblib.parallel
    joblib.parallel.DEFAULT_BACKEND = "threading"
    if "threading" in joblib.parallel.BACKENDS:
        joblib.parallel.BACKENDS["loky"] = joblib.parallel.BACKENDS["threading"]
except Exception:
    pass

logging.basicConfig(level=logging.INFO, format="[main] %(message)s")
logger = logging.getLogger(__name__)


def check_and_prepare_environment():
    """Verify models and database exist, auto-create if missing."""
    models_dir   = os.path.join(BACKEND_DIR, "models", "saved")
    metrics_file = os.path.join(models_dir, "metrics.json")

    if not os.path.exists(metrics_file):
        logger.info("Trained models not found. Running dataset & ML training pipeline...")

        # Process / seed data if needed
        processed_csv = os.path.join(BACKEND_DIR, "data", "processed", "unified_delivery.csv")
        if not os.path.exists(processed_csv):
            logger.info("Processing raw datasets...")
            from data.process_datasets import main as process_main
            process_main()

        # Train models
        logger.info("Training ML models (Random Forest, XGBoost, Linear Regression)...")
        from models.train import train
        train()
        logger.info("ML Models trained successfully!")
    else:
        logger.info("Trained ML models verified OK.")


def main():
    print("=" * 65)
    print("  DeliverAI — AI Package Delivery Time Prediction System")
    print("=" * 65)

    check_and_prepare_environment()

    # Import Flask app factory
    from app import create_app
    app = create_app()

    port = int(os.environ.get("PORT", 7860 if os.environ.get("SPACE_ID") else 5000))
    url  = f"http://127.0.0.1:{port}"

    print(f"\n[+] Server starting at: {url}")
    print("    Press CTRL+C to stop the server\n")

    # Automatically open browser after 1.5s delay
    def open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open(url)
        except Exception as e:
            logger.warning("Could not auto-open browser: %s", e)

    threading.Thread(target=open_browser, daemon=True, name="deliverai-browser-opener").start()

    # Start Flask dev server with resilient keep-alive loop
    while True:
        try:
            logger.info("Starting Flask application server on port %d...", port)
            app.run(host="0.0.0.0", port=port, debug=False, threaded=True, use_reloader=False)
            logger.warning("Flask app.run() returned unexpectedly. Restarting in 1s...")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] Server stopped by user (Ctrl+C).")
            break
        except BaseException as e:
            logger.error("Flask server encountered critical error: %s (%s)", e, type(e))
            traceback.print_exc()
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        logger.error("Fatal exception in main(): %s", e)
        traceback.print_exc()

