"""
data/download_datasets.py — Automated Kaggle dataset downloader
Requires: pip install kaggle
          ~/.kaggle/kaggle.json  OR  KAGGLE_USERNAME + KAGGLE_KEY env vars

Run from backend/ directory:
    python -m data.download_datasets
"""

import os
import sys
import subprocess
import zipfile
import shutil
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

# ── Dataset definitions (India-Specific Logistics) ───────────────
DATASETS = [
    {
        "id":       "santanukundu/delhivery-dataset",
        "slug":     "delhivery",
        "label":    "Delhivery Logistics Dataset (~144,800 rows)",
    },
    {
        "id":       "benroshan/ecommerce-data",
        "slug":     "flipkart_ecom",
        "label":    "Flipkart / Indian E-Commerce Orders",
    },
    {
        "id":       "thedevastator/unlock-profits-with-e-commerce-sales-data",
        "slug":     "amazon_india",
        "label":    "Amazon India Sales & Delivery Dataset (128,975 rows)",
    },
    {
        "id":       "vanvalkenberg/historicalweatherdataforindiancities",
        "slug":     "india_weather",
        "label":    "India Historical Cities Weather Data (IMD)",
    },
    {
        "id":       "gauravmalik26/food-delivery-dataset",
        "slug":     "food_delivery",
        "label":    "Food & Grocery Last-Mile Delivery (45,593 rows)",
    },
    {
        "id":       "preethamgouda/banglore-city-traffic-dataset",
        "slug":     "bangalore_traffic",
        "label":    "Bangalore City Traffic & Travel Time Index (8,936 rows)",
    },
    {
        "id":       "sehaj1104/indian-road-accident-dataset-20222025",
        "slug":     "road_accidents",
        "label":    "Indian Road Network & Corridor Congestion (20,000 rows)",
    },
    {
        "id":       "mansiaggarwal88/indian-railway-stations-and-routing-network",
        "slug":     "railway_network",
        "label":    "Indian Railway Stations & Freight Corridors (8,990 rows)",
    },
]

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(RAW_DIR, exist_ok=True)


def check_kaggle():
    """Verify kaggle CLI is available and credentials are set."""
    try:
        result = subprocess.run(["kaggle", "--version"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("kaggle CLI not responding")
        print(f"[download] Kaggle CLI: {result.stdout.strip()}")
    except FileNotFoundError:
        print("[download] ❌ Kaggle CLI not found.")
        print("           Install it: pip install kaggle")
        print("           Then place kaggle.json at ~/.kaggle/kaggle.json")
        sys.exit(1)

    # Check credentials
    cred_path = os.path.expanduser("~/.kaggle/kaggle.json")
    has_env   = os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")
    if not os.path.exists(cred_path) and not has_env:
        print("[download] ❌ Kaggle credentials not found.")
        print(f"           Create {cred_path} from https://www.kaggle.com/account")
        sys.exit(1)

    print("[download] ✅ Kaggle credentials OK")


def download_dataset(dataset_id: str, slug: str, label: str):
    dest_dir = os.path.join(RAW_DIR, slug)

    if os.path.exists(dest_dir) and os.listdir(dest_dir):
        print(f"[download] ⏭️  {label} already downloaded, skipping.")
        return

    print(f"\n[download] ⬇️  Downloading: {label}")
    os.makedirs(dest_dir, exist_ok=True)

    result = subprocess.run(
        ["kaggle", "datasets", "download",
         "-d", dataset_id,
         "--path", dest_dir,
         "--unzip"],
        capture_output=False,
        text=True,
    )

    if result.returncode != 0:
        print(f"[download] ❌ Failed to download {dataset_id}")
        shutil.rmtree(dest_dir, ignore_errors=True)
    else:
        # Check if any nested zip files exist and extract them
        for item in os.listdir(dest_dir):
            if item.endswith(".zip"):
                zip_path = os.path.join(dest_dir, item)
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        zf.extractall(dest_dir)
                    os.remove(zip_path)
                except Exception as e:
                    print(f"[download] Warning extracting {item}: {e}")

        files = os.listdir(dest_dir)
        print(f"[download] ✅ Downloaded: {files}")


def main():
    print("=" * 60)
    print("  AI Delivery Prediction — Dataset Downloader")
    print("=" * 60)

    check_kaggle()

    for ds in DATASETS:
        download_dataset(ds["id"], ds["slug"], ds["label"])

    print("\n[download] ✅ All downloads complete.")
    print(f"[download]    Raw data stored in: {RAW_DIR}")
    print("\n[download] Next step: python -m data.process_datasets")


if __name__ == "__main__":
    main()
