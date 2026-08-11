# Catálogo de Anti-Patterns

Catálogo completo de anti-patterns arquiteturais com sinais de detecção, severidade e recomendações de correção.

---

## Índice de Anti-Patterns

| # | Anti-Pattern | Severidade |
|---|---|---|
| AP-01 | Hardcoded Credentials | CRITICAL |
| AP-02 | SQL Injection | CRITICAL |
| AP-03 | God Class / God Module | CRITICAL |
| AP-04 | Raw SQL Execution Endpoint | CRITICAL |
| AP-05 | Business Logic in Controllers/Routes | HIGH |
| AP-06 | Global Mutable State (Singleton) | HIGH |
| AP-07 | Insecure Password Handling | HIGH |
| AP-08 | Callback Hell / Pyramid of Doom | HIGH |
| AP-09 | N+1 Queries | MEDIUM |
| AP-10 | Duplicate Code (DRY Violation) | MEDIUM |
| AP-11 | Missing Input Validation | MEDIUM |
| AP-12 | Bare Except / Empty Catch | MEDIUM |
| AP-13 | Magic Numbers / Magic Strings | LOW |
| AP-14 | Print Statements as Logging | LOW |
| AP-15 | Exposed Sensitive Data in Responses | HIGH |
| AP-16 | Deprecated APIs Usage | MEDIUM |
| AP-17 | Mixed Concerns / Side Effects | MEDIUM |
| AP-18 | Inconsistent Code Patterns | LOW |

---

## AP-01: Hardcoded Credentials

**Severidade**: CRITICAL

**Descrição**: Credenciais, chaves de API, tokens e segredos embutidos diretamente no código fonte.

**Sinais de Detecção**:
- Strings contendo `SECRET_KEY`, `password`, `senha`, `pass`, `pwd`, `token`, `api_key`, `API_KEY`
- Padrões como: `= "minha-chave-"`, `= "senha"`, `= "admin"`, `= 'super-secreta'`
- Strings de conexão com credenciais inline: `mysql://user:pass@host`
- Chaves de gateway: `paymentGatewayKey`, `stripe_key`, `paypal_secret`
- Credenciais SMTP: `smtpUser`, `smtpPass`, `EMAIL_PASSWORD`
- Valores atribuídos que parecem chaves reais (hex longos, base64, UUID-like)
- Objetos de configuração com campos `user`, `pass`, `password`, `secret`, `key`

**Impacto**: Exposição de dados sensíveis no repositório. Qualquer pessoa com acesso ao código tem acesso a todos os sistemas.

**Recomendação**: Usar variáveis de ambiente (`os.getenv()`, `process.env`) ou arquivo `.env` com python-dotenv / dotenv.

---

## AP-02: SQL Injection

**Severidade**: CRITICAL

**Descrição**: Consultas SQL construídas por concatenação de strings com entrada do usuário, permitindo injeção de comandos maliciosos.

**Sinais de Detecção**:
- Concatenação de strings em queries: `"SELECT * FROM x WHERE id = " + str(id)`
- Interpolação de strings: `f"SELECT * FROM x WHERE name = '{name}'"`
- Uso de `.format()` em queries SQL
- Queries com `%s` ou `+` concatenando variáveis diretamente
- Ausência de queries parametrizadas (`?`, `:param`, `%s` com tupla)
- No Node.js: string interpolation em `.run()`, `.get()`, `.all()` sem placeholders `?`
- Padrão regex: `SELECT|INSERT|UPDATE|DELETE.*\+.*` ou `SELECT|INSERT|UPDATE|DELETE.*f".*{`

**Impacto**: Atacante pode ler, modificar ou deletar todo o banco de dados.

**Recomendação**: Usar queries parametrizadas (placeholders `?` no SQLite, `%s` no psycopg2) ou ORM.

---

## AP-03: God Class / God Module

**Severidade**: CRITICAL

**Descrição**: Um único arquivo ou classe que contém múltiplas responsabilidades não relacionadas (acesso a dados, lógica de negócio, validação, roteamento).

**Sinais de Detecção**:
- Arquivo com mais de 200 linhas contendo funções para múltiplos domínios diferentes
- Múltiplas entidades/domínios no mesmo arquivo (ex: produtos, usuários, pedidos em models.py)
- Classe com mais de 10 métodos públicos que tratam de responsabilidades distintas
- Arquivo com imports de múltiplos domínios não relacionados
- Arquivo nomeado como "manager", "util", "common", "core", "app" com >150 linhas
- Múltiplos padrões de acesso a dados (SELECT, INSERT, UPDATE, DELETE para >3 tabelas diferentes)

**Impacto**: Impossível testar em isolamento. Qualquer mudança afeta múltiplos domínios. Acoplamento extremo.

**Recomendação**: Separar por domínio/entidade — cada model/classe deve ter responsabilidade única (SRP).

---

## AP-04: Raw SQL Execution Endpoint

**Severidade**: CRITICAL

**Descrição**: Endpoint HTTP que aceita e executa queries SQL arbitrárias enviadas pelo cliente.

**Sinais de Detecção**:
- Rota/endpoint que recebe uma string SQL do request body
- Variável chamada `query`, `sql`, `raw_query` vinda de `request.get_json()`, `req.body`, `request.POST`
- Código como `cursor.execute(dados["sql"])` ou `db.run(req.body.query)`
- Nomes de rota como `/admin/query`, `/execute`, `/raw`, `/sql`
- Comentários ou nomes sugestivos como "executar_query", "run_sql", "raw_query"

**Impacto**: Atacante pode executar qualquer comando SQL — deletar tabelas, extrair dados, escalar privilégios.

**Recomendação**: Remover completamente o endpoint. Se for para admin, usar interface com comandos predefinidos.

---

## AP-05: Business Logic in Controllers/Routes

**Severidade**: HIGH

**Descrição**: Lógica de negócio (validações, regras, cálculos, workflows) embutida diretamente nos controllers ou handlers de rota.

**Sinais de Detecção**:
- Funções de rota/endpoint com mais de 30 linhas
- Validações complexas dentro do handler (múltiplos if/else de regras de negócio)
- Cálculos de desconto, imposto, regras de preço dentro do controller
- Lógica de formatação de dados para múltiplos campos dentro da rota
- Chamadas a serviços externos (email, SMS, push notification) dentro do handler de rota
- Blocos try/except que fazem rollback manual ou compensação

**Impacto**: Difícil testar regras de negócio isoladamente. Duplicação de lógica entre endpoints.

**Recomendação**: Extrair lógica de negócio para services/controllers dedicados. Handlers apenas recebem requisição, delegam, retornam resposta.

---

## AP-06: Global Mutable State (Singleton)

**Severidade**: HIGH

**Descrição**: Uso de variáveis globais mutáveis ou singletons que mantêm estado compartilhado entre requisições.

**Sinais de Detecção**:
- `global` statement em Python
- Variáveis declaradas no escopo do módulo com `let` ou `var` (Node.js) que são modificadas em funções
- Singletons com estado interno mutável (`db_connection = None` no escopo do módulo)
- Objetos de cache global: `globalCache`, `let cache = {}`
- Variáveis globais como contadores ou acumuladores: `totalRevenue`, `requestCount`
- Conexões compartilhadas entre threads sem pool: `check_same_thread=False` com singleton

**Impacto**: Condições de corrida, vazamento de memória, estado inconsistente entre requisições.

**Recomendação**: Usar injeção de dependência, connection pool, ou passar estado explicitamente.

---

## AP-07: Insecure Password Handling

**Severidade**: HIGH

**Descrição**: Senhas armazenadas em plaintext ou com algoritmos criptograficamente quebrados (MD5, SHA1).

**Sinais de Detecção**:
- `hashlib.md5()` usado para hash de senhas
- `hashlib.sha1()` usado para hash de senhas
- Senhas comparadas diretamente: `WHERE senha = '` + senha_input + `'`
- Campo de senha armazenado como texto puro sem hash
- Criptografia caseira: funções chamadas `badCrypto`, `simpleHash`, `customEncrypt`
- Encoding Base64 usado como "criptografia" de senha
- Uso de `Buffer.from(pwd).toString('base64')` para "hashear"

**Impacto**: Senhas podem ser recuperadas em caso de vazamento do banco. MD5 é quebrado em segundos.

**Recomendação**: Usar `bcrypt`, `scrypt`, `argon2` ou `hashlib.sha256()` com salt. Nunca armazenar senhas em plaintext.

---

## AP-08: Callback Hell / Pyramid of Doom

**Severidade**: HIGH

**Descrição**: Múltiplos níveis de callbacks aninhados, tornando o código ilegível e difícil de manter.

**Sinais de Detecção**:
- Mais de 3 níveis de indentação dentro de callbacks
- Funções anônimas passadas como callbacks com mais de 10 linhas
- Padrão: `db.get(..., (err, result) => { db.get(..., (err2, result2) => { ... }) })`
- Múltiplos `})` no final de blocos (pirâmide)
- Mix de lógica síncrona e assíncrona sem organização clara

**Impacto**: Extremamente difícil de debugar, testar e modificar. Propenso a memory leaks e race conditions.

**Recomendação**: Converter para async/await ou Promises. Extrair cada nível para funções nomeadas.

---

## AP-09: N+1 Queries

**Severidade**: MEDIUM

**Descrição**: Loop que executa uma query SQL para cada iteração, resultando em N+1 queries quando 2 queries bastariam.

**Sinais de Detecção**:
- `for` loop que contém `cursor.execute()` ou `db.get()` / `db.run()` dentro
- Query dentro de iteração sobre resultados de outra query
- Padrão: itera sobre lista e faz SELECT para cada item
- Exemplo: `for row in rows: cursor.execute("SELECT ... WHERE id = " + row["id"])`
- No Node.js: `.forEach()` ou `for` loop com `.get()`, `.all()`, `.run()` dentro

**Impacto**: Degradação severa de performance. Em vez de 2 queries, executa centenas ou milhares.

**Recomendação**: Usar JOIN ou buscar todos os IDs de uma vez com `WHERE id IN (...)`.

---

## AP-10: Duplicate Code (DRY Violation)

**Severidade**: MEDIUM

**Descrição**: Blocos de código idênticos ou muito similares repetidos em múltiplos locais.

**Sinais de Detecção**:
- Funções com lógica idêntica mas nomes diferentes
- Serialização de objetos repetida em múltiplas funções (mesmos campos mapeados manualmente)
- Blocos de validação copiados e colados entre endpoints
- Lógica de formatação de data/id/nome duplicada
- Mesmo padrão de try/except em múltiplas funções
- Construção manual de dict/objeto repetida com os mesmos campos

**Impacto**: Bugs precisam ser corrigidos em múltiplos lugares. Diverge com o tempo.

**Recomendação**: Extrair lógica comum para funções helpers, métodos compartilhados ou classes base.

---

## AP-11: Missing Input Validation

**Severidade**: MEDIUM

**Descrição**: Endpoints que aceitam dados do usuário sem validação adequada de tipo, tamanho, formato ou range.

**Sinais de Detecção**:
- `request.get_json()` ou `req.body` seguido de acesso direto aos campos sem validação
- Ausência de checks de tipo (isinstance, typeof) antes de usar valores
- Campos obrigatórios não verificados
- Falta de validação de email, URL, formato de data
- Aceitação de qualquer string sem limite de tamanho
- Campos numéricos sem validação de range (preço negativo, quantidade negativa)

**Impacto**: Dados inválidos corrompem o banco, causam erros 500, podem levar a vulnerabilidades.

**Recomendação**: Validar todos os inputs: tipo, formato, range, obrigatoriedade. Usar bibliotecas como marshmallow, joi, zod.

---

## AP-12: Bare Except / Empty Catch

**Severidade**: MEDIUM

**Descrição**: Blocos try/except ou try/catch que capturam todas as exceções sem tratamento específico, escondendo erros.

**Sinais de Detecção**:
- `except:` sem especificar tipo de exceção (Python)
- `except Exception as e:` seguido apenas de `print(e)` e retorno 500
- `catch(err) { }` vazio ou apenas com console.log
- `catch { }` sem parâmetro
- Blocos except/catch que engolem erros sem log, rollback ou tratamento adequado

**Impacto**: Erros reais são escondidos. Debugging fica impossível. Transações podem ficar inconsistentes.

**Recomendação**: Capturar exceções específicas. Fazer rollback em transações. Logar erro completo.

---

## AP-13: Magic Numbers / Magic Strings

**Severidade**: LOW

**Descrição**: Valores numéricos ou strings literais usados diretamente no código sem explicação do significado.

**Sinais de Detecção**:
- Números "soltos" em comparações: `if total > 10000`, `if len(name) < 3`
- Strings de status repetidas: `'pending'`, `'done'`, `'active'`
- Valores de desconto/fator inline: `* 0.1`, `* 0.05`, `* 0.02`
- Cores, limites, timeouts como literais: `'#000000'`, `timeout=30`

**Impacto**: Difícil entender o significado dos valores. Mudanças requerem caça aos números pelo código.

**Recomendação**: Extrair para constantes nomeadas no topo do módulo ou em arquivo de configuração.

---

## AP-14: Print Statements as Logging

**Severidade**: LOW

**Descrição**: Uso de `print()` ou `console.log()` para logging em vez de um sistema de logging adequado.

**Sinais de Detecção**:
- `print(` em código Python fora de scripts
- `console.log(` em código Node.js que não seja desenvolvimento
- Ausência de imports de bibliotecas de logging (`import logging`, `winston`, `pino`, `bunyan`)
- Mensagens de log sem timestamp, nível de severidade ou contexto

**Impacto**: Sem controle de nível de log (DEBUG, INFO, WARN, ERROR). Logs vão para stdout sem estrutura.

**Recomendação**: Usar `logging` (Python) ou `winston`/`pino` (Node.js) com níveis apropriados.

---

## AP-15: Exposed Sensitive Data in Responses

**Severidade**: HIGH

**Descrição**: Endpoints que retornam dados sensíveis como senhas, chaves, tokens ou configurações internas.

**Sinais de Detecção**:
- Resposta JSON incluindo campo `senha`, `password`, `pass`, `secret_key`
- Health check endpoint retornando configurações internas (secret_key, db_path, debug)
- `to_dict()` ou serializador incluindo hash de senha
- Listagem de usuários retornando campo de senha
- Resposta de erro incluindo stack trace completo ou query SQL

**Impacto**: Vazamento de dados sensíveis para qualquer cliente da API. Escalável para ataques.

**Recomendação**: Filtrar campos sensíveis nas respostas. Criar DTOs/serializers específicos para API.

---

## AP-16: Deprecated APIs Usage

**Severidade**: MEDIUM

**Descrição**: Uso de APIs, funções ou métodos marcados como deprecated que serão removidos em versões futuras.

**Sinais de Detecção**:

### Python
- `datetime.utcnow()` → substituir por `datetime.now(datetime.UTC)`
- `datetime.utcfromtimestamp()` → substituir por `datetime.fromtimestamp(ts, tz=datetime.UTC)`
- `hashlib.md5()` para senhas → substituir por `bcrypt`/`scrypt`/`hashlib.sha256()` com salt
- `sqlite3.connect(..., check_same_thread=False)` → usar connection pool ou `g` do Flask
- `@app.before_first_request` → usar `with app.app_context()` para init
- `flask.ext.` imports → usar `flask_` prefix

### Node.js
- `new Buffer()` ou `Buffer()` sem `new` → usar `Buffer.from()` ou `Buffer.alloc()`
- `var` declarações → usar `let` ou `const`
- `url.parse()` → usar `new URL()`
- `request` (biblioteca) → substituir por `fetch` ou `axios`
- Callbacks sem Promise wrapper → usar `util.promisify()` ou async/await

**Impacto**: Código quebra ao atualizar versões do runtime/framework. Vulnerabilidades não corrigidas.

**Recomendação**: Substituir pelas APIs recomendadas na documentação oficial.

---

## AP-17: Mixed Concerns / Side Effects

**Severidade**: MEDIUM

**Descrição**: Funções que misturam lógica de negócio com efeitos colaterais (notificações, logging, chamadas externas).

**Sinais de Detecção**:
- Função de criação/atualização que também envia email/SMS/push notification
- Controller que faz print de "ENVIANDO EMAIL" ou "NOTIFICAÇÃO" durante operação
- Lógica de negócio seguida de chamadas a serviços externos no mesmo bloco
- Múltiplas responsabilidades na mesma função: salva no banco E notifica E loga E cacheia

**Impacto**: Se a notificação falha, a transação principal pode ser afetada. Difícil testar em isolamento.

**Recomendação**: Separar em serviços distintos. Usar padrão Observer, eventos ou filas para notificações.

---

## AP-18: Inconsistent Code Patterns

**Severidade**: LOW

**Descrição**: Uso inconsistente de padrões de código no mesmo projeto (estilos de roteamento, nomenclatura, formatação).

**Sinais de Detecção**:
- Mix de `@app.route()` e `app.add_url_rule()` no mesmo arquivo
- Mix de `snake_case` e `camelCase` na mesma base de código
- Alguns endpoints retornam `{"dados": x, "sucesso": true}` e outros `{data: x}`
- Mix de funções async e sync sem padrão claro
- Alguns models com `to_dict()` e outros manualmente serializados
- Import de módulos não utilizados (`import json` sem uso, `require('fs')` não usado)

**Impacto**: Codebase confusa. Desenvolvedores não sabem qual padrão seguir.

**Recomendação**: Padronizar em um estilo e aplicar consistentemente. Usar linters (flake8, eslint, prettier).
