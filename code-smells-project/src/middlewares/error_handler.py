"""
Middlewares da aplicacao.
Tratamento centralizado de erros — elimina try/except repetidos (TR-12).
"""
import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Registra handlers de erro centralizados na aplicacao."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": str(e) if str(e) else "Requisicao invalida", "sucesso": False}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso nao encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"erro": "Metodo nao permitido", "sucesso": False}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Erro interno do servidor")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
