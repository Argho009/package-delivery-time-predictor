"""
app.py — Flask application factory
"""

import os
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import config
from database.db import db
from routes.predict import predict_bp
from routes.history import history_bp
from routes.analytics import analytics_bp
from routes.copilot import copilot_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    # Load config
    app.config["SECRET_KEY"]                     = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"]        = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config.DB_TYPE.lower() == "sqlite":
        from sqlalchemy.pool import NullPool
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "poolclass": NullPool,
            "connect_args": {"check_same_thread": False},
        }
    else:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": config.SQLALCHEMY_POOL_RECYCLE,
            "pool_timeout": config.SQLALCHEMY_POOL_TIMEOUT,
        }

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(predict_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(copilot_bp)

    # Serve frontend static files
    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if not path or path in ("index.html", "dashboard.html"):
            return send_from_directory(frontend_dir, "dashboard.html")
        if path and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, "dashboard.html")

    # Health check
    @app.route("/api/health")
    def health():
        from flask import jsonify
        from models.predict import models_available
        return jsonify({
            "status":          "ok",
            "models_loaded":   models_available(),
        })

    # Memory & GPU VRAM Purge Endpoint
    @app.route("/api/system/cleanup", methods=["GET", "POST"])
    def system_cleanup():
        from flask import jsonify
        from utils.memory_cleanup import clear_vram_and_ram, get_memory_stats
        before = get_memory_stats()
        clear_vram_and_ram(verbose=True)
        after = get_memory_stats()
        return jsonify({
            "status": "success",
            "message": "GPU VRAM and System RAM cleared successfully",
            "before": before,
            "after": after,
        })

    return app


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        db.create_all()
    application.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=config.DEBUG,
    )
