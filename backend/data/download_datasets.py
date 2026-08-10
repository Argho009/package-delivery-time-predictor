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

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

# ── Dataset definitions ──────────────────────────────────────────
DATASETS = [
    {
        "id":       "sujalsuthar/amazon-delivery-dataset",
        "slug":     "amazon_delivery",
        "label":    "Amazon Delivery Dataset (43,632 rows)",
    },
    {
        "id":       "datasetengineer/logistics-and-supply-chain-dataset",
        "slug":     "logistics_supply_chain",
        "label":    "Logistics & Supply Chain Dataset (10,000 rows)",
    },
    {
        "id":       "abbas829/global-superstore-sales-dataset",
        "slug":     "global_superstore",
        "label":    "Global Superstore Sales & Logistics (10,000 rows)",
    },
    {
        "id":       "prachi13/customer-analytics",
        "slug":     "ecom_shipment",
        "label":    "E-Commerce Shipment Prediction (10,000 rows)",
    },
    {
        "id":       "jacopoferretti/superstore-dataset",
        "slug":     "enhanced_superstore",
        "label":    "Enhanced Superstore Sales Dataset (9,994 rows)",
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
