"""
Servico Admin — operacoes administrativas seguras e predefinidas (TR-04).
Extrai do handler HTTP a logica de acesso a dados, mantendo a rota apenas
como roteamento e delegacao (AP-05).
"""
import logging
from src.models.database import get_db

logger = logging.getLogger(__name__)


class AdminService:
    """Operacoes administrativas do sistema.

    Contem apenas acoes predefinidas e seguras — nunca executa SQL arbitrario
    enviado pelo cliente (TR-04)."""

    def reset_database(self):
        """Reseta o banco de dados, apagando os registros de todas as tabelas.

        A ordem importa: itens_pedido e pedidos sao apagados antes de produtos
        e usuarios, respeitando as chaves estrangeiras habilitadas na conexao."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")
        db.commit()
        logger.warning("Banco de dados resetado via AdminService")
