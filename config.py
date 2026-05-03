import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fureversafe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings - INCREASED FOR VIDEOS
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 700 * 1024 * 1024  # 500MB for videos
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'}

    # AI Chatbot Model Settings
    GGUF_MODEL_PATH = os.environ.get('GGUF_MODEL_PATH') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets', 'ai_model', 'fureversafe_q4_k_m.gguf')
    GGUF_N_GPU_LAYERS = int(os.environ.get('GGUF_N_GPU_LAYERS', -1))
    GGUF_N_CTX = int(os.environ.get('GGUF_N_CTX', 512))

    LORA_MODEL_PATH = os.environ.get('LORA_MODEL_PATH') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets', 'fureversafe_lora_model')
    LORA_BASE_MODEL = os.environ.get('LORA_BASE_MODEL') or 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'

    AI_MAX_NEW_TOKENS = int(os.environ.get('AI_MAX_NEW_TOKENS', 200))
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', 0.2))
    AI_SYSTEM_PROMPT = (
        "You are the FureverSafe AI assistant, dedicated to helping users with pet shelter information, adoption, and care. "
        "When the user greets you casually (hi, hello, hey, etc.), respond with a friendly short greeting and ask how you can help. "
        "Keep responses concise and well-structured. Use numbered steps only when explaining a process."
    )