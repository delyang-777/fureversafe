# 🚀 FurEverSafe Dataset - Quick Reference

## What You Have

✅ **20 training examples** - FurEverSafe domain-specific chatbot data  
✅ **JSONL format** - Ready to use with any fine-tuning tool  
✅ **Mid-end laptop optimized** - Works on 8GB RAM + 6GB VRAM  
✅ **Complete setup guide** - From zero to production  

---

## Install (Copy & Paste)

```bash
cd FurEverSafe/datasets
pip install -r dataset_requirements.txt
python quickstart.py
```

---

## File Guide

| File | Purpose |
|------|---------|
| `fureversafe_chatbot_training.jsonl` | **The dataset** (use this!) |
| `README.md` | Full documentation |
| `SUMMARY.md` | Complete guide & checklist |
| `quickstart.py` | Automated setup wizard |
| `dataset_utils.py` | Convert/validate/split data |
| `llamafactory_config.yaml` | Training configuration |
| `axolotl_config.yaml` | Alternative training config |
| `dataset_requirements.txt` | All dependencies |

---

## Training in 4 Commands

```bash
# 1. Install
pip install -r dataset_requirements.txt

# 2. Download model (one-time, ~30 min)
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.1

# 3. Train (15-45 min)
llamafactory-cli train llamafactory_config.yaml

# 4. Test
python test_model.py
```

---

## Hardware Check

```bash
# Check GPU
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# Check VRAM
python -c "import torch; print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB')"
```

---

## Dataset Preview

```json
{
  "instruction": "You are a helpful assistant for FurEverSafe...",
  "input": "How do I adopt a dog?",
  "output": "Here's how to find and adopt your perfect dog..."
}
```

**Topics**: Dog adoption, health, training, lost dogs, feature help, general care

---

## Model Specs

- **Name**: Mistral 7B
- **Size**: 7 billion parameters
- **Memory**: ~20 GB total (model + training)
- **Training time**: 15-45 min
- **Speed**: ~1K tokens/sec inference

---

## Expected Training Output

```
Epoch 1/3:
  Step 10/30: loss=2.145
  Step 20/30: loss=1.876
  Step 30/30: loss=1.654
Epoch 2/3: ...
Epoch 3/3: ...
Training complete!
Model saved to ./fureversafe-mistral-tuned
```

---

## Use in Your App

### With Flask
```python
from transformers import pipeline

pipe = pipeline("text-generation", model="./fureversafe-mistral-tuned")

@app.route('/chat', methods=['POST'])
def chat():
    response = pipe(request.json['message'])
    return jsonify(response)
```

### With Ollama
```bash
ollama create fureversafe-model -f Modelfile
ollama run fureversafe-model "How do I adopt a dog?"
```

---

## Expand Dataset

```python
import json

new = {
    "instruction": "You are a helpful FurEverSafe assistant...",
    "input": "Your question",
    "output": "Your answer"
}

with open('fureversafe_chatbot_training.jsonl', 'a') as f:
    f.write(json.dumps(new) + '\n')
```

Then retrain: `llamafactory-cli train llamafactory_config.yaml`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Out of memory | Reduce `per_device_train_batch_size` to 2 |
| GPU not found | `pip install torch --force-reinstall` |
| Slow training | Close other apps, use SSD |
| Bad responses | Add more examples, train longer |
| Model won't load | Check disk space, file permissions |

---

## Cost & Time

| Item | Time | Cost |
|------|------|------|
| Setup | 10 min | Free |
| Model download | 30 min | Free |
| Training | 20-45 min | Free |
| **Total** | **~70 min** | **$0** |

---

## Next Steps

1. ✅ Install: `pip install -r dataset_requirements.txt`
2. ⬜ Download: `huggingface-cli download mistralai/Mistral-7B-Instruct-v0.1`
3. ⬜ Train: `llamafactory-cli train llamafactory_config.yaml`
4. ⬜ Test: `python test_model.py`
5. ⬜ Deploy: Integrate with Flask/Ollama

---

## Useful Commands

```bash
# Validate dataset
python dataset_utils.py validate fureversafe_chatbot_training.jsonl

# Analyze dataset
python dataset_utils.py analyze fureversafe_chatbot_training.jsonl

# Convert to CSV
python dataset_utils.py convert fureversafe_chatbot_training.jsonl --to csv

# Split train/val/test
python dataset_utils.py split fureversafe_chatbot_training.jsonl

# Run automated setup
python quickstart.py
```

---

## Resources

- 📖 Full guide: See `README.md`
- 📋 Checklist: See `SUMMARY.md`
- 🤖 Model: [Mistral 7B](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1)
- 🛠️ Trainer: [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
- 🚀 Ollama: [ollama.ai](https://ollama.ai/)

---

## Support

- Check `README.md` for detailed documentation
- See `SUMMARY.md` for complete troubleshooting
- Run `python quickstart.py` for guided setup
- Review config files for customization

---

**Ready? Start with:** `pip install -r dataset_requirements.txt`

**Questions?** Check SUMMARY.md → Troubleshooting section

**Let's go! 🚀**
