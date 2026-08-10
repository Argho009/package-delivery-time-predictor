"""
database/db.py — SQLAlchemy instance (shared singleton)
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
