"""
Servico de Health Check — verifica a saude do sistema sem expor dados sensiveis.
Extrai do handler HTTP a logica de acesso a dados (AP-05), mantendo a rota
apenas como roteamento e delegacao.
"""
import logging
import sqlite3
from src.models.database import get_db

logger = logging.getLogger(__name__)


class HealthService:
    """Verifica a saude do sistema e a conectividade do banco de dados.

    Retorna apenas informacoes nao sensiveis — nunca secret_key, db_path ou debug."""

    def check(self):
        """Retorna (dados, erro). dados e None se o banco falhar."""
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.execute("SELECT COUNT(*) FROM produtos")
            produtos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            usuarios = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            pedidos = cursor.fetchone()[0]

            return {
                "status": "ok",
                "database": "connected",
                "counts": {
                    "produtos": produtos,
                    "usuarios": usuarios,
                    "pedidos": pedidos,
                },
                "versao": "1.0.0",
            }, None
        except sqlite3.Error:
            logger.exception("Falha na conexao com banco de dados")
            return None, "Falha na conexao com banco"
