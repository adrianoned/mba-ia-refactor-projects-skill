"""
Configuracoes centralizadas da aplicacao.
Todas as credenciais sao lidas de variaveis de ambiente.
"""
import os
from pathlib import Path

# Carrega .env se disponivel
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-me")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///tasks.db")

    # SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")

    # Constantes de dominio
    VALID_STATUSES: list = ["pending", "in_progress", "done", "cancelled"]
    VALID_ROLES: list = ["user", "admin", "manager"]
    VALID_PRIORITIES: range = range(1, 6)  # 1 a 5
    MIN_TITLE_LENGTH: int = 3
    MAX_TITLE_LENGTH: int = 200
    MIN_PASSWORD_LENGTH: int = 8
    DEFAULT_PRIORITY: int = 3
    DEFAULT_COLOR: str = "#000000"


settings = Settings()
