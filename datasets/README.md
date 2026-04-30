# FurEverSafe Chatbot Training Dataset

This dataset contains conversation examples for fine-tuning small LLM models for the FurEverSafe platform.

## Dataset Overview

- **Format**: JSONL (JSON Lines)
- **Total Examples**: 20 high-quality conversation pairs
- **File**: `fureversafe_chatbot_training.jsonl`
- **Topics**: Dog adoption, pet health, feature navigation, lost/found dogs, dog care, training
- **Model Size**: Optimized for 7B-13B parameter models
- **Hardware**: Mid-end laptops (8GB+ RAM, 6GB+ VRAM recommended)

## File Structure

Each line in the JSONL file contains a JSON object:

```json
{
  "instruction": "System prompt describing the chatbot's role",
  "input": "User's question or request",
  "output": "Assistant's response"
}
```

## Supported Models for Fine-Tuning

### Small Models (Recommended for Mid-End Laptops)
1. **Llama 2 7B** - Meta's open-source model
2. **Mistral 7B** - Optimized and faster
3. **Neural Chat 7B** - Intel's model
4. **Orca 2 7B** - Smaller but capable
5. **TinyLlama 1.1B** - Ultra-light option

### Medium Models (If you have 16GB+ VRAM)
- Llama 2 13B
- Mistral Medium
- Nous Hermes 13B

## Hardware Requirements

### Minimum (For Training)
- RAM: 8GB system RAM
- VRAM: 4GB GPU VRAM
- Storage: 20GB free space
- CPU: Intel i5/Ryzen 5 or better

### Recommended (For Better Performance)
- RAM: 16GB system RAM
- VRAM: 6-8GB GPU VRAM (NVIDIA)
- Storage: 50GB free space
- CPU: Intel i7/Ryzen 7 or better
- GPU: NVIDIA GTX 1660 or better

### Optimal
- RAM: 32GB+ system RAM
- VRAM: 12GB+ (RTX 3060 or better)
- SSD: 100GB+ NVMe
- GPU: NVIDIA RTX 3080/4070 or better

## Installation & Setup

### Step 1: Clone and Set Up
```bash
cd FurEverSafe
mkdir -p models
cd datasets
```

### Step 2: Install Required Tools

#### Option A: Using LLaMA Factory (Recommended)
```bash
pip install llama-factory
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Option B: Using Ollama (Easiest for Beginners)
```bash
# Download from https://ollama.ai
# Then just run: ollama run mistral
```

#### Option C: Using Text Generation WebUI
```bash
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui
pip install -r requirements.txt
```

### Step 3: Download Base Model
```bash
# Using Ollama (automatic)
ollama pull mistral

# OR using HuggingFace CLI
pip install huggingface-hub
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.1
```

## Converting Dataset Format

The JSONL format is ready-to-use, but here are conversions for different tools:

### Convert to CSV Format
```python
import json
import csv

with open('fureversafe_chatbot_training.jsonl', 'r') as f:
    with open('fureversafe_dataset.csv', 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(['instruction', 'input', 'output'])
        for line in f:
            obj = json.loads(line)
            writer.writerow([obj['instruction'], obj['input'], obj['output']])
```

### Convert for GPT Format (Chat Completion)
```python
import json

output = []
with open('fureversafe_chatbot_training.jsonl', 'r') as f:
    for line in f:
        obj = json.loads(line)
        output.append({
            "messages": [
                {"role": "system", "content": obj['instruction']},
                {"role": "user", "content": obj['input']},
                {"role": "assistant", "content": obj['output']}
            ]
        })

with open('fureversafe_gpt_format.jsonl', 'w') as f:
    for obj in output:
        f.write(json.dumps(obj) + '\n')
```

## Fine-Tuning Instructions

### Method 1: Using LLaMA Factory (Recommended)
```bash
# Install
pip install llama-factory

# Create config file (config.yaml)
# See config_example.yaml below

# Run training
llamafactory-cli train config.yaml
```

### Method 2: Using Ollama
```bash
# Create Modelfile
FROM mistral
PARAMETER temperature 0.7
PARAMETER num_ctx 4096
SYSTEM """You are FurEverSafe assistant..."""

# Fine-tune
ollama create fureversafe-model -f Modelfile
```

### Method 3: Using Hugging Face Transformers
```python
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TextDatasetForLanguageModeling
from transformers import Trainer, TrainingArguments

# Load dataset
dataset = load_dataset('json', data_files='fureversafe_chatbot_training.jsonl')

# Load model
model_name = "mistralai/Mistral-7B"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Training arguments
training_args = TrainingArguments(
    output_dir='./fureversafe-mistral',
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,  # Adjust for your GPU memory
    save_steps=100,
    save_total_limit=2,
    learning_rate=2e-5,
    warmup_steps=100,
    weight_decay=0.01,
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
)

trainer.train()
```

### Method 4: Using Axolotl
```bash
pip install axolotl

# Create config
# See axolotl_config.yaml

# Train
accelerate launch -m axolotl.cli.train axolotl_config.yaml
```

## Example Training Config Files

### LLaMA Factory Config (config.yaml)
```yaml
### Model Configuration
model_name_or_path: mistralai/Mistral-7B-Instruct-v0.1
template: mistral
cutoff_len: 1024

### Data Configuration
data_path: fureversafe_chatbot_training.jsonl

### Training Configuration
output_dir: ./fureversafe-mistral-tuned
overwrite_output_dir: true
per_device_train_batch_size: 4
gradient_accumulation_steps: 4
lr_scheduler_type: cosine
logging_steps: 10
save_steps: 100
learning_rate: 5.0e-5
num_train_epochs: 3
warmup_ratio: 0.1

### Optimization
fp16: true  # Enable mixed precision for faster training
max_grad_norm: 1.0

### Hardware
devices: [0]  # GPU device(s)
```

### Axolotl Config (axolotl_config.yaml)
```yaml
base_model: mistralai/Mistral-7B-Instruct-v0.1
model_type: mistral
tokenizer_type: mistral

datasets:
  - path: fureversafe_chatbot_training.jsonl
    type: alpaca

sequence_len: 1024
sample_packing: true
pad_to_sequence_len: true

micro_batch_size: 4
gradient_accumulation_steps: 4
num_epochs: 3
optimizer: adamw_bnb_8bit
lr_scheduler: cosine
learning_rate: 0.0001

output_dir: ./fureversafe-axolotl-tuned
save_steps: 100
eval_steps: 0
```

## Training Tips for Mid-End Hardware

### Memory Optimization
```python
# Reduce batch size for limited VRAM
per_device_train_batch_size = 2  # Start with 2, increase if possible
gradient_accumulation_steps = 4   # Effective batch size = 2 * 4 = 8

# Enable flash attention (faster memory usage)
# torch.backends.cuda.enable_flash_sdp(True)

# Use 8-bit optimization
# optimizer: adamw_bnb_8bit
```

### Training Duration
- **Small dataset (20 examples)**: 10-30 minutes
- **Learning rate**: Start with 5e-5, adjust based on loss
- **Epochs**: 3-5 recommended for small dataset
- **Gradient accumulation**: Simulate larger batches

### Expected Results
- **Training loss**: Should decrease over time
- **Perplexity**: Lower is better
- **Response quality**: Subjective but measurable

## Testing Fine-Tuned Model

### Using Ollama
```bash
# After fine-tuning
ollama create fureversafe-model -f Modelfile
ollama run fureversafe-model "How do I adopt a dog?"
```

### Using Python
```python
from transformers import pipeline

# Load fine-tuned model
pipe = pipeline(
    "text-generation",
    model="./fureversafe-mistral-tuned",
    device=0
)

# Test
response = pipe("How do I create a dog profile on FurEverSafe?", max_length=512)
print(response[0]['generated_text'])
```

### Evaluation Metrics
- BLEU score
- ROUGE score
- Human evaluation
- Perplexity
- Response length appropriateness

## Expanding the Dataset

### Adding More Examples
```python
import json

new_example = {
    "instruction": "You are a helpful FurEverSafe assistant...",
    "input": "New user question",
    "output": "Detailed response"
}

with open('fureversafe_chatbot_training.jsonl', 'a') as f:
    f.write(json.dumps(new_example) + '\n')
```

### Data Collection Sources
1. **User feedback**: Collect common questions
2. **Customer support**: Review FAQ and tickets
3. **Community forums**: Extract Q&A
4. **Domain expertise**: Write scenarios
5. **Edge cases**: Include challenging questions

### Quality Guidelines
- Clear, specific questions
- Detailed, accurate responses
- Conversational tone
- Helpful and relevant
- 2-3 sentences minimum
- No harmful content
- Factually accurate

## Deployment Options

### Option 1: Local Ollama
```bash
ollama serve
# Access at http://localhost:11434
```

### Option 2: Text Generation WebUI
```bash
python server.py
# Access at http://localhost:7860
```

### Option 3: Flask API (for FurEverSafe)
```python
from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)
pipe = pipeline("text-generation", model="./fureversafe-mistral-tuned")

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']
    response = pipe(message, max_length=512)
    return jsonify(response)

app.run()
```

## Troubleshooting

### Out of Memory
- Reduce batch size
- Use gradient checkpointing
- Enable 8-bit quantization
- Use smaller model (7B instead of 13B)
- Close other applications

### Slow Training
- Use fewer epochs
- Smaller sequence length (512 vs 2048)
- Reduce logging frequency
- Use GPU instead of CPU
- Enable flash attention

### Poor Response Quality
- Increase dataset size
- Train for more epochs
- Adjust learning rate
- Add domain-specific examples
- Fine-tune on similar domain

### Model Won't Load
- Check CUDA/PyTorch installation
- Verify model file exists
- Check file permissions
- Try CPU mode first

## Resources

- [LLaMA Factory Docs](https://github.com/hiyouga/LLaMA-Factory)
- [Ollama](https://ollama.ai/)
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Text Generation WebUI](https://github.com/oobabooga/text-generation-webui)
- [Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl)

## License

This dataset is provided for educational and research purposes for the FurEverSafe project.

## Contact & Support

For questions about the dataset or fine-tuning:
- Email: support@fureversafe.com
- GitHub: [FurEverSafe Repository]
- Discord: [FurEverSafe Community]
