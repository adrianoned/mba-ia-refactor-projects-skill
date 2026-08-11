"""
Model de Produto — acesso a dados da entidade Produto.
Todas as queries usam placeholders parametrizados (seguro contra SQL Injection).
"""
import logging
from src.models.database import get_db

logger = logging.getLogger(__name__)

# Constantes extraidas (TR-13)
CATEGORIAS_VALIDAS = [
    "informatica", "moveis", "vestuario",
    "geral", "eletronicos", "livros"
]


def _produto_to_dict(row):
    """Serializacao padronizada de produto — evita duplicacao (TR-10)."""
    if row is None:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def find_all():
    """Retorna todos os produtos ativos."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE ativo = 1")
    rows = cursor.fetchall()
    logger.info("Listando %d produtos", len(rows))
    return [_produto_to_dict(row) for row in rows]


def find_by_id(produto_id):
    """Busca produto por ID — query parametrizada."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    return _produto_to_dict(row)


def create(nome, descricao, preco, estoque, categoria="geral"):
    """Cria novo produto — query parametrizada."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
        "VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    logger.info("Produto criado: ID=%d, nome='%s'", cursor.lastrowid, nome)
    return cursor.lastrowid


def update(produto_id, nome, descricao, preco, estoque, categoria):
    """Atualiza produto existente — query parametrizada."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
        "estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()
    logger.info("Produto atualizado: ID=%d", produto_id)
    return True


def delete(produto_id):
    """Soft-delete — desativa produto ao inves de remover."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET ativo = 0 WHERE id = ?",
        (produto_id,),
    )
    db.commit()
    logger.info("Produto desativado: ID=%d", produto_id)
    return True


def search(termo=None, categoria=None, preco_min=None, preco_max=None):
    """Busca produtos com filtros dinamicos — query parametrizada (TR-02)."""
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM produtos WHERE ativo = 1"
    params = []

    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [_produto_to_dict(row) for row in rows]
