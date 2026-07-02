import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


def _get_db_config():
    database_url = os.getenv('DATABASE_URL', '').strip()
    if database_url:
        parsed = urlparse(database_url)
        if parsed.scheme and parsed.hostname:
            return {
                'host': parsed.hostname,
                'port': parsed.port or 4000,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path.lstrip('/') or os.getenv('DB_NAME', 'Portofolio'),
            }

    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '4000')),
        'user': os.getenv('DB_USER', ''),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'Portofolio'),
    }


class Config:
    DB_CONFIG = _get_db_config()
    DB_HOST = DB_CONFIG['host']
    DB_PORT = int(DB_CONFIG['port'])
    DB_USER = DB_CONFIG['user']
    DB_PASSWORD = DB_CONFIG['password']
    DB_NAME = DB_CONFIG['database']

    MYSQL_CONFIG = {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME,
        'ssl_disabled': False,
        'ssl_verify_cert': True,
        'ssl_verify_identity': True,
        'autocommit': True,
        'charset': 'utf8mb4',
        'connection_timeout': 10,
    }

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

    RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
    RESEND_FROM = os.getenv('RESEND_FROM', os.getenv('EMAIL_FROM', 'Portfolio <onboarding@resend.dev>'))
    CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', os.getenv('EMAIL_TO', 'contact@example.com'))

    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'uploads'))