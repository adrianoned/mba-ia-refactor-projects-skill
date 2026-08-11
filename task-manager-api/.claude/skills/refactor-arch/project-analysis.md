# Análise de Projeto — Heurísticas de Detecção

Este documento descreve as heurísticas para detectar automaticamente a stack tecnológica, framework, banco de dados e arquitetura de um projeto.

---

## 1. Detecção de Linguagem

| Arquivo/Sinal | Linguagem |
|---|---|
| `package.json` | Node.js / JavaScript / TypeScript |
| `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile` | Python |
| `go.mod`, `go.sum` | Go |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java / Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `Cargo.toml` | Rust |
| `*.csproj`, `*.sln` | C# / .NET |
| `tsconfig.json` (sem package.json) | TypeScript (puro) |
| `CMakeLists.txt` | C / C++ |

### Prioridade de detecção
1. Verifique primeiro arquivos de manifesto de dependências
2. Depois extensões de arquivos fonte (.py, .js, .ts, .go, .java, .rb, .php, .rs, .cs)
3. Se houver múltiplos, priorize pelo manifesto principal

---

## 2. Detecção de Framework

### Python
| Sinal | Framework |
|---|---|
| `from flask import` | Flask |
| `from fastapi import` | FastAPI |
| `from django.` | Django |
| `import tornado` | Tornado |
| `import aiohttp` | aiohttp |
| `import sanic` | Sanic |

### Node.js / JavaScript
| Sinal | Framework |
|---|---|
| `require('express')` ou `from 'express'` | Express.js |
| `require('koa')` | Koa |
| `require('@nestjs/')` | NestJS |
| `require('fastify')` | Fastify |
| `require('hapi')` | Hapi |

### Detecção de versão
- Python: leia `requirements.txt` — formato `flask==3.1.1` ou `flask>=3.0`
- Node.js: leia `package.json` → `dependencies` → versão (ex: `"express": "^4.18.2"`)

---

## 3. Detecção de Banco de Dados

| Sinal | Banco / ORM |
|---|---|
| `import sqlite3` ou `require('sqlite3')` | SQLite |
| `import psycopg2` ou `require('pg')` | PostgreSQL |
| `import pymysql`, `mysql.connector` ou `require('mysql2')` | MySQL / MariaDB |
| `import pymongo` ou `require('mongoose')` | MongoDB |
| `import redis` ou `require('redis')` | Redis |
| `SQLAlchemy`, `flask_sqlalchemy` | SQLAlchemy ORM |
| `mongoose` | Mongoose ODM |
| `sequelize`, `typeorm`, `prisma` | ORM (Node.js) |
| `django.db` | Django ORM |

### Detecção por string de conexão
- Padrões: `sqlite:///`, `postgresql://`, `mysql://`, `mongodb://`, `redis://`
- Variáveis de ambiente: `DATABASE_URL`, `DB_URI`, `MONGO_URI`, `MONGODB_URI`

---

## 4. Mapeamento de Arquitetura

### Classificação automática

**Monolítica — sem separação de camadas**:
- Todos os arquivos fonte em 1 diretório (ou no máximo 2)
- Sem diretórios como models/, controllers/, routes/, services/
- Arquivos com nomes genéricos: app.py, models.py, utils.js
- Mix de responsabilidades: SQL, lógica de negócio, HTTP no mesmo arquivo

**Parcialmente estruturada**:
- Possui alguns diretórios de separação (models/, routes/) mas com responsabilidades misturadas
- Controllers com lógica de negócio, models que fazem queries diretas
- Falta clara separação entre camadas

**Bem estruturada**:
- Diretórios claros: config/, models/, controllers/, routes/, services/, middlewares/
- Injeção de dependência presente
- Cada arquivo tem responsabilidade única

### Identificação de domínio
Analise:
- Nomes de tabelas SQL (CREATE TABLE / FROM / INSERT INTO)
- Nomes de collections MongoDB
- Nomes de endpoints/routes
- Nomes de classes/modelos
- Comentários e documentação

Exemplos de domínios:
- "E-commerce API (produtos, pedidos, usuários)"
- "LMS API (cursos, matrículas, pagamentos, alunos)"
- "Task Manager API (tarefas, usuários, categorias)"
- "Blog API (posts, comentários, autores)"

---

## 5. Contagem e Estatísticas

### Arquivos fonte
Conte apenas arquivos que contenham código fonte (exclua):
- `node_modules/`, `venv/`, `.venv/`, `env/`
- `.git/`, `__pycache__/`, `*.pyc`
- `dist/`, `build/`, `.next/`
- Arquivos de lock (`package-lock.json`, `yarn.lock`, `poetry.lock`)
- Diretórios de migração automática

### Linhas de código
- Conte linhas não-vazias dos arquivos fonte
- Use `wc -l` para estimativa rápida
- Para Python: exclua docstrings e comentários se possível
- Para JavaScript: exclua blocos de comentários

---

## 6. Detecção de APIs Deprecated

### Python / Flask
| Sinal | Descrição |
|---|---|
| `datetime.utcnow()` | Deprecated no Python 3.12+ — usar `datetime.now(datetime.UTC)` |
| `datetime.utcfromtimestamp()` | Deprecated — usar `datetime.fromtimestamp(ts, tz=datetime.UTC)` |
| `hashlib.md5()` | Inseguro para senhas — usar `bcrypt`, `scrypt` ou `hashlib.sha256()` com salt |
| `@app.before_first_request` | Deprecated no Flask 2.3+ — usar `with app.app_context()` |

### Node.js / Express
| Sinal | Descrição |
|---|---|
| `Buffer()` sem `new` | Deprecated — usar `Buffer.from()` ou `Buffer.alloc()` |
| `new Buffer()` | Deprecated desde Node 6 — usar `Buffer.from()` |
| `req.body` sem middleware | Express 4.16+ requer `express.json()` explicitamente |
| `var` (em vez de `let/const`) | ES6+ usa `let` e `const` — `var` é obsoleto |
| Callbacks aninhados sem Promises | Padrão obsoleto — usar async/await |
| `url.parse()` | Deprecated — usar `new URL()` |

---

## Exemplo de Execução

Entrada: diretório de projeto
Saída: resumo formatado

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors, sqlite3
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed (~800 lines of code)
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```
