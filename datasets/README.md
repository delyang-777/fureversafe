# FurEverSafe AI Chatbot Model

## Overview

FurEverSafe uses a custom fine-tuned language model to power its chatbot
assistant. The model helps users with dog adoption, pet care, training,
health advice, lost and found, veterinary appointments, and platform
navigation.

The production model is a 4-bit quantized GGUF file optimized for fast
CPU inference. It was created through a multi-stage pipeline: dataset
creation, LoRA fine-tuning, model merging, GGUF conversion, and
quantization.

## Model Architecture

| Property | Value |
|---|---|
| Base Model | TinyLlama/TinyLlama-1.1B-Chat-v1.0 |
| Parameters | 1.1 billion |
| Fine-tuning Method | LoRA (Low-Rank Adaptation) |
| Production Format | GGUF Q4_K_M (4-bit quantized) |
| Inference Engine | llama-cpp-python |
| Context Window | 512 tokens |

## Training

### Dataset

- **File**: `fureversafe_chatbot_training.jsonl`
- **Size**: 5,888 training examples
- **Format**: Instruction-Input-Output JSONL
- **Topics**: Dog adoption, pet care, training, health advice, lost and found,
  veterinary appointments, educational resources, platform navigation
- **Structure**: Each example contains a system instruction, user input
  (with paraphrase variations), and a detailed assistant response

### Fine-Tuning (LoRA)

The base TinyLlama model was fine-tuned using LoRA (Low-Rank Adaptation),
which trains a small set of adapter weights instead of modifying the full
model. This keeps training fast and memory-efficient.

| Hyperparameter | Value |
|---|---|
| LoRA Rank (r) | 8 |
| LoRA Alpha | 32 |
| LoRA Dropout | 0.05 |
| Target Modules | q_proj, v_proj |
| Bias | none |
| Task Type | CAUSAL_LM |
| PEFT Version | 0.19.1 |

The fine-tuned LoRA adapter is stored in `fureversafe_lora_model/` as
`adapter_model.safetensors` with its config in `adapter_config.json`.

### GGUF Conversion and Quantization

After fine-tuning, the LoRA adapter was merged back into the base model
and converted to GGUF format for fast CPU inference:

1. **Merge**: The LoRA adapter weights were merged into the base TinyLlama
   model to produce a single standalone model
2. **Convert to GGUF**: The merged model was converted to GGUF format
   (used by llama.cpp) producing `fureversafe_f16.gguf` (full precision)
3. **Quantize**: The F16 model was quantized to Q4_K_M (4-bit mixed
   precision) producing `fureversafe_q4_k_m.gguf`

Q4_K_M was chosen as the quantization method because it provides a good
balance between model quality and file size, with minimal quality loss
compared to the full precision model.

### Model Files

| File | Format | Size | Purpose |
|---|---|---|---|
| `ai_model/fureversafe_q4_k_m.gguf` | GGUF Q4_K_M | ~650 MB | Production (fast, low memory) |
| `ai_model/fureversafe_f16.gguf` | GGUF F16 | ~2.2 GB | Full precision reference |
| `fureversafe_lora_model/` | PEFT/LoRA | ~5 MB | Adapter weights (fallback) |

## Inference

The production system uses `llama-cpp-python` to load the Q4_K_M GGUF
model directly. If the GGUF file or library is unavailable, it falls back
to loading the LoRA adapter on top of the TinyLlama base model via
`transformers` + `peft`.

Key inference parameters:
- **Max tokens**: 200
- **Temperature**: 0.2 (low for consistent, factual responses)
- **Top-p**: 0.9
- **Repeat penalty**: 1.15
- **Stop tokens**: "User:", "\nUser" (prevents the model from continuing
  as the user)

## Evaluation

Model evaluation results are stored in the `evaluation/` folder.

## Project Structure

```
datasets/
  ai_model/
    fureversafe_q4_k_m.gguf       # Production model (4-bit quantized)
    fureversafe_f16.gguf           # Full precision GGUF
  fureversafe_lora_model/
    adapter_config.json            # LoRA configuration
    adapter_model.safetensors      # LoRA adapter weights
  evaluation/                      # Model evaluation results
  fureversafe_chatbot_training.jsonl  # Training dataset
  INSTRUCTIONS.md                  # Setup guide
  README.md                        # This file
```
