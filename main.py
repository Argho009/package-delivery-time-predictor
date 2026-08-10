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
import time
import webbrowser
import logging

# Ensure backend directory is on sys.path
ROOT_DIR    = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ["PYTHONPATH"] = BACKEND_DIR

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

    port = 5000
    url  = f"http://127.0.0.1:{port}"

    print(f"\n[+] Server starting at: {url}")
    print("    Press CTRL+C to stop the server\n")

    # Automatically open browser after 1.5s delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask dev server
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
