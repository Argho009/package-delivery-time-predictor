"""
backend/models/train_llm.py — Fine-Tune 7B/8B Local LLM via 4-bit QLoRA
Optimized specifically for 6GB VRAM (NVIDIA RTX 3050 Laptop GPU).
Base Model: Qwen/Qwen2.5-7B-Instruct or meta-llama/Llama-3.1-8B-Instruct
Fine-tuned on DeliverAI Indian logistics instruction dataset for Q4 GGUF export to LM Studio.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone

# Auto-forward to venv
_venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    import subprocess
    _res = subprocess.run([_venv_python] + sys.argv)
    sys.exit(_res.returncode)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "deliverai_llm_instructions.jsonl")
OUTPUT_DIR = os.path.join(BASE_DIR, "models", "saved", "deliverai_7b_lora")


def check_prerequisites():
    """Verify required fine-tuning libraries and GPU availability."""
    print("=" * 70)
    print("  DELIVERAI — 7B/8B LOCAL LLM DOMAIN FINE-TUNING PIPELINE (QLoRA 4-BIT)")
    print("=" * 70)

    try:
        import torch
        cuda_ok = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if cuda_ok else "None (CPU only)"
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3) if cuda_ok else 0.0
        print(f"  • PyTorch:  {torch.__version__} (CUDA: {cuda_ok} - {gpu_name} [{vram_gb:.1f} GB VRAM])")
    except ImportError:
        print("  ❌ PyTorch not found.")
        return False

    required = ["transformers", "peft", "bitsandbytes", "datasets", "accelerate"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"\n  ⚠️  Missing packages for LLM fine-tuning: {', '.join(missing)}")
        print(f"  Install using:")
        print(f"     .\\venv\\Scripts\\python.exe -m pip install {' '.join(missing)} trl\n")
        return False

    if not os.path.exists(DATA_PATH):
        print(f"  ⚠️  Instruction dataset not found at: {DATA_PATH}")
        print("  Generating 5,000 logistics instruction pairs now...")
        import subprocess
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "data", "generate_llm_data.py")])

    return True


def train_7b_lora(
    base_model_name: str = "Qwen/Qwen2.5-7B-Instruct",
    epochs: int = 1,
    batch_size: int = 1,
    gradient_accumulation_steps: int = 16,
    learning_rate: float = 1.5e-4,
    lora_r: int = 16,
    lora_alpha: int = 32,
    max_seq_length: int = 512,
):
    """
    Run 4-bit QLoRA fine-tuning tailored specifically to fit 7B models inside 6GB VRAM.
    Uses:
      - 4-bit NormalFloat (NF4) double quantization
      - Gradient Checkpointing (saves ~60% activation VRAM)
      - Paged 8-bit AdamW optimizer
      - Micro batch size = 1 with gradient accumulation
    """
    import torch
    from datasets import load_dataset
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer

    print(f"\n[1/5] Configuring 4-Bit NF4 Quantization for 6GB VRAM envelope...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    print(f"[2/5] Loading 7B base model & tokenizer: {base_model_name}")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )

    # Enable gradient checkpointing to keep VRAM < 5.2 GB on RTX 3050
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    print(f"[3/5] Applying LoRA Adapter (rank={lora_r}, alpha={lora_alpha})...")
    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    print(f"[4/5] Loading dataset: {DATA_PATH}")
    dataset = load_dataset("json", data_files=DATA_PATH, split="train")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        num_train_epochs=epochs,
        logging_steps=10,
        save_strategy="epoch",
        fp16=True,
        optim="paged_adamw_8bit",
        gradient_checkpointing=True,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        max_seq_length=max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
    )

    print(f"[5/5] Launching GPU Fine-Tuning on RTX 3050...")
    trainer.train()

    print(f"\n[✓] Fine-tuning complete! Saving 7B LoRA weights to: {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"    You can now convert and quantize this adapter to Q4 GGUF for LM Studio!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DeliverAI 7B/8B QLoRA Fine-Tuning Pipeline")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-7B-Instruct",
                        help="Base 7B model (e.g. Qwen/Qwen2.5-7B-Instruct or meta-llama/Llama-3.1-8B-Instruct)")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs")
    args = parser.parse_args()

    if check_prerequisites():
        train_7b_lora(base_model_name=args.model, epochs=args.epochs)
