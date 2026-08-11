"""
Controller de Produto — logica de negocio para operacoes de produto.
Validacoes, regras de categoria e formatacao centralizadas aqui.
"""
import logging
from src.models import produto_model
from src.config.settings import settings

logger = logging.getLogger(__name__)


def listar_produtos():
    """Retorna todos os produtos."""
    produtos = produto_model.find_all()
    return produtos, None


def buscar_produto(produto_id):
    """Busca produto por ID."""
    produto = produto_model.find_by_id(produto_id)
    if produto is None:
        return None, ["Produto nao encontrado"]
    return produto, None


def buscar_produtos(termo=None, categoria=None, preco_min=None, preco_max=None):
    """Busca produtos com filtros."""
    resultados = produto_model.search(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados)}, None


def criar_produto(dados):
    """Cria produto apos validar dados de entrada (TR-11)."""
    erros = _validar_dados_produto(dados)
    if erros:
        return None, erros

    produto_id = produto_model.create(
        nome=dados["nome"],
        descricao=dados.get("descricao", ""),
        preco=dados["preco"],
        estoque=dados["estoque"],
        categoria=dados.get("categoria", "geral"),
    )
    return {"id": produto_id}, None


def atualizar_produto(produto_id, dados):
    """Atualiza produto existente apos validacao."""
    produto = produto_model.find_by_id(produto_id)
    if produto is None:
        return None, ["Produto nao encontrado"]

    erros = _validar_dados_produto(dados)
    if erros:
        return None, erros

    produto_model.update(
        produto_id=produto_id,
        nome=dados["nome"],
        descricao=dados.get("descricao", ""),
        preco=dados["preco"],
        estoque=dados["estoque"],
        categoria=dados.get("categoria", "geral"),
    )
    return {"mensagem": "Produto atualizado"}, None


def deletar_produto(produto_id):
    """Remove (soft-delete) produto."""
    produto = produto_model.find_by_id(produto_id)
    if produto is None:
        return None, ["Produto nao encontrado"]

    produto_model.delete(produto_id)
    return {"mensagem": "Produto deletado"}, None


def _validar_dados_produto(dados):
    """Validacao centralizada de dados de produto (TR-10, TR-11)."""
    erros = []

    if not dados:
        return ["Dados invalidos"]

    nome = dados.get("nome", "")
    if not nome:
        erros.append("Nome e obrigatorio")
    elif len(nome) < settings.PRODUTO_NOME_MIN:
        erros.append(f"Nome muito curto (min. {settings.PRODUTO_NOME_MIN} caracteres)")
    elif len(nome) > settings.PRODUTO_NOME_MAX:
        erros.append(f"Nome muito longo (max. {settings.PRODUTO_NOME_MAX} caracteres)")

    preco = dados.get("preco")
    if preco is None:
        erros.append("Preco e obrigatorio")
    elif not isinstance(preco, (int, float)) or preco < 0:
        erros.append("Preco nao pode ser negativo")

    estoque = dados.get("estoque")
    if estoque is None:
        erros.append("Estoque e obrigatorio")
    elif not isinstance(estoque, int) or estoque < 0:
        erros.append("Estoque nao pode ser negativo")

    categoria = dados.get("categoria", "geral")
    if categoria not in settings.CATEGORIAS_VALIDAS:
        erros.append(f"Categoria invalida. Validas: {settings.CATEGORIAS_VALIDAS}")

    return erros
