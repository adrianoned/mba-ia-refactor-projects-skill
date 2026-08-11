"""
Controller de Usuario — logica de negocio para cadastro e autenticacao.
Validacao de email, senha e formato de dados centralizada (TR-11).
"""
import re
import logging
from src.models import usuario_model

logger = logging.getLogger(__name__)

# Constante de validacao de email
_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def listar_usuarios():
    """Lista todos os usuarios — dados sem senha."""
    usuarios = usuario_model.find_all()
    return usuarios, None


def buscar_usuario(usuario_id):
    """Busca usuario por ID — sem expor senha."""
    usuario = usuario_model.find_by_id(usuario_id)
    if usuario is None:
        return None, ["Usuario nao encontrado"]
    return usuario, None


def criar_usuario(dados):
    """Cria usuario com validacao completa de entrada (TR-11)."""
    erros = _validar_dados_usuario(dados)
    if erros:
        return None, erros

    # Verifica email duplicado
    existente = usuario_model.find_by_email(dados["email"])
    if existente:
        return None, ["Email ja cadastrado"]

    user_id = usuario_model.create(
        nome=dados["nome"],
        email=dados["email"],
        senha=dados["senha"],
        tipo=dados.get("tipo", "cliente"),
    )
    return {"id": user_id}, None


def login(dados):
    """Autentica usuario com email e senha."""
    email = dados.get("email", "").strip()
    senha = dados.get("senha", "")

    if not email or not senha:
        return None, ["Email e senha sao obrigatorios"]

    usuario = usuario_model.authenticate(email, senha)
    if usuario is None:
        return None, ["Email ou senha invalidos"]

    return usuario, None


def _validar_dados_usuario(dados):
    """Validacao centralizada de dados de usuario."""
    erros = []

    if not dados:
        return ["Dados invalidos"]

    nome = dados.get("nome", "").strip()
    if not nome:
        erros.append("Nome e obrigatorio")
    elif len(nome) < 2:
        erros.append("Nome deve ter no minimo 2 caracteres")

    email = dados.get("email", "").strip()
    if not email:
        erros.append("Email e obrigatorio")
    elif not _EMAIL_REGEX.match(email):
        erros.append("Formato de email invalido")

    senha = dados.get("senha", "")
    if not senha:
        erros.append("Senha e obrigatoria")
    elif len(senha) < 6:
        erros.append("Senha deve ter no minimo 6 caracteres")

    return erros
