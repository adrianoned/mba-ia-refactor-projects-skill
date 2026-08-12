"""Model de Usuario — acesso a dados e autenticacao.
Senhas com pbkdf2_hmac + salt (TR-07). Dados sensiveis nao expostos (TR-15)."""
from database import db
from datetime import datetime, timezone
import hashlib
import os as _os
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> bytes:
    """PBKDF2-HMAC-SHA256 com salt aleatorio de 32 bytes."""
    salt = _os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt + key


def verify_password(password: str, stored: bytes) -> bool:
    """Verifica senha contra hash armazenado."""
    salt = stored[:32]
    key = stored[32:]
    new_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return new_key == key


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)  # binary hash
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Serializacao SEM dados sensiveis (TR-15)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": str(self.created_at),
        }

    def set_password(self, pwd):
        """Hash seguro com PBKDF2 (TR-07)."""
        self.password = hash_password(pwd)

    def check_password(self, pwd):
        """Verifica senha contra hash armazenado (TR-07)."""
        return verify_password(pwd, self.password)

    def is_admin(self):
        return self.role == "admin"
