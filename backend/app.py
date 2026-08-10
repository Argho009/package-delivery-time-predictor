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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    # Load config
    app.config["SECRET_KEY"]                  = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"]     = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_POOL_RECYCLE"]     = config.SQLALCHEMY_POOL_RECYCLE
    app.config["SQLALCHEMY_POOL_TIMEOUT"]     = config.SQLALCHEMY_POOL_TIMEOUT

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(predict_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(analytics_bp)

    # Serve frontend static files
    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, "index.html")

    # Health check
    @app.route("/api/health")
    def health():
        from flask import jsonify
        from models.predict import models_available
        return jsonify({
            "status":          "ok",
            "models_loaded":   models_available(),
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
