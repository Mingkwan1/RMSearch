import os
from huggingface_hub import snapshot_download

MODEL_DIR = "/models/llama3b-rm"

def confirm_model_downloaded():
    if not os.path.exists(MODEL_DIR):
        print("🔵 Downloading model...")
        snapshot_download(repo_id="Ray2333/GRM-Llama3.2-3B-rewardmodel-ft", local_dir=MODEL_DIR)
        print("✅ Download complete.")
    else:
        print("🟢 Model already exists, skipping download.")
    return MODEL_DIR
