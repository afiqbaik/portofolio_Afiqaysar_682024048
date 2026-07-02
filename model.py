import os
import logging
import time
from mysql.connector import pooling
from werkzeug.security import generate_password_hash
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._pool is None:
            if not Config.DB_USER:
                logger.warning("Database credentials are not configured; skipping pool creation")
                return
            self._create_pool()

    def _create_pool(self):
        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name="portfolio_pool",
                pool_size=5,
                pool_reset_session=True,
                **Config.MYSQL_CONFIG
            )
            self.ensure_schema()
        except Exception as e:
            logger.exception("Failed to create DB pool: %s", e)
            self._pool = None

    def get_connection(self):
        if self._pool is None:
            # try to create pool on-demand if credentials exist
            if not Config.DB_USER:
                raise RuntimeError("Database is not configured in this environment")
            self._create_pool()
            if self._pool is None:
                raise RuntimeError("Database pool unavailable")
        return self._pool.get_connection()

    def execute_query(self, query, params=None, fetch=False):
        start_time = time.time()
        if self._pool is None:
            raise RuntimeError("Database not available")
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid if cursor.lastrowid else True

            elapsed = time.time() - start_time
            logger.debug(f"Query executed in {elapsed:.3f}s: {query[:50]}...")
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def ensure_schema(self):
        if not Config.DB_USER or not Config.DB_PASSWORD:
            logger.warning("Database credentials are not configured; skipping schema bootstrap")
            return

        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role VARCHAR(50) DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()[0]
            if user_count == 0:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    ('admin', generate_password_hash('password123'), 'admin')
                )
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    nama_lengkap VARCHAR(255),
                    nama_panggilan VARCHAR(100),
                    tempat_lahir VARCHAR(100),
                    tanggal_lahir DATE,
                    email VARCHAR(255),
                    telepon VARCHAR(50),
                    universitas VARCHAR(255),
                    fakultas VARCHAR(255),
                    prodi VARCHAR(255),
                    semester VARCHAR(50),
                    alamat TEXT,
                    foto_url TEXT,
                    about_me TEXT,
                    cv_url TEXT,
                    social_links TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    posisi VARCHAR(255) NOT NULL,
                    perusahaan VARCHAR(255) NOT NULL,
                    durasi VARCHAR(100),
                    deskripsi TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    judul VARCHAR(255) NOT NULL,
                    deskripsi TEXT,
                    gambar_url TEXT,
                    link_project TEXT,
                    github_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    nama_skill VARCHAR(255) NOT NULL,
                    icon_class VARCHAR(255),
                    kategori VARCHAR(100),
                    level VARCHAR(50),
                    progress INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.exception("Schema bootstrap failed: %s", exc)
        finally:
            cursor.close()
            conn.close()
