"""
Entry point da aplicacao — apenas composicao e bootstrap.
NENHUMA rota, logica de negocio ou configuracao hardcoded aqui.
"""
import logging
from flask import Flask
from flask_cors import CORS
from src.config.settings import settings
from src.models.database import init_db
from src.views.routes import register_routes
from src.middlewares.error_handler import register_error_handlers


def create_app():
    """Fabrica da aplicacao — composicao de todos os componentes."""
    app = Flask(__name__)

    # Configuracoes via env vars (TR-01)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    app.config["DATABASE_PATH"] = settings.DATABASE_PATH

    # CORS
    CORS(app)

    # Logging estruturado (TR-14)
    _setup_logging(app)

    # Banco de dados (TR-06 — conexao por request via Flask g)
    init_db(app)

    # Rotas (organizadas por Blueprint)
    register_routes(app)

    # Error handlers (centralizados — TR-12)
    register_error_handlers(app)

    return app


def _setup_logging(app):
    """Configura logging estruturado com niveis apropriados."""
    log_level = logging.DEBUG if app.config["DEBUG"] else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.info("Aplicacao iniciada — DEBUG=%s", app.config["DEBUG"])


if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
