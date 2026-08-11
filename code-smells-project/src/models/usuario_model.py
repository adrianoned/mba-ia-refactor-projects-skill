"""
Model de Usuario — acesso a dados e autenticacao.
Senhas armazenadas com hash seguro (pbkdf2_hmac + salt) — TR-07.
"""
import hashlib
import os
import logging
from src.models.database import get_db

logger = logging.getLogger(__name__)


def hash_password(password: str) -> bytes:
    """Gera hash seguro com salt aleatorio usando PBKDF2-HMAC-SHA256.
    Retorna salt (32 bytes) + key (32 bytes) concatenados."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 100000
    )
    return salt + key


def verify_password(password: str, stored: bytes) -> bool:
    """Verifica senha contra hash armazenado."""
    salt = stored[:32]
    key = stored[32:]
    new_key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 100000
    )
    return new_key == key


def _usuario_to_dict(row, include_sensitive=False):
    """Serializacao de usuario — NUNCA expoe senha por padrao (TR-15)."""
    if row is None:
        return None
    data = {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }
    if include_sensitive:
        data["senha_hash"] = row["senha_hash"]
    return data


def find_all():
    """Lista todos os usuarios — sem campo de senha."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    rows = cursor.fetchall()
    return [_usuario_to_dict(row) for row in rows]


def find_by_id(usuario_id):
    """Busca usuario por ID — sem campo de senha."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    return _usuario_to_dict(row)


def find_by_email(email):
    """Busca usuario por email — inclui senha_hash para autenticacao."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    return _usuario_to_dict(row, include_sensitive=True) if row else None


def create(nome, email, senha, tipo="cliente"):
    """Cria usuario com senha hasheada — query parametrizada."""
    db = get_db()
    cursor = db.cursor()

    senha_hash = hash_password(senha)

    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
        (nome, email.lower().strip(), senha_hash, tipo),
    )
    db.commit()
    logger.info("Usuario criado: email='%s', tipo='%s'", email, tipo)
    return cursor.lastrowid


def authenticate(email, senha):
    """Autentica usuario por email e senha.
    Busca usuario pelo email, verifica hash da senha.
    Retorna dados do usuario (sem senha) ou None."""
    usuario = find_by_email(email)
    if usuario is None:
        logger.warning("Tentativa de login com email inexistente: '%s'", email)
        return None

    if not verify_password(senha, usuario["senha_hash"]):
        logger.warning("Senha invalida para usuario: '%s'", email)
        return None

    # Remove senha_hash do retorno
    del usuario["senha_hash"]
    logger.info("Login bem-sucedido: '%s'", email)
    return usuario
