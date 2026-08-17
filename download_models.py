"""
Model Downloader Utility for Unmark.
Downloads open-source models (Qwen2.5, GPT-2) from ModelScope / HuggingFace.
"""

import argparse
import os
import sys
import urllib.request

MODELS_CONFIG = {
    "qwen": {
        "name": "Qwen/Qwen2.5-0.5B",
        "save_dir": "qwen_local",
        "files": [
            "config.json",
            "generation_config.json",
            "model.safetensors",
            "tokenizer_config.json",
            "tokenizer.json",
            "vocab.json",
            "merges.txt",
        ],
    },
    "gpt2": {
        "name": "gpt2",
        "save_dir": "gpt2_local",
        "files": [
            "config.json",
            "model.safetensors",
            "tokenizer.json",
            "vocab.json",
            "merges.txt",
        ],
    },
}


def download_model(model_key: str = "qwen"):
    if model_key not in MODELS_CONFIG:
        print(f"[!] Unknown model key: {model_key}. Available: {list(MODELS_CONFIG.keys())}")
        return

    cfg = MODELS_CONFIG[model_key]
    save_path = os.path.join(os.path.dirname(__file__), cfg["save_dir"])
    os.makedirs(save_path, exist_ok=True)

    print(f"[*] Downloading {cfg['name']} into {save_path} ...")
    base_url = f"https://www.modelscope.cn/api/v1/models/{cfg['name']}/repo?FilePath="

    for file_name in cfg["files"]:
        target_file = os.path.join(save_path, file_name)
        if os.path.exists(target_file) and os.path.getsize(target_file) > 0:
            print(f"  [✓] {file_name} already exists (skipping)")
            continue

        url = base_url + file_name
        print(f"  [↓] Downloading {file_name} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp, open(target_file, "wb") as f:
                f.write(resp.read())
            print(f"  [✓] {file_name} downloaded successfully.")
        except Exception as e:
            print(f"  [✗] Failed to download {file_name}: {e}")

    print(f"\n[+] {cfg['name']} setup complete in: {save_path}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download local models for Unmark.")
    parser.add_argument("--model", type=str, choices=["qwen", "gpt2"], default="qwen", help="Model to download")
    args = parser.parse_args()
    download_model(args.model)
