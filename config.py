import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'), encoding='utf-8')


class Config:
    _default_secret = 'pechati5-secret-key-change-me'
    SECRET_KEY = os.getenv('SECRET_KEY', _default_secret)

    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() in ('1', 'true', 'yes')
    PERMANENT_SESSION_LIFETIME = 3600

    UPLOAD_ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf'}
    MAX_FIELD_NAME = 200
    MAX_FIELD_PHONE = 50
    MAX_FIELD_EMAIL = 200
    MAX_FIELD_MESSAGE = 5000
    MAX_FIELD_ADDRESS = 1000
    MAX_PARAMS_JSON_LENGTH = 10000

    # --- PostgreSQL ---
    _db_url = os.getenv('DATABASE_URL', 'postgresql://pechati7:pechati7@localhost:5432/pechati7')
    if _db_url.startswith('postgres://'):
        _db_url = 'postgresql://' + _db_url[len('postgres://'):]
    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', 5)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 10)),
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
    }

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.yandex.ru')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'pechati5tyumen@ya.ru')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_RECIPIENT = os.getenv('MAIL_RECIPIENT', 'pechati5tyumen@ya.ru')

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
