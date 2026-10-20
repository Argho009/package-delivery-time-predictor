"""
download.py — Master Downloader for All Inland India Logistics Datasets & Prerequisites
AI-Based Package Delivery Time Prediction System (DeliverAI)

Downloads all real Indian logistics datasets from Kaggle:
1. Delhivery Logistics Courier Routes (santanukundu/delhivery-dataset)
2. Amazon India Sales & Shipping (thedevastator/unlock-profits-with-e-commerce-sales-data)
3. Food Delivery Real Trips (gauravmalik26/food-delivery-dataset)
4. Bangalore City Traffic & Travel Time Index (preethamgouda/banglore-city-traffic-dataset)
5. Indian Road Corridors & Accidents (sehaj1104/indian-road-accident-dataset-20222025)
6. Indian Railway Stations & Network (mansiaggarwal88/indian-railway-stations-and-routing-network)
7. Flipkart E-Commerce Orders (benroshan/ecommerce-data)
8. IMD Weather for Indian Cities (vanvalkenberg/historicalweatherdataforindiancities)

Usage:
    python download.py
"""

import os
import sys

# ── Auto-forward to project venv if invoked from system Python ───
_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    import subprocess
    _res = subprocess.run([_venv_python] + sys.argv)
    sys.exit(_res.returncode)

import time
import zipfile
import shutil
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
RAW_DIR = os.path.join(BACKEND_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Load .env
load_dotenv(os.path.join(ROOT_DIR, ".env"))


# ── Terminal Styling ─────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[36m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    RED     = "\033[31m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    WHITE   = "\033[37m"


def banner():
    print(f"\n{C.CYAN}{'═' * 76}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}  DELIVERAI — INLAND INDIA DATASET & PREREQUISITES DOWNLOADER{C.RESET}")
    print(f"{C.DIM}  Automated downloader for all 8 Indian logistics, traffic & freight datasets{C.RESET}")
    print(f"{C.CYAN}{'═' * 76}{C.RESET}\n")


def status(icon, text, color=C.WHITE):
    print(f"  {color}{icon}{C.RESET} {text}")


# ── All India Logistics Datasets ─────────────────────────────────
DATASETS = [
    {
        "id": "santanukundu/delhivery-dataset",
        "slug": "delhivery",
        "title": "Delhivery Logistics Courier Routes",
        "desc": "144k+ real Indian courier and freight routes (OSRM vs actual time)",
    },
    {
        "id": "thedevastator/unlock-profits-with-e-commerce-sales-data",
        "slug": "amazon_india",
        "title": "Amazon India Sales & Shipping",
        "desc": "128k+ real fulfillment records, expedited vs standard delivery",
    },
    {
        "id": "gauravmalik26/food-delivery-dataset",
        "slug": "food_delivery",
        "title": "Real Food & Grocery Last-Mile Delivery",
        "desc": "45.5k+ Indian restaurant delivery trips with GPS coords & traffic density",
    },
    {
        "id": "preethamgouda/banglore-city-traffic-dataset",
        "slug": "bangalore_traffic",
        "title": "Bangalore City Traffic & Speed Index",
        "desc": "8.9k+ area-level speed, travel time index, and congestion observations",
    },
    {
        "id": "sehaj1104/indian-road-accident-dataset-20222025",
        "slug": "road_accidents",
        "title": "Indian Road Network & Corridor Delays",
        "desc": "20k+ highway and urban road network traffic density & weather records",
    },
    {
        "id": "mansiaggarwal88/indian-railway-stations-and-routing-network",
        "slug": "railway_network",
        "title": "Indian Railway Stations & Freight Network",
        "desc": "8.9k+ Indian railway stations, junctions, and container rail corridors",
    },
    {
        "id": "benroshan/ecommerce-data",
        "slug": "flipkart_ecom",
        "title": "Flipkart / Indian E-Commerce Orders",
        "desc": "Multi-item domestic retail orders, weights, and categories",
    },
    {
        "id": "vanvalkenberg/historicalweatherdataforindiancities",
        "slug": "india_weather",
        "title": "IMD Historical Indian Cities Weather",
        "desc": "Multi-year precipitation, monsoon rainfall, and temperature delays",
    },
]


def check_environment():
    """Verify Kaggle credentials and core packages."""
    print(f"{C.BOLD}[1/3] Checking Authentication & Environment...{C.RESET}")

    username = os.getenv("KAGGLE_USERNAME", "")
    key = os.getenv("KAGGLE_KEY", "")
    cred_file = os.path.expanduser("~/.kaggle/kaggle.json")

    if username and key:
        status("✓", f"Kaggle API credentials found in .env ({username})", C.GREEN)
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"] = key
    elif os.path.exists(cred_file):
        status("✓", f"Kaggle credentials found at {cred_file}", C.GREEN)
    else:
        status("❌", "Kaggle credentials missing!", C.RED)
        print(f"      Please set KAGGLE_USERNAME and KAGGLE_KEY in .env")
        print(f"      Or place kaggle.json at ~/.kaggle/kaggle.json")
        sys.exit(1)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        status("✓", "Kaggle API successfully authenticated", C.GREEN)
        return api
    except Exception as e:
        status("❌", f"Kaggle authentication error: {e}", C.RED)
        sys.exit(1)


def download_all_datasets(api):
    """Download all datasets into backend/data/raw/."""
    print(f"\n{C.BOLD}[2/3] Downloading Indian Logistics Datasets...{C.RESET}")
    total = len(DATASETS)

    for idx, d in enumerate(DATASETS, 1):
        slug = d["slug"]
        ds_id = d["id"]
        title = d["title"]
        dest_dir = os.path.join(RAW_DIR, slug)
        os.makedirs(dest_dir, exist_ok=True)

        existing = [f for f in os.listdir(dest_dir) if not f.endswith(".tmp")]

        if existing:
            # Check if directory has CSVs
            has_csv = any(f.endswith(".csv") for f in existing)
            if has_csv:
                status("✓", f"[{idx}/{total}] {title} (already present in raw/{slug}/)", C.GREEN)
                continue

        status("⬇️ ", f"[{idx}/{total}] Downloading {title} ({ds_id})...", C.CYAN)
        t_start = time.time()
        try:
            api.dataset_download_files(ds_id, path=dest_dir, unzip=True)

            # Unzip any nested zips
            for f in os.listdir(dest_dir):
                if f.endswith(".zip"):
                    zip_path = os.path.join(dest_dir, f)
                    try:
                        with zipfile.ZipFile(zip_path, "r") as z:
                            z.extractall(dest_dir)
                        os.remove(zip_path)
                    except Exception:
                        pass

            elapsed = time.time() - t_start
            files = [f for f in os.listdir(dest_dir) if f.endswith(".csv") or f.endswith(".parquet")]
            status("✓", f"[{idx}/{total}] {title} downloaded ({len(files)} files, {elapsed:.1f}s)", C.GREEN)
        except Exception as e:
            status("⚠️ ", f"[{idx}/{total}] {title} download warning: {e}", C.YELLOW)


def verify_packages():
    """Verify that all required ML, DL, and web packages are installed."""
    print(f"\n{C.BOLD}[3/3] Verifying Installed Packages...{C.RESET}")

    pkgs = [
        ("sklearn", "Scikit-Learn (Core ML)"),
        ("xgboost", "XGBoost Regressor"),
        ("lightgbm", "LightGBM Regressor"),
        ("catboost", "CatBoost Regressor"),
        ("torch", "PyTorch (Deep Learning)"),
        ("pytorch_tabnet", "TabNet (Tabular Deep Learning)"),
        ("flask", "Flask Web Server"),
        ("pandas", "Pandas DataFrames"),
        ("numpy", "NumPy Vectorization"),
    ]

    for mod_name, label in pkgs:
        try:
            __import__(mod_name)
            status("✓", f"{label:35s} OK", C.GREEN)
        except ImportError:
            status("❌", f"{label:35s} NOT INSTALLED (Run: pip install -r requirements.txt)", C.RED)


def main():
    banner()
    api = check_environment()
    download_all_datasets(api)
    verify_packages()

    print(f"\n{C.CYAN}{'═' * 76}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}  ✅ ALL DATASETS & DEPENDENCIES DOWNLOADED AND READY!{C.RESET}")
    print(f"  Storage location: {RAW_DIR}")
    print(f"\n  Next Step:")
    print(f"    {C.BOLD}python train.py{C.RESET} — Automatically clean, merge & train all 16 models!")
    print(f"{C.CYAN}{'═' * 76}{C.RESET}\n")


if __name__ == "__main__":
    main()
