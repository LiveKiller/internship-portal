import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration for application."""
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-dev-key')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/internship_portal')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-dev-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size for uploads