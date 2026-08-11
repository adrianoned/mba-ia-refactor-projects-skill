# Guidelines de Arquitetura MVC

Este documento define o padrão MVC (Model-View-Controller) alvo que a skill refactor-arch aplica durante a Fase 3 de refatoração.

---

## Princípios Fundamentais

### Separação de Responsabilidades (SRP)
Cada camada tem uma responsabilidade clara e exclusiva:
- **Model**: Apenas estrutura de dados e acesso ao banco — NUNCA contém lógica HTTP
- **View/Route**: Apenas roteamento HTTP e formatação de resposta — NUNCA contém lógica de negócio
- **Controller**: Apenas orquestração do fluxo — recebe dados da rota, chama models/services, retorna resultado

### Injeção de Dependência
- Nenhuma camada deve instanciar diretamente suas dependências
- Conexões de banco, serviços e configurações são injetados
- Facilita testes e reduz acoplamento

### Configuração Externalizada
- NADA de credenciais, chaves ou secrets no código fonte
- Tudo via variáveis de ambiente ou arquivo `.env`
- Módulo de config centralizado

---

## Estrutura de Diretórios Alvo

### Python / Flask

```
src/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configurações via env vars
├── models/
│   ├── __init__.py
│   ├── <entidade>_model.py  # Um model por entidade
│   └── ...
├── controllers/
│   ├── __init__.py
│   ├── <entidade>_controller.py  # Lógica de negócio
│   └── ...
├── views/
│   ├── __init__.py
│   └── routes.py            # Blueprints — apenas roteamento
├── middlewares/
│   ├── __init__.py
│   └── error_handler.py     # Tratamento centralizado de erros
├── services/                # (opcional) Serviços externos
│   ├── __init__.py
│   └── notification_service.py
└── app.py                   # Entry point / composition root
```

### Node.js / Express

```
src/
├── config/
│   └── settings.js          # Configurações via process.env
├── models/
│   ├── <Entidade>.js        # Um model por entidade
│   └── ...
├── controllers/
│   ├── <entidade>Controller.js  # Lógica de negócio
│   └── ...
├── routes/
│   ├── index.js             # Agregador de rotas
│   ├── <entidade>Routes.js  # Rotas por entidade
│   └── ...
├── middlewares/
│   └── errorHandler.js      # Tratamento centralizado de erros
├── services/                # (opcional) Serviços externos
│   └── notificationService.js
└── app.js                   # Entry point / composition root
```

---

## Responsabilidades por Camada

### 1. Config (`config/`)

**O que vai aqui**:
- Leitura de variáveis de ambiente
- Configurações de banco de dados (URL, credenciais)
- Chaves de API e segredos
- Flags de feature (DEBUG, LOG_LEVEL)
- Constantes de aplicação

**O que NÃO vai aqui**:
- Lógica de inicialização de banco
- Criação de tabelas/seeds
- Rotas ou handlers

**Exemplo Python**:
```python
# config/settings.py
import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-me")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
    PORT = int(os.getenv("PORT", "5000"))

settings = Settings()
```

**Exemplo Node.js**:
```javascript
// config/settings.js
const settings = {
    port: process.env.PORT || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    jwtSecret: process.env.JWT_SECRET || 'dev-secret-change-me',
    nodeEnv: process.env.NODE_ENV || 'development',
};
module.exports = { settings };
```

---

### 2. Models (`models/`)

**O que vai aqui**:
- Definição de entidades/tabelas (ORM ou schema)
- Métodos de acesso a dados (CRUD)
- Validação de dados da entidade
- Relacionamentos entre entidades
- Serialização/deserialização (to_dict, toJSON)

**O que NÃO vai aqui**:
- Lógica de negócio complexa (descontos, workflows)
- Chamadas HTTP ou resposta HTTP (request, response, jsonify)
- Regras de autorização ou permissão
- Envio de emails ou notificações

**Exemplo Python**:
```python
# models/produto_model.py
from database import db

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)

    @staticmethod
    def find_all():
        return Produto.query.all()

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "preco": self.preco,
            "estoque": self.estoque
        }
```

**Exemplo Node.js**:
```javascript
// models/User.js
class User {
    constructor(db) {
        this.db = db;
    }

    findById(id) {
        return new Promise((resolve, reject) => {
            this.db.get("SELECT * FROM users WHERE id = ?", [id], (err, row) => {
                if (err) return reject(err);
                resolve(row);
            });
        });
    }

    toJSON(row) {
        return {
            id: row.id,
            name: row.name,
            email: row.email
            // NUNCA incluir password
        };
    }
}
```

---

### 3. Controllers (`controllers/`)

**O que vai aqui**:
- Orquestração do fluxo entre rotas e models
- Chamada a services externos (email, notificação)
- Validação de regras de negócio
- Transformação de dados para a camada de view
- Decisões de fluxo (conditional branching)

**O que NÃO vai aqui**:
- Acesso direto ao request/response HTTP (recebe dados já extraídos)
- Queries SQL diretas (usa models)
- Definição de rotas (@app.route, router.get)

**Exemplo Python**:
```python
# controllers/produto_controller.py
from models.produto_model import Produto

class ProdutoController:
    def listar_produtos(self):
        produtos = Produto.find_all()
        return [p.to_dict() for p in produtos], None

    def criar_produto(self, dados):
        erros = self._validar_dados(dados)
        if erros:
            return None, erros
        produto = Produto.criar(**dados)
        return produto.to_dict(), None

    def _validar_dados(self, dados):
        erros = []
        if not dados.get("nome"):
            erros.append("Nome é obrigatório")
        if dados.get("preco", 0) < 0:
            erros.append("Preço não pode ser negativo")
        return erros
```

**Exemplo Node.js**:
```javascript
// controllers/courseController.js
class CourseController {
    constructor(courseModel, paymentService) {
        this.courseModel = courseModel;
        this.paymentService = paymentService;
    }

    async checkout(userData, courseId) {
        const course = await this.courseModel.findById(courseId);
        if (!course) throw new Error("Curso não encontrado");

        const payment = await this.paymentService.process(course.price);
        if (!payment.success) throw new Error("Pagamento recusado");

        return await this.courseModel.enroll(userData.id, courseId);
    }
}
```

---

### 4. Views / Routes (`views/` ou `routes/`)

**O que vai aqui**:
- Definição de rotas/endpoints (URL, método HTTP)
- Extração de parâmetros da requisição
- Chamada ao controller correspondente
- Formatação da resposta HTTP (status code, headers, body)
- APENAS isso — sem lógica de negócio

**O que NÃO vai aqui**:
- Validações complexas
- Queries de banco de dados
- Cálculos ou regras de negócio
- Chamadas a serviços externos

**Exemplo Python (Flask Blueprint)**:
```python
# views/routes.py
from flask import Blueprint, request, jsonify
from controllers.produto_controller import ProdutoController

produto_bp = Blueprint('produtos', __name__)
controller = ProdutoController()

@produto_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    dados, erro = controller.listar_produtos()
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify({"dados": dados}), 200

@produto_bp.route('/produtos', methods=['POST'])
def criar_produto():
    dados, erro = controller.criar_produto(request.get_json())
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify({"dados": dados}), 201
```

**Exemplo Node.js (Express Router)**:
```javascript
// routes/courseRoutes.js
const { Router } = require('express');
const router = Router();

module.exports = (courseController) => {
    router.post('/checkout', async (req, res) => {
        try {
            const result = await courseController.checkout(req.body, req.body.course_id);
            res.json({ success: true, data: result });
        } catch (err) {
            res.status(400).json({ error: err.message });
        }
    });
    return router;
};
```

---

### 5. Middlewares (`middlewares/`)

**O que vai aqui**:
- Tratamento centralizado de erros
- Autenticação e autorização
- Validação de schema/input (pode ser middleware)
- Logging de requisições
- CORS, rate limiting, compressão

**Exemplo Python**:
```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
```

**Exemplo Node.js**:
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    console.error(`[ERROR] ${err.message}`);
    res.status(err.status || 500).json({
        error: err.message || 'Internal Server Error',
        success: false
    });
}
module.exports = { errorHandler };
```

---

### 6. Entry Point (`app.py` / `app.js`)

**O que vai aqui**:
- Criação da aplicação
- Registro de middlewares
- Registro de blueprints/routers
- Inicialização de banco de dados
- Inicialização de serviços (injeção de dependência)
- Apenas o bootstrap da aplicação

**O que NÃO vai aqui**:
- Rotas definidas inline
- Lógica de negócio
- Queries SQL
- Configurações hardcoded

**Exemplo Python**:
```python
# app.py
from flask import Flask
from config.settings import settings
from views.routes import register_routes
from middlewares.error_handler import register_error_handlers
from database import init_db

def create_app():
    app = Flask(__name__)
    app.config.update(settings.__dict__)

    init_db(app)
    register_routes(app)
    register_error_handlers(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=settings.PORT)
```

---

## Checklist de Validação MVC

Após a refatoração, verificar:

- [ ] Cada model tem APENAS definição de entidade + acesso a dados
- [ ] Cada controller NÃO acessa request/response diretamente
- [ ] Cada rota NÃO contém lógica de negócio (só extrai parâmetros e delega)
- [ ] Configurações NÃO estão hardcoded
- [ ] Entry point é limpo (apenas composição/bootstrapping)
- [ ] Error handling é centralizado (não repete try/except em cada rota)
- [ ] Serviços externos são injetados, não instanciados diretamente
- [ ] A aplicação inicia e todos os endpoints originais respondem
