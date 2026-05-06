"""
download_gguf.py
Run this on your LOCAL machine after the Kaggle notebook finishes.
It downloads fureversafe-f16.gguf directly into your ai_model/ folder.

Requirements:
    pip install kaggle
    Place your kaggle.json at: C:\\Users\\fosta\\.kaggle\\kaggle.json
    (Get it from https://www.kaggle.com/settings → API → Create New Token)
"""

import os
import sys
import subprocess
import zipfile
import shutil

# ── CONFIG ────────────────────────────────────────────────────────────────────
KAGGLE_USERNAME  = "your_kaggle_username"   # ← change this
NOTEBOOK_SLUG    = "your_notebook_slug"     # ← change this (the URL slug of your notebook)
GGUF_FILENAME    = "fureversafe-f16.gguf"
JSONL_FILENAME   = "fureversafe_clean.jsonl"

PROJECT_ROOT     = os.path.dirname(os.path.abspath(__file__))
AI_MODEL_DIR     = os.path.join(PROJECT_ROOT, "ai_model")
DATASETS_DIR     = os.path.join(PROJECT_ROOT, "datasets")
DOWNLOAD_DIR     = os.path.join(PROJECT_ROOT, "_kaggle_download")
# ─────────────────────────────────────────────────────────────────────────────

def check_kaggle_credentials():
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_json):
        print("❌  kaggle.json not found at:", kaggle_json)
        print()
        print("   1. Go to https://www.kaggle.com/settings")
        print("   2. Scroll to 'API' section → 'Create New Token'")
        print("   3. Save the downloaded kaggle.json to:", kaggle_json)
        sys.exit(1)
    print("✓  kaggle.json found")

def check_kaggle_installed():
    try:
        import kaggle
        print("✓  kaggle package found")
    except ImportError:
        print("Installing kaggle package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "-q"])
        print("✓  kaggle installed")

def download_output():
    import kaggle

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(AI_MODEL_DIR, exist_ok=True)
    os.makedirs(DATASETS_DIR, exist_ok=True)

    kernel_ref = f"{KAGGLE_USERNAME}/{NOTEBOOK_SLUG}"
    print(f"\nDownloading output from kernel: {kernel_ref}")
    print("(This may take a few minutes for the 1.17 GB GGUF...)\n")

    kaggle.api.kernels_output(kernel_ref, path=DOWNLOAD_DIR)

    # ── Find and move the GGUF ────────────────────────────────────────────────
    gguf_dest = os.path.join(AI_MODEL_DIR, GGUF_FILENAME)
    gguf_found = False

    for root, dirs, files in os.walk(DOWNLOAD_DIR):
        for fname in files:
            fpath = os.path.join(root, fname)
            # Handle zip archive (Kaggle sometimes wraps outputs)
            if fname.endswith(".zip"):
                print(f"Extracting {fname}...")
                with zipfile.ZipFile(fpath, "r") as z:
                    z.extractall(DOWNLOAD_DIR)
                continue
            if fname == GGUF_FILENAME:
                print(f"Moving {fname} → {gguf_dest}")
                shutil.move(fpath, gguf_dest)
                gguf_found = True
            elif fname == JSONL_FILENAME:
                jsonl_dest = os.path.join(DATASETS_DIR, JSONL_FILENAME)
                print(f"Moving {fname} → {jsonl_dest}")
                shutil.move(fpath, jsonl_dest)

    if not gguf_found:
        # Second pass after zip extraction
        for root, dirs, files in os.walk(DOWNLOAD_DIR):
            for fname in files:
                if fname == GGUF_FILENAME:
                    shutil.move(os.path.join(root, fname), gguf_dest)
                    gguf_found = True

    if gguf_found:
        size_mb = os.path.getsize(gguf_dest) / (1024 * 1024)
        print(f"\n✅  {GGUF_FILENAME} saved to: {gguf_dest}  ({size_mb:.1f} MB)")
    else:
        print("\n⚠️  GGUF file not found in kernel output.")
        print("   Make sure Step 10 in your notebook ran successfully.")
        print(f"   Downloaded files: {os.listdir(DOWNLOAD_DIR)}")

    # Cleanup
    shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)

def print_next_steps(success=True):
    print()
    print("─" * 60)
    print("Next steps:")
    print(f"  1. GGUF is in:   {os.path.join(AI_MODEL_DIR, GGUF_FILENAME)}")
    print(f"  2. Update your chatbot_service.py / ai_server.py to point")
    print(f"     MODEL_PATH to that file")
    print(f"  3. Restart the chatbot server")
    print("─" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("FurEverSafe GGUF Downloader")
    print("=" * 60)

    if KAGGLE_USERNAME == "your_kaggle_username":
        print("❌  Edit download_gguf.py and set KAGGLE_USERNAME and NOTEBOOK_SLUG first!")
        print()
        print("   KAGGLE_USERNAME: your Kaggle username (e.g. 'johndoe')")
        print("   NOTEBOOK_SLUG:   the notebook URL slug")
        print("   e.g. https://kaggle.com/johndoe/fureversafe-retrain")
        print("                                    ^^^^^^^^^^^^^^^^^^^^ this part")
        sys.exit(1)

    check_kaggle_credentials()
    check_kaggle_installed()
    download_output()
    print_next_steps()
