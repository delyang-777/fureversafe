import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://neondb_owner:npg_QjPwJ7TU4EfD@ep-misty-mouse-ambs5ztr-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings - INCREASED FOR VIDEOS
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 700 * 1024 * 1024  # 500MB for videos
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'}