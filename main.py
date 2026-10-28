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
os.environ["USE_TF"] = "0"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ── Auto-forward to project venv if invoked from system Python ───
_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    import subprocess
    proc = None
    try:
        proc = subprocess.Popen([_venv_python] + sys.argv, env=os.environ)
        code = proc.wait()
        sys.exit(code if code is not None else 0)
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C received. Terminating DeliverAI processes...")
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        sys.exit(0)
    except BaseException as _e:
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass
        sys.exit(1)

import time
import threading
import traceback
import webbrowser
import logging
import faulthandler

faulthandler.enable(file=sys.stderr)

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

    # ── Register Global Memory & GPU VRAM Cleanup Handlers ──
    from utils.memory_cleanup import register_exit_cleanup_handlers, clear_vram_and_ram
    register_exit_cleanup_handlers()

    check_and_prepare_environment()

    # Import Flask app factory
    from app import create_app
    app = create_app()

    port = int(os.environ.get("PORT", 7860 if os.environ.get("SPACE_ID") else 5000))
    url  = f"http://127.0.0.1:{port}"

    print(f"\n[+] Server starting at: {url}")
    print("    Press CTRL+C to stop the server and purge VRAM/RAM\n")

    # Automatically open browser after 1.5s delay
    def open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open(url)
        except Exception as e:
            logger.warning("Could not auto-open browser: %s", e)

    threading.Thread(target=open_browser, daemon=True, name="deliverai-browser-opener").start()

    # Start Flask dev server
    try:
        logger.info("Starting Flask application server on port %d...", port)
        app.run(host="0.0.0.0", port=port, debug=False, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n[!] Server stopped by user (Ctrl+C). Initiating resource purge...")
    except BaseException as e:
        logger.error("Flask server encountered critical error: %s (%s)", e, type(e))
        traceback.print_exc()
    finally:
        clear_vram_and_ram(verbose=True)
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from utils.memory_cleanup import clear_vram_and_ram
        clear_vram_and_ram(verbose=True)
        sys.exit(0)
    except BaseException as e:
        logger.error("Fatal exception in main(): %s", e)
        traceback.print_exc()
        try:
            from utils.memory_cleanup import clear_vram_and_ram
            clear_vram_and_ram(verbose=True)
        except Exception:
            pass
        sys.exit(1)

