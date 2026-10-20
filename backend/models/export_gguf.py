"""
backend/models/export_gguf.py — Merge LoRA Adapter and Export to GGUF (Q4) for LM Studio
Takes the trained LoRA adapter from backend/models/saved/deliverai_7b_lora,
merges it with the base 7B model, and prepares GGUF Q4 export for LM Studio.
"""

import os
import sys
import argparse

_venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    import subprocess
    _res = subprocess.run([_venv_python] + sys.argv)
    sys.exit(_res.returncode)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LORA_PATH = os.path.join(BASE_DIR, "models", "saved", "deliverai_7b_lora")
MERGED_OUTPUT = os.path.join(BASE_DIR, "models", "saved", "deliverai_7b_merged")


def merge_lora_to_full(base_model_name: str = "Qwen/Qwen2.5-7B-Instruct"):
    """Merge LoRA weights back into the full 7B base model."""
    print("=" * 70)
    print("  DELIVERAI — MERGE 7B LORA ADAPTER FOR GGUF / Q4 QUANTIZATION")
    print("=" * 70)

    if not os.path.exists(LORA_PATH):
        print(f"❌ Error: LoRA adapter directory not found at: {LORA_PATH}")
        print("   Please run 'python backend/models/train_llm.py' first.")
        return False

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel

    print(f"[1/3] Loading base model: {base_model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="cpu",
        trust_remote_code=True,
    )

    print(f"[2/3] Merging LoRA adapter from: {LORA_PATH}...")
    model = PeftModel.from_pretrained(base_model, LORA_PATH)
    merged_model = model.merge_and_unload()

    print(f"[3/3] Saving merged 16-bit model to: {MERGED_OUTPUT}...")
    os.makedirs(MERGED_OUTPUT, exist_ok=True)
    merged_model.save_pretrained(MERGED_OUTPUT)
    tokenizer.save_pretrained(MERGED_OUTPUT)

    print("\n[✓] Merged 7B model saved successfully!")
    print("\nTo convert to GGUF and quantize to Q4 for LM Studio:")
    print("  1. Clone llama.cpp if not installed:")
    print("     git clone https://github.com/ggerganov/llama.cpp")
    print("  2. Convert merged model to GGUF:")
    print(f"     python llama.cpp/convert_hf_to_gguf.py \"{MERGED_OUTPUT}\" --outfile deliverai-7b-f16.gguf")
    print("  3. Quantize to Q4_K_M (fits ~4.2 GB VRAM):")
    print("     llama.cpp/llama-quantize deliverai-7b-f16.gguf deliverai-7b-q4_k_m.gguf q4_k_m")
    print("  4. Drop 'deliverai-7b-q4_k_m.gguf' into LM Studio models folder and run!")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DeliverAI 7B LoRA Merge & GGUF Preparation")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-7B-Instruct",
                        help="Base 7B model used during fine-tuning")
    args = parser.parse_args()

    merge_lora_to_full(base_model_name=args.model)
