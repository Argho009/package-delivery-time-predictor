"""
config.py — Application configuration loader
Reads from .env file and exposes typed config values.
Supports SQLite for zero-setup local testing when DB_TYPE=sqlite.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DEBUG: bool     = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    PORT: int       = int(os.getenv("FLASK_PORT", 5000))

    # ── Database ─────────────────────────────────────────────────
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")   # "sqlite" | "mysql"

    if DB_TYPE.lower() == "sqlite":
        SQLALCHEMY_DATABASE_URI: str = os.getenv(
            "DATABASE_URL",
            f"sqlite:///{os.path.join(BASE_DIR, 'delivery.db')}"
        )
    else:
        _DB_HOST:     str = os.getenv("DB_HOST", "localhost")
        _DB_PORT:     str = os.getenv("DB_PORT", "3306")
        _DB_USER:     str = os.getenv("DB_USER", "root")
        _DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
        _DB_NAME:     str = os.getenv("DB_NAME", "delivery_db")
        SQLALCHEMY_DATABASE_URI: str = os.getenv(
            "DATABASE_URL",
            f"mysql+pymysql://{_DB_USER}:{_DB_PASSWORD}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}?charset=utf8mb4"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_POOL_RECYCLE:         int = 280
    SQLALCHEMY_POOL_TIMEOUT:         int = 20

    SQLALCHEMY_ENGINE_OPTIONS: dict = (
        {} if DB_TYPE.lower() == "sqlite"
        else {"pool_recycle": 280, "pool_timeout": 20}
    )

    # Weather API (OpenWeather)
    OPENWEATHER_API_KEY: str  = os.getenv("OPENWEATHER_API_KEY", "")

    # ML model storage
    MODELS_DIR: str = os.path.join(BASE_DIR, "models", "saved")


config = Config()
