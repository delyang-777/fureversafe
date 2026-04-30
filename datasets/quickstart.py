#!/usr/bin/env python3
"""
Quick Start Guide for FurEverSafe Chatbot Fine-Tuning
Run this script to set up and start fine-tuning on your mid-end laptop
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command with error handling"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✓ {description} completed successfully!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error: {e}\n")
        return False


def check_gpu():
    """Check if GPU is available"""
    print("\n📱 Checking GPU availability...")
    
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            print(f"✓ GPU found: {device_name}")
            print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            return True
        else:
            print("⚠️  No GPU detected. Will use CPU (much slower).")
            return False
    except ImportError:
        print("⚠️  PyTorch not installed yet. Will check after installation.")
        return None


def install_dependencies():
    """Install required dependencies"""
    print("\n" + "="*60)
    print("🔧 STEP 1: Installing Dependencies")
    print("="*60)
    
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118", 
         "Installing PyTorch with CUDA support"),
        ("pip install transformers datasets accelerate bitsandbytes", 
         "Installing Hugging Face packages"),
        ("pip install llama-factory", 
         "Installing LLaMA-Factory"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"⚠️  {desc} failed. Continuing...")


def prepare_dataset():
    """Prepare and validate dataset"""
    print("\n" + "="*60)
    print("📊 STEP 2: Preparing Dataset")
    print("="*60)
    
    # Check if dataset exists
    if not os.path.exists('fureversafe_chatbot_training.jsonl'):
        print("❌ Dataset file not found: fureversafe_chatbot_training.jsonl")
        print("   Make sure you're in the datasets directory!")
        return False
    
    # Validate dataset
    print("\n✓ Validating dataset...")
    result = subprocess.run(
        [sys.executable, 'dataset_utils.py', 'validate', 'fureversafe_chatbot_training.jsonl'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print("❌ Dataset validation failed!")
        return False
    
    # Analyze dataset
    print("\n✓ Analyzing dataset...")
    result = subprocess.run(
        [sys.executable, 'dataset_utils.py', 'analyze', 'fureversafe_chatbot_training.jsonl'],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    # Split dataset
    print("\n✓ Splitting dataset...")
    if not run_command(
        f"{sys.executable} dataset_utils.py split fureversafe_chatbot_training.jsonl --output-dir ./splits",
        "Splitting dataset"
    ):
        return False
    
    return True


def download_model():
    """Download the base model"""
    print("\n" + "="*60)
    print("🔽 STEP 3: Downloading Base Model")
    print("="*60)
    
    print("\n📝 Model: mistralai/Mistral-7B-Instruct-v0.1")
    print("   Size: ~14 GB (will be cached locally)")
    print("   Time: 10-30 minutes depending on internet speed")
    
    if not run_command(
        "huggingface-cli download mistralai/Mistral-7B-Instruct-v0.1",
        "Downloading model"
    ):
        return False
    
    return True


def start_training():
    """Start fine-tuning training"""
    print("\n" + "="*60)
    print("🚀 STEP 4: Starting Training")
    print("="*60)
    
    print("\n⚡ Training Configuration:")
    print("   Model: Mistral 7B")
    print("   Dataset: 20 examples (FurEverSafe domain-specific)")
    print("   Epochs: 3")
    print("   Batch Size: 4 (per-device)")
    print("   Effective Batch: 16 (with gradient accumulation)")
    print("   Learning Rate: 5e-5")
    print("   Estimated Time: 15-45 minutes")
    
    confirm = input("\n🔄 Start training? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Training cancelled.")
        return False
    
    if not run_command(
        "llamafactory-cli train llamafactory_config.yaml",
        "Training FurEverSafe Chatbot"
    ):
        return False
    
    return True


def test_model():
    """Test the fine-tuned model"""
    print("\n" + "="*60)
    print("🧪 STEP 5: Testing Fine-Tuned Model")
    print("="*60)
    
    test_script = '''
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

print("Loading fine-tuned model...")
model_path = "./fureversafe-mistral-tuned"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

print("\\n✓ Model loaded successfully!")

# Test prompts
test_prompts = [
    "How do I create a dog profile on FurEverSafe?",
    "My dog has been limping for 2 days. Should I be worried?",
    "I want to adopt a dog but I'm not sure what breed would be best for my apartment."
]

print("\\n📝 Testing model with sample prompts:\\n")

for prompt in test_prompts:
    print(f"Q: {prompt}")
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_length=256,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove the prompt from response
    response = response[len(prompt):].strip()
    
    print(f"A: {response[:200]}...\\n")

print("✓ Test complete!")
'''
    
    with open('test_model.py', 'w') as f:
        f.write(test_script)
    
    print("\n✓ Created test script: test_model.py")
    print("Run: python test_model.py")
    
    confirm = input("\n🔄 Run test now? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        run_command(f"{sys.executable} test_model.py", "Testing model")


def setup_flask_integration():
    """Create Flask integration code"""
    print("\n" + "="*60)
    print("🌐 STEP 6: Flask Integration")
    print("="*60)
    
    flask_code = '''
# Add to your FurEverSafe app.py

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load fine-tuned model
model_path = "./fureversafe-mistral-tuned"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

@app.route('/api/chatbot', methods=['POST'])
def chatbot_endpoint():
    """Chatbot API using fine-tuned model"""
    data = request.json
    user_message = data.get('message')
    
    inputs = tokenizer(user_message, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_length=512,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response[len(user_message):].strip()
    
    return jsonify({
        'response': response,
        'model': 'fureversafe-mistral-tuned'
    })
'''
    
    with open('flask_integration.py', 'w') as f:
        f.write(flask_code)
    
    print("\n✓ Created: flask_integration.py")
    print("Copy this code to your app.py for chatbot integration")


def main():
    """Main setup flow"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   FurEverSafe Chatbot Fine-Tuning Quick Start Guide      ║
║                                                           ║
║   Fine-tune Mistral 7B on your mid-end laptop            ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check prerequisites
    print("📋 Prerequisites:")
    print("   ✓ Python 3.8+")
    print("   ✓ 8GB+ RAM")
    print("   ✓ GPU with 6GB+ VRAM (NVIDIA recommended)")
    print("   ✓ 50GB+ free disk space")
    print("   ✓ Internet connection")
    
    confirm = input("\n✓ Ready to proceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Aborted.")
        return
    
    # Check GPU
    check_gpu()
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Prepare dataset
    if not prepare_dataset():
        print("❌ Dataset preparation failed!")
        return
    
    # Step 3: Download model
    if not download_model():
        print("❌ Model download failed!")
        return
    
    # Step 4: Start training
    if not start_training():
        print("❌ Training failed!")
        return
    
    # Step 5: Test model
    test_model()
    
    # Step 6: Flask integration
    setup_flask_integration()
    
    # Final message
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("""
Next steps:
1. Your fine-tuned model is in: ./fureversafe-mistral-tuned
2. Test it: python test_model.py
3. Integrate with Flask: Copy code from flask_integration.py
4. Deploy using Ollama or Flask API

For more details, see README.md
    """)


if __name__ == '__main__':
    main()
