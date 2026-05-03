"""
download_gguf.py
Downloads fureversafe_q4_k_m.gguf from your Kaggle notebook output.
Prompts where to save it.

Setup (one-time):
  1. Go to https://www.kaggle.com/settings → API → Create New Token
  2. Place the downloaded kaggle.json at: C:\\Users\\<you>\\.kaggle\\kaggle.json
  3. Run: python download_gguf.py
"""

import os, sys, shutil

KAGGLE_USER    = "kimmykimho"
NOTEBOOK_SLUG  = "kaggle-convert-gguf"
GGUF_FILE      = "fureversafe_q4_k_m.gguf"

# ── Prompt where to save ─────────────────────────────────────────────────────
default = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets")
answer  = input(f"Save to (press Enter for '{default}'): ").strip()
save_dir = answer if answer else default
os.makedirs(save_dir, exist_ok=True)
dest = os.path.join(save_dir, GGUF_FILE)

if os.path.exists(dest):
    print(f"✅  Already exists: {dest}  ({os.path.getsize(dest)/1024**2:.0f} MB)")
    sys.exit(0)

# ── Check kaggle.json ────────────────────────────────────────────────────────
kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
if not os.path.exists(kaggle_json):
    print("❌  kaggle.json not found.")
    print("    1. Go to https://www.kaggle.com/settings → API → Create New Token")
    print(f"   2. Move kaggle.json to: {kaggle_json}")
    sys.exit(1)

# ── Download ─────────────────────────────────────────────────────────────────
try:
    import kaggle
except ImportError:
    os.system(f"{sys.executable} -m pip install kaggle -q")
    import kaggle

tmp = os.path.join(save_dir, "_tmp_gguf")
os.makedirs(tmp, exist_ok=True)

print(f"Downloading {GGUF_FILE} ...")
try:
    kaggle.api.kernels_output(f"{KAGGLE_USER}/{NOTEBOOK_SLUG}", path=tmp)
except Exception as e:
    print(f"❌  {e}")
    shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(1)

# Move the file
for root, _, files in os.walk(tmp):
    for f in files:
        if f == GGUF_FILE:
            shutil.move(os.path.join(root, f), dest)
            break

shutil.rmtree(tmp, ignore_errors=True)

if os.path.exists(dest):
    print(f"✅  Saved to: {dest}  ({os.path.getsize(dest)/1024**2:.0f} MB)")
else:
    print("❌  File not found in output. Make sure Cell 6 (quantize) ran in Kaggle.")
