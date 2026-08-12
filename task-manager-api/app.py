"""Entry point da aplicacao — bootstrap e composicao.
Configuracoes externalizadas via config/ (TR-01)."""
import logging
from flask import Flask
from flask_cors import CORS
from database import db
from config.settings import settings
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from routes.category_routes import category_bp


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    _setup_logging(app)
    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(category_bp)

    @app.route("/health")
    def health():
        from datetime import datetime
        return {"status": "ok", "timestamp": str(datetime.now())}

    @app.route("/")
    def index():
        return {"message": "Task Manager API", "version": "2.0"}

    with app.app_context():
        db.create_all()

    return app


def _setup_logging(app):
    log_level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)
