import os, time, logging
from huggingface_hub import snapshot_download

# MODEL_DIR = "/models/llama3b-rm"
MODEL_DIR = "/runpod-volume/models/llama3b-rm"

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # default to INFO level
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def confirm_model_downloaded():
    if not os.path.exists(MODEL_DIR):
        logging.info("Model not found. Starting download...")
        os.makedirs(MODEL_DIR, exist_ok=True)
        start_time = time.time()
        snapshot_download(repo_id="Ray2333/GRM-Llama3.2-3B-rewardmodel-ft", local_dir=MODEL_DIR,
                          local_dir_use_symlinks=False)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Download complete. Time taken: {elapsed_time:.2f} seconds.")
    else:
        logging.info("Model already exists, skipping download.")
        
    return MODEL_DIR
