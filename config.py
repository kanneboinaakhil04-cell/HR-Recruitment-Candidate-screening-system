import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hr_screening_secret_key_2026_academic_project')
    
    # Upload Folder
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload limit
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    # MySQL connection string format: mysql+pymysql://user:password@localhost/dbname
    # Falls back to local SQLite database if MYSQL_URI is not configured
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'hr_screening_db')
    
    # DB URI logic
    # Ensure database directory exists
    DB_DIR = os.path.join(BASE_DIR, 'database')
    os.makedirs(DB_DIR, exist_ok=True)

    DEFAULT_SQLITE_URI = f"sqlite:///{os.path.join(DB_DIR, 'hr_screening.db')}"
    
    # Use MySQL if explicitly enabled or configured, otherwise seamless SQLite DB
    USE_MYSQL = os.environ.get('USE_MYSQL', 'false').lower() == 'true'
    
    if USE_MYSQL:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    else:
        SQLALCHEMY_DATABASE_URI = DEFAULT_SQLITE_URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False
