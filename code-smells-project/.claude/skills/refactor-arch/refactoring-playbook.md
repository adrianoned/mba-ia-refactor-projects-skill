# Playbook de Refatoração

Padrões concretos de transformação para cada anti-pattern do catálogo, com exemplos de código antes/depois.

---

## Índice de Transformações

| # | Transformação | Anti-Pattern Alvo | Severidade |
|---|---|---|---|
| TR-01 | Externalizar Credenciais | AP-01 Hardcoded Credentials | CRITICAL |
| TR-02 | Parametrizar Queries SQL | AP-02 SQL Injection | CRITICAL |
| TR-03 | Separar God Class por Domínio | AP-03 God Class/Module | CRITICAL |
| TR-04 | Remover Endpoint de SQL Arbitrário | AP-04 Raw SQL Endpoint | CRITICAL |
| TR-05 | Extrair Lógica para Controller | AP-05 Business Logic in Routes | HIGH |
| TR-06 | Substituir Estado Global por DI | AP-06 Global Mutable State | HIGH |
| TR-07 | Corrigir Hash de Senhas | AP-07 Insecure Password | HIGH |
| TR-08 | Converter Callbacks para Async/Await | AP-08 Callback Hell | HIGH |
| TR-09 | Resolver N+1 Queries | AP-09 N+1 Queries | MEDIUM |
| TR-10 | Eliminar Código Duplicado | AP-10 Duplicate Code | MEDIUM |
| TR-11 | Adicionar Validação de Input | AP-11 Missing Validation | MEDIUM |
| TR-12 | Substituir Bare Except | AP-12 Bare Except/Empty Catch | MEDIUM |
| TR-13 | Extrair Magic Numbers/Strings | AP-13 Magic Numbers | LOW |
| TR-14 | Substituir Print por Logger | AP-14 Print as Logging | LOW |
| TR-15 | Filtrar Dados Sensíveis em Respostas | AP-15 Exposed Sensitive Data | HIGH |
| TR-16 | Atualizar APIs Deprecated | AP-16 Deprecated APIs | MEDIUM |
| TR-17 | Separar Side Effects | AP-17 Mixed Concerns | MEDIUM |

---

## TR-01: Externalizar Credenciais

**Alvo**: AP-01 — Hardcoded Credentials

### Python — Antes
```python
# app.py
app = Flask(__name__)
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True

# database.py
db_path = "loja.db"
```

### Python — Depois
```python
# config/settings.py
import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-me")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///loja.db")

settings = Settings()

# app.py
from config.settings import settings
app = Flask(__name__)
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["DEBUG"] = settings.DEBUG
```

### Node.js — Antes
```javascript
// utils.js
const config = {
    dbUser: "admin_master",
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    port: 3000
};
```

### Node.js — Depois
```javascript
// config/settings.js
require('dotenv').config();
const settings = {
    dbUser: process.env.DB_USER || 'dev_user',
    dbPass: process.env.DB_PASS || 'dev_pass',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'pk_test_xxx',
    port: process.env.PORT || 3000,
};
module.exports = { settings };
```

---

## TR-02: Parametrizar Queries SQL

**Alvo**: AP-02 — SQL Injection

### Python (SQLite) — Antes
```python
# models.py — VULNERÁVEL a SQL Injection
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco) VALUES ('" +
    nome + "', '" + descricao + "', " + str(preco) + ")"
)
cursor.execute(
    "SELECT * FROM produtos WHERE nome LIKE '%" + termo + "%'"
)
```

### Python (SQLite) — Depois
```python
# models/produto_model.py — SEGURO com queries parametrizadas
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))

cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)",
    (nome, descricao, preco)
)

cursor.execute(
    "SELECT * FROM produtos WHERE nome LIKE ?",
    (f"%{termo}%",)
)
```

### Python (SQLite com múltiplos filtros dinâmicos) — Depois
```python
def buscar_produtos(termo=None, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
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
    return cursor.fetchall()
```

### Node.js (sqlite3) — Antes
```javascript
// VULNERÁVEL — concatenação de strings
db.get("SELECT * FROM users WHERE email = '" + email + "'", (err, row) => { ... });
```

### Node.js (sqlite3) — Depois
```javascript
// SEGURO — placeholders parametrizados
db.get("SELECT * FROM users WHERE email = ?", [email], (err, row) => { ... });
```

---

## TR-03: Separar God Class por Domínio

**Alvo**: AP-03 — God Class / God Module

### Python — Antes
```python
# models.py (350 linhas, 4 domínios misturados)
def get_todos_produtos(): ...
def criar_produto(...): ...
def get_todos_usuarios(): ...
def criar_usuario(...): ...
def login_usuario(...): ...
def criar_pedido(...): ...
def get_pedidos_usuario(...): ...
def relatorio_vendas(): ...
```

### Python — Depois
```python
# models/produto_model.py (~80 linhas)
class Produto:
    @staticmethod
    def find_all(): ...
    @staticmethod
    def find_by_id(id): ...
    @staticmethod
    def create(nome, descricao, preco, estoque, categoria): ...
    @staticmethod
    def update(id, **kwargs): ...
    @staticmethod
    def delete(id): ...
    @staticmethod
    def search(termo, categoria=None, preco_min=None, preco_max=None): ...

# models/usuario_model.py (~60 linhas)
class Usuario:
    @staticmethod
    def find_all(): ...
    @staticmethod
    def find_by_id(id): ...
    @staticmethod
    def create(nome, email, senha_hash, tipo): ...
    @staticmethod
    def authenticate(email, senha_hash): ...

# models/pedido_model.py (~80 linhas)
class Pedido:
    @staticmethod
    def create(usuario_id, itens, total): ...
    @staticmethod
    def find_by_usuario(usuario_id): ...
    @staticmethod
    def find_all(): ...
    @staticmethod
    def update_status(pedido_id, status): ...

# controllers/relatorio_controller.py (~40 linhas)
class RelatorioController:
    def gerar_relatorio_vendas(self): ...
```

### Node.js — Antes
```javascript
// AppManager.js (140 linhas — tudo em um lugar)
class AppManager {
    constructor() { /* init DB */ }
    initDb() { /* cria todas as tabelas */ }
    setupRoutes(app) {
        app.post('/api/checkout', ...);  // checkout com nested callbacks
        app.get('/api/admin/financial-report', ...);  // nested loops
        app.delete('/api/users/:id', ...); // delete sem cleanup
    }
}
```

### Node.js — Depois
```javascript
// models/Course.js
class Course {
    constructor(db) { this.db = db; }
    findById(id) { ... }
    findAll() { ... }
}

// models/User.js
class User {
    constructor(db) { this.db = db; }
    findById(id) { ... }
    findByEmail(email) { ... }
    create(data) { ... }
    delete(id) { ... }
}

// models/Enrollment.js
class Enrollment {
    constructor(db) { this.db = db; }
    create(userId, courseId) { ... }
    findByUser(userId) { ... }
}

// controllers/checkoutController.js
class CheckoutController {
    constructor(userModel, courseModel, enrollmentModel, paymentService) {
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentService = paymentService;
    }
    async execute(userData, courseId) { ... }
}

// routes/index.js
module.exports = (app, controllers) => {
    app.post('/api/checkout', (req, res) => { ... });
    app.get('/api/admin/financial-report', (req, res) => { ... });
};

// app.js
const db = new sqlite3.Database(':memory:');
const userModel = new User(db);
const courseModel = new Course(db);
const checkoutController = new CheckoutController(userModel, courseModel, ...);
```

---

## TR-04: Remover Endpoint de SQL Arbitrário

**Alvo**: AP-04 — Raw SQL Execution Endpoint

### Antes
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)  # EXECUTA QUALQUER SQL!
    ...
```

### Depois
**Simplesmente REMOVA o endpoint inteiro.** Se for necessário para admin, crie endpoints específicos com comandos predefinidos:

```python
# services/admin_service.py — a operação vive no SERVICE (não na rota)
import logging
from src.models.database import get_db

logger = logging.getLogger(__name__)


class AdminService:
    def reset_database(self):
        """Reset seguro — operação predefinida, sem SQL arbitrário."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")
        db.commit()
        logger.warning("Banco de dados resetado via AdminService")
```

```python
# views/routes.py — a rota apenas delega (SEM get_db/cursor/commit inline)
from src.services.admin_service import AdminService

@admin_bp.route("/admin/reset-db", methods=["POST"])
@require_admin
def reset_database():
    """Endpoint específico para reset — sem SQL arbitrário e sem lógica na rota."""
    AdminService().reset_database()
    return jsonify({"mensagem": "Banco resetado"}), 200
```

> **ATENÇÃO (causa raiz de reincidência)**: deixar `get_db()`, `cursor.execute(...)` e `commit()` diretamente no handler da rota — mesmo com operações predefinidas — NÃO resolve o problema por inteiro. Isso mantém a violação (Business Logic in Routes). Qualquer operação administrativa deve viver em um service dedicado (`AdminService`); a rota apenas instancia o service e delega.

---

## TR-05: Extrair Lógica para Controller

**Alvo**: AP-05 — Business Logic in Controllers/Routes

### Python — Antes
```python
# controllers.py — validação e regras misturadas com HTTP
def criar_produto():
    dados = request.get_json()
    # Validação inline (20 linhas)
    if not dados: return jsonify(...), 400
    if "nome" not in dados: return jsonify(...), 400
    if preco < 0: return jsonify(...), 400
    categorias_validas = ["informatica", "moveis", ...]
    if categoria not in categorias_validas: return jsonify(...), 400
    # ...
    id = models.criar_produto(nome, descricao, preco, estoque, categoria)
    print("Produto criado com ID: " + str(id))  # log misturado
    return jsonify({"dados": {"id": id}}), 201
```

### Python — Depois
```python
# controllers/produto_controller.py
class ProdutoController:
    CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

    def criar_produto(self, dados):
        """Lógica de negócio pura — sem dependência HTTP"""
        erros = self._validar_criacao(dados)
        if erros:
            return None, erros
        produto_id = ProdutoModel.create(
            nome=dados["nome"],
            descricao=dados.get("descricao", ""),
            preco=dados["preco"],
            estoque=dados["estoque"],
            categoria=dados.get("categoria", "geral")
        )
        logger.info(f"Produto criado: ID={produto_id}")
        return {"id": produto_id}, None

    def _validar_criacao(self, dados):
        erros = []
        if not dados.get("nome") or len(dados["nome"]) < 2:
            erros.append("Nome é obrigatório (mín. 2 caracteres)")
        if dados.get("preco", -1) < 0:
            erros.append("Preço não pode ser negativo")
        if dados.get("estoque", -1) < 0:
            erros.append("Estoque não pode ser negativo")
        if dados.get("categoria") and dados["categoria"] not in self.CATEGORIAS_VALIDAS:
            erros.append(f"Categoria inválida. Válidas: {self.CATEGORIAS_VALIDAS}")
        return erros

# views/routes.py
@produto_bp.route("/produtos", methods=["POST"])
def criar_produto():
    dados, erros = controller.criar_produto(request.get_json())
    if erros:
        return jsonify({"erro": erros[0], "sucesso": False}), 400
    return jsonify({"dados": dados, "sucesso": True}), 201
```

---

## TR-06: Substituir Estado Global por DI

**Alvo**: AP-06 — Global Mutable State

### Python — Antes
```python
# database.py
db_connection = None  # GLOBAL MUTÁVEL

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
    return db_connection
```

### Python — Depois
```python
# database.py
import sqlite3
from flask import g, current_app

def get_db():
    """Obtém conexão do contexto da aplicação Flask"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_URL'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """Registra handlers de DB na aplicação"""
    app.teardown_appcontext(close_db)
```

### Node.js — Antes
```javascript
// utils.js
let globalCache = {};
let totalRevenue = 0;

function logAndCache(key, data) {
    globalCache[key] = data;  // MUTA ESTADO GLOBAL!
}
```

### Node.js — Depois
```javascript
// services/cacheService.js
class CacheService {
    constructor() {
        this.cache = new Map();
    }
    set(key, data) { this.cache.set(key, data); }
    get(key) { return this.cache.get(key); }
}

// app.js — injetado via construtor
const cacheService = new CacheService();
const checkoutController = new CheckoutController(..., cacheService);
```

---

## TR-07: Corrigir Hash de Senhas

**Alvo**: AP-07 — Insecure Password Handling

### Python — Antes
```python
# Login com senha em plaintext no banco
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email +
    "' AND senha = '" + senha + "'"
)

# Usando MD5
import hashlib
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

### Python — Depois
```python
# Usando hashlib com salt
import hashlib
import os

def hash_password(password):
    """Gera hash seguro com salt aleatório"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000
    )
    return salt + key

def verify_password(password, stored):
    """Verifica senha contra hash armazenado"""
    salt = stored[:32]
    key = stored[32:]
    new_key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000
    )
    return new_key == key

# Uso
user = Usuario.find_by_email(email)
if user and verify_password(senha, user.password_hash):
    return user  # Login OK
```

### Node.js — Antes
```javascript
// Crypto caseira INSEGURA
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

### Node.js — Depois
```javascript
// bcrypt ou crypto.scrypt
const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    return new Promise((resolve, reject) => {
        crypto.scrypt(password, salt, 64, (err, derivedKey) => {
            if (err) reject(err);
            resolve(salt + ':' + derivedKey.toString('hex'));
        });
    });
}

async function verifyPassword(password, stored) {
    const [salt, key] = stored.split(':');
    return new Promise((resolve, reject) => {
        crypto.scrypt(password, salt, 64, (err, derivedKey) => {
            if (err) reject(err);
            resolve(key === derivedKey.toString('hex'));
        });
    });
}
```

---

### Regras adicionais (Aplicáveis a qualquer linguagem)

1. **Nunca use senha default com fallback** — padrões como `password || '123456'` (Node.js) ou `dados.get("senha", "123456")` (Python). Exija a senha do usuário e valide presença/complexidade.
2. **Hasheie também as senhas dos seeds** — dados iniciais gravados como `'123'`, `'admin'`, `'senha123'` em texto puro também são problemas. Aplique `hashPassword()`/`hash_password()` antes de persistir no seed.
3. **Verifique TODOS os pontos de persistência de senha** — criação de usuário, seed, migração e reset de senha devem passar pelo mesmo hash.

---

## TR-08: Converter Callbacks para Async/Await

**Alvo**: AP-08 — Callback Hell / Pyramid of Doom

### Node.js — Antes
```javascript
// Aninhamento profundo — 4 níveis de callback
app.post('/api/checkout', (req, res) => {
    this.db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
        if (err || !course) return res.status(404).send("Curso não encontrado");
        this.db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
            if (err) return res.status(500).send("Erro DB");
            // Callback dentro de callback dentro de callback...
            this.db.run("INSERT INTO enrollments ...", function(err) {
                this.db.run("INSERT INTO payments ...", function(err) {
                    this.db.run("INSERT INTO audit_logs ...", (err) => {
                        res.status(200).json({ msg: "Sucesso" });
                    });
                });
            });
        });
    });
});
```

### Node.js — Depois
```javascript
// Promisify + async/await
const util = require('util');

class Database {
    constructor(db) {
        this.db = db;
        // Promisify métodos do sqlite3
        this.get = util.promisify(db.get).bind(db);
        this.run = util.promisify(db.run).bind(db);
        this.all = util.promisify(db.all).bind(db);
    }
}

// No controller
async checkout(userData, courseId) {
    const course = await this.db.get(
        "SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]
    );
    if (!course) throw new Error("Curso não encontrado");

    let user = await this.db.get(
        "SELECT id FROM users WHERE email = ?", [userData.email]
    );
    if (!user) {
        const result = await this.db.run(
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [userData.name, userData.email, userData.passwordHash]
        );
        user = { id: result.lastID };
    }

    const payment = await this.paymentService.process(userData.card, course.price);
    if (!payment.success) throw new Error("Pagamento recusado");

    const enrResult = await this.db.run(
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        [user.id, courseId]
    );
    await this.db.run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [enrResult.lastID, course.price, 'PAID']
    );
    await this.db.run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [`Checkout curso ${courseId} por ${user.id}`]
    );

    return { enrollment_id: enrResult.lastID };
}
```

---

## TR-09: Resolver N+1 Queries

**Alvo**: AP-09 — N+1 Queries

### Python — Antes
```python
def get_pedidos_usuario(usuario_id):
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    rows = cursor.fetchall()
    for row in rows:  # N queries adicionais dentro do loop!
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (row["id"],))
        itens = cursor2.fetchall()
        for item in itens:
            cursor3 = db.cursor()
            cursor3.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
            prod = cursor3.fetchone()
```

### Python — Depois
```python
def get_pedidos_usuario(usuario_id):
    cursor = db.cursor()

    # 1 query: pedidos
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    pedidos = cursor.fetchall()
    pedido_ids = [p["id"] for p in pedidos]

    if not pedido_ids:
        return []

    # 1 query: todos os itens de uma vez
    placeholders = ",".join(["?" for _ in pedido_ids])
    cursor.execute(
        f"SELECT * FROM itens_pedido WHERE pedido_id IN ({placeholders})",
        pedido_ids
    )
    itens = cursor.fetchall()

    # 1 query: todos os produtos de uma vez
    produto_ids = list(set(i["produto_id"] for i in itens))
    placeholders = ",".join(["?" for _ in produto_ids])
    cursor.execute(
        f"SELECT id, nome FROM produtos WHERE id IN ({placeholders})",
        produto_ids
    )
    produtos = {p["id"]: p["nome"] for p in cursor.fetchall()}

    # Montagem em memória (O(n)) — sem queries adicionais
    itens_por_pedido = {}
    for item in itens:
        itens_por_pedido.setdefault(item["pedido_id"], []).append(item)

    result = []
    for pedido in pedidos:
        pedido_dict = dict(pedido)
        pedido_dict["itens"] = [
            {**dict(i), "produto_nome": produtos.get(i["produto_id"], "Desconhecido")}
            for i in itens_por_pedido.get(pedido["id"], [])
        ]
        result.append(pedido_dict)
    return result
```

---

## TR-10: Eliminar Código Duplicado

**Alvo**: AP-10 — Duplicate Code (DRY Violation)

### Antes
```python
# Duplicado em get_todos_pedidos() E get_pedidos_usuario()
pedido = {
    "id": row["id"],
    "usuario_id": row["usuario_id"],
    "status": row["status"],
    "total": row["total"],
    "criado_em": row["criado_em"],
    "itens": []
}
cursor2 = db.cursor()
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
# ...mesmo código repetido em duas funções
```

### Depois
```python
# Função helper extraída — usada em ambos os lugares
def _serializar_pedido(row, db):
    pedido = {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
        "itens": _buscar_itens_pedido(row["id"], db)
    }
    return pedido

def _buscar_itens_pedido(pedido_id, db):
    cursor = db.cursor()
    cursor.execute(
        """SELECT ip.*, p.nome as produto_nome
           FROM itens_pedido ip
           LEFT JOIN produtos p ON ip.produto_id = p.id
           WHERE ip.pedido_id = ?""",
        (pedido_id,)
    )
    return [dict(row) for row in cursor.fetchall()]

def get_todos_pedidos():
    rows = cursor.fetchall()
    return [_serializar_pedido(row, db) for row in rows]

def get_pedidos_usuario(usuario_id):
    rows = cursor.fetchall()
    return [_serializar_pedido(row, db) for row in rows]
```

---

## TR-11: Adicionar Validação de Input

**Alvo**: AP-11 — Missing Input Validation

### Antes
```python
def criar_usuario():
    dados = request.get_json()
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    # SEM validação de email, força da senha, etc.
    id = models.criar_usuario(nome, email, senha)
```

### Depois
```python
import re

def criar_usuario(dados):
    erros = []
    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")

    if not nome or len(nome) < 2:
        erros.append("Nome deve ter no mínimo 2 caracteres")
    if not email or not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
        erros.append("Email inválido")
    if len(senha) < 6:
        erros.append("Senha deve ter no mínimo 6 caracteres")

    if UsuarioModel.find_by_email(email):
        erros.append("Email já cadastrado")

    if erros:
        return None, erros

    senha_hash = hash_password(senha)
    user_id = UsuarioModel.create(nome=nome, email=email, password_hash=senha_hash)
    return {"id": user_id}, None
```

---

## TR-12: Substituir Bare Except

**Alvo**: AP-12 — Bare Except / Empty Catch

### Python — Antes
```python
def criar_produto():
    try:
        # ... lógica
    except:  # BARBARE EXCEPT — esconde TODOS os erros!
        return jsonify({"erro": "Erro interno"}), 500
```

### Python — Depois
```python
import logging
logger = logging.getLogger(__name__)

def criar_produto():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        # ... lógica
    except ValueError as e:
        logger.warning(f"Validação falhou: {e}")
        return jsonify({"erro": str(e)}), 400
    except sqlite3.IntegrityError as e:
        logger.error(f"Erro de integridade: {e}")
        db.rollback()
        return jsonify({"erro": "Dados duplicados ou inválidos"}), 409
    except Exception as e:
        logger.exception(f"Erro inesperado ao criar produto: {e}")
        db.rollback()
        return jsonify({"erro": "Erro interno do servidor"}), 500
```

---

## TR-13: Extrair Magic Numbers/Strings

**Alvo**: AP-13 — Magic Numbers / Magic Strings

### Antes
```python
def relatorio_vendas():
    desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02
    # O que são 10000, 5000, 1000? O que são 0.1, 0.05, 0.02?
```

### Depois
```python
# config/constants.py ou topo do módulo
FAIXAS_DESCONTO = [
    (10000, 0.10),   # 10% para faturamento acima de 10k
    (5000, 0.05),    # 5% para faturamento acima de 5k
    (1000, 0.02),    # 2% para faturamento acima de 1k
]

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

def relatorio_vendas():
    desconto = 0
    for limite, taxa in FAIXAS_DESCONTO:
        if faturamento > limite:
            desconto = faturamento * taxa
            break
```

---

## TR-14: Substituir Print por Logger

**Alvo**: AP-14 — Print Statements as Logging

### Antes
```python
print("Listando " + str(len(produtos)) + " produtos")
print("ERRO: " + str(e))
print("SERVIDOR INICIADO")
print("!!! BANCO DE DADOS RESETADO !!!")
```

### Depois
```python
import logging

# Configurar no entry point
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Uso contextual
logger.info("Listando %d produtos", len(produtos))
logger.error("Erro ao buscar produtos: %s", e)
logger.info("Servidor iniciado na porta %d", port)
logger.warning("Banco de dados resetado!")
```

### Node.js — Antes
```javascript
console.log(`[LOG] Salvando no cache: ${key}`);
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```

### Node.js — Depois
```javascript
// Usando winston ou pino
const logger = require('pino')();

logger.info({ key }, 'Salvando no cache');
logger.warn('Processando pagamento');  // NUNCA logar número do cartão!
```

---

## TR-15: Filtrar Dados Sensíveis em Respostas

**Alvo**: AP-15 — Exposed Sensitive Data in Responses

### Python — Antes
```python
# Retorna senha do usuário na resposta
def to_dict(self):
    return {
        'id': self.id,
        'nome': self.nome,
        'email': self.email,
        'password': self.password,  # EXPÕE HASH DA SENHA!
    }

# Health check expõe configurações
return jsonify({
    "secret_key": "minha-chave-super-secreta-123",  # EXPÕE SEGREDO!
    "db_path": "loja.db",
    "debug": True,
})
```

### Python — Depois
```python
# Serializer SEM campos sensíveis
def to_dict(self):
    return {
        'id': self.id,
        'nome': self.nome,
        'email': self.email,
        'role': self.role,
        'active': self.active,
        'created_at': str(self.created_at)
        # password NUNCA incluído
    }

# Health check SEGURO
return jsonify({
    "status": "ok",
    "database": "connected",
    "counts": {
        "produtos": produtos,
        "usuarios": usuarios,
        "pedidos": pedidos
    }
})
```

---

## TR-16: Atualizar APIs Deprecated

**Alvo**: AP-16 — Deprecated APIs Usage

### Python — Antes
```python
from datetime import datetime
# ...
created_at = db.Column(db.DateTime, default=datetime.utcnow)  # DEPRECATED!
```

### Python — Depois
```python
from datetime import datetime, timezone
# ...
created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```

### Node.js — Antes
```javascript
var app = express();  // 'var' obsoleto
var hash = Buffer(pwd).toString('base64');  // Buffer() deprecated
```

### Node.js — Depois
```javascript
const app = express();  // 'const' moderno
const hash = Buffer.from(pwd).toString('base64');  // Buffer.from() correto
```

---

## TR-17: Separar Side Effects

**Alvo**: AP-17 — Mixed Concerns / Side Effects

### Antes
```python
def criar_pedido():
    # ...cria pedido...
    resultado = models.criar_pedido(usuario_id, itens)

    # Side effects misturados com lógica de negócio!
    print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]))
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    print("ENVIANDO PUSH: Novo pedido recebido")

    return jsonify({"dados": resultado, "sucesso": True}), 201
```

### Depois
```python
# controllers/pedido_controller.py
class PedidoController:
    def __init__(self, pedido_model, notification_service):
        self.pedido_model = pedido_model
        self.notification_service = notification_service

    def criar_pedido(self, usuario_id, itens):
        # 1. Lógica de negócio (pura)
        resultado = self.pedido_model.create(usuario_id, itens)
        if "erro" in resultado:
            return None, [resultado["erro"]]

        # 2. Side effects (separados, assíncronos, não bloqueiam)
        try:
            self.notification_service.notify_new_order(
                pedido_id=resultado["pedido_id"],
                usuario_id=usuario_id
            )
        except Exception as e:
            logger.warning(f"Notificação falhou (não crítico): {e}")

        return resultado, None

# services/notification_service.py
class NotificationService:
    def notify_new_order(self, pedido_id, usuario_id):
        """Notificações não bloqueiam o fluxo principal"""
        logger.info(f"Notificação: Pedido {pedido_id} criado para usuário {usuario_id}")
        # Email, SMS, Push — cada um em seu próprio método
```

---

## Ordem Recomendada de Aplicação

Ao refatorar um projeto inteiro, siga esta ordem:

1. **Segurança primeiro** (TR-01, TR-02, TR-04, TR-07, TR-15)
   - Remova credenciais hardcoded, corrija SQL Injection, remova endpoints perigosos
   - Corrija hashing de senhas, filtre dados sensíveis

2. **Estrutura** (TR-03, TR-05, TR-06, TR-08)
   - Separe God Classes, extraia lógica para controllers
   - Substitua estado global, converta callbacks para async/await

3. **Qualidade** (TR-09, TR-10, TR-11, TR-12, TR-17)
   - Resolva N+1 queries, elimine duplicação
   - Adicione validação, corrija tratamento de erros, separe side effects

4. **Polimento** (TR-13, TR-14, TR-16)
   - Extraia magic numbers, substitua prints por logging, atualize APIs deprecated

### A CADA PASSO, VERIFIQUE:
- A aplicação ainda inicia?
- Os endpoints ainda respondem?
- O comportamento é idêntico ao original?
