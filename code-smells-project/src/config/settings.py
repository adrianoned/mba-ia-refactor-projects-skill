"""
Configuracoes centralizadas da aplicacao.
Todas as credenciais e configuracoes sao lidas de variaveis de ambiente,
com fallback para valores seguros de desenvolvimento.
"""
import os
from pathlib import Path

# Carrega .env se disponivel (desenvolvimento local)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv nao instalado — usa env vars do sistema


class Settings:
    # --- Seguranca ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-me-please")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # --- Banco de Dados ---
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "loja.db")

    # --- Servidor ---
    PORT: int = int(os.getenv("PORT", "5000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # --- Constantes de Negocio ---
    CATEGORIAS_VALIDAS: list = [
        "informatica", "moveis", "vestuario",
        "geral", "eletronicos", "livros"
    ]

    STATUS_PEDIDO_VALIDOS: list = [
        "pendente", "aprovado", "enviado", "entregue", "cancelado"
    ]

    # Faixas de desconto para relatorio de vendas
    # (limite_faturamento, percentual_desconto)
    FAIXAS_DESCONTO: list = [
        (10000, 0.10),   # 10% para faturamento acima de R$ 10.000
        (5000, 0.05),    # 5% para faturamento acima de R$ 5.000
        (1000, 0.02),    # 2% para faturamento acima de R$ 1.000
    ]

    # --- Validacao de Campos ---
    PRODUTO_NOME_MIN: int = 2
    PRODUTO_NOME_MAX: int = 200
    USUARIO_SENHA_MIN: int = 6
    USUARIO_NOME_MIN: int = 2


settings = Settings()
