"""
Gerenciamento de conexao com banco de dados SQLite.

Usa o padrao Flask 'g' para manter uma conexao por request,
eliminando o singleton global mutavel (AP-06).
"""
import sqlite3
from flask import g, current_app


def get_db():
    """Obtem conexao com banco de dados do contexto da request Flask.
    Cria uma nova conexao por request — sem estado global compartilhado."""
    if "db" not in g:
        db_path = current_app.config.get("DATABASE_PATH", "loja.db")
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        # Habilita foreign keys
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Fecha conexao com banco ao final da request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Registra handlers de banco de dados e cria tabelas se necessario."""
    app.teardown_appcontext(close_db)

    # Cria tabelas e seeds usando o contexto da aplicacao
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT DEFAULT '',
                preco REAL NOT NULL,
                estoque INTEGER NOT NULL DEFAULT 0,
                categoria TEXT DEFAULT 'geral',
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                tipo TEXT DEFAULT 'cliente',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pendente',
                total REAL NOT NULL DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)
        db.commit()

        # Seeds — dados iniciais se o banco estiver vazio
        cursor.execute("SELECT COUNT(*) FROM produtos")
        if cursor.fetchone()[0] == 0:
            _seed_database(cursor, db)


def _seed_database(cursor, db):
    """Popula banco de dados com dados iniciais de exemplo."""
    produtos = [
        ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
        ("Mouse Wireless", "Mouse sem fio ergonomico", 89.90, 50, "informatica"),
        ("Teclado Mecanico", "Teclado mecanico RGB", 299.90, 30, "informatica"),
        ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
        ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
        ("Cadeira Gamer", "Cadeira ergonomica", 1299.90, 8, "moveis"),
        ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
        ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
        ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
        ("Camiseta Dev", "Camiseta estampa codigo", 59.90, 100, "vestuario"),
    ]
    cursor.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        produtos,
    )

    # Senhas pre-hasheadas com pbkdf2_hmac para os seeds
    from src.models.usuario_model import hash_password

    usuarios = [
        ("Admin", "admin@loja.com", hash_password("admin123"), "admin"),
        ("Joao Silva", "joao@email.com", hash_password("123456"), "cliente"),
        ("Maria Santos", "maria@email.com", hash_password("senha123"), "cliente"),
    ]
    cursor.executemany(
        "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
        usuarios,
    )
    db.commit()
