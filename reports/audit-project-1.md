# Relatório de Auditoria Arquitetural

**Projeto**: `code-smells-project` (E-commerce Loja Virtual API)
**Data**: 2026-08-11
**Skill**: refactor-arch v1.0.0

---

## Resumo Executivo

| Métrica | Valor |
|---|---|
| Linguagem | Python |
| Framework | Flask 3.1.1 |
| Arquivos analisados | 4 (app.py, controllers.py, models.py, database.py) |
| Linhas de código (aprox.) | 780 |
| Banco de dados | SQLite3 (via `sqlite3` nativo) |
| Tabelas/Coleções | produtos, usuarios, pedidos, itens_pedido |

### Arquitetura Atual

Parcialmente estruturada — o projeto separa arquivos por função (`models.py`, `controllers.py`, `database.py`, `app.py`), mas com graves violações de separação de camadas. Todos os models realizam SQL Injection por concatenação de strings. A lógica de validação e regras de negócio está embutida nos controllers. Credenciais e configurações estão hardcoded no código fonte. Não há módulo de configuração, middleware de erro, nem serviços separados.

### Domínio

E-commerce — Loja Virtual com catálogo de produtos (informática, móveis, vestuário, eletrônicos, livros), gestão de usuários (admin e cliente), criação e acompanhamento de pedidos, controle de status (pendente, aprovado, enviado, entregue, cancelado), e relatórios de vendas.

---

## Sumário de Findings

| Severidade | Quantidade |
|---|---|
| CRITICAL | 4 |
| HIGH | 5 |
| MEDIUM | 7 |
| LOW | 3 |
| **TOTAL** | **19** |

---

## Findings por Severidade

### CRITICAL (4)

#### AP-01 — Hardcoded Credentials
- **Arquivo**: `app.py:7-8`, `database.py:5`
- **Severidade**: CRITICAL
- **Descrição**: SECRET_KEY hardcoded como string literal `'minha-chave-super-secreta-123'` e DEBUG=True ativado diretamente no código. O caminho do banco `db_path = "loja.db"` está hardcoded no escopo do módulo `database.py:5`.
- **Impacto**: Sessões de usuário podem ser forjadas com a SECRET_KEY exposta. Tokens JWT ou cookies de sessão são inseguros. O modo DEBUG em produção expõe stack traces detalhados com informações sensíveis do sistema.
- **Recomendação**: Mover SECRET_KEY para variável de ambiente (`os.getenv('SECRET_KEY')`), DEBUG para `os.getenv('DEBUG', 'False').lower() == 'true'`, e db_path para `os.getenv('DATABASE_PATH', 'loja.db')`. Usar python-dotenv para carregar arquivo `.env` em desenvolvimento.

#### AP-02 — SQL Injection (Múltiplas Ocorrências)
- **Arquivo**: `models.py` — 20 ocorrências em todo o arquivo
- **Severidade**: CRITICAL
- **Descrição**: TODAS as queries SQL no projeto são construídas por concatenação de strings, permitindo injeção de comandos maliciosos. Ocorrências detalhadas:
  - `models.py:28` — `get_produto_por_id`: `"SELECT * FROM produtos WHERE id = " + str(id)`
  - `models.py:47-49` — `criar_produto`: INSERT com valores concatenados diretamente
  - `models.py:57-61` — `atualizar_produto`: UPDATE com nome, descricao, categoria concatenados
  - `models.py:68` — `deletar_produto`: DELETE com id concatenado
  - `models.py:92` — `get_usuario_por_id`: SELECT com id concatenado
  - `models.py:109-110` — `login_usuario`: SELECT com email e senha concatenados (dupla vulnerabilidade)
  - `models.py:126-128` — `criar_usuario`: INSERT com nome, email, senha concatenados
  - `models.py:140` — `criar_pedido`: SELECT produto por id concatenado
  - `models.py:148-150` — `criar_pedido`: INSERT pedido concatenado
  - `models.py:155` — `criar_pedido`: SELECT preco concatenado
  - `models.py:157-160` — `criar_pedido`: INSERT itens_pedido concatenado
  - `models.py:163-165` — `criar_pedido`: UPDATE estoque concatenado
  - `models.py:174` — `get_pedidos_usuario`: SELECT por usuario_id concatenado
  - `models.py:188` — `get_pedidos_usuario`: SELECT itens_pedido concatenado (N+1 query)
  - `models.py:192` — `get_pedidos_usuario`: SELECT nome produto concatenado (N+1 query)
  - `models.py:220` — `get_todos_pedidos`: SELECT itens_pedido concatenado (N+1 query)
  - `models.py:224` — `get_todos_pedidos`: SELECT nome produto concatenado (N+1 query)
  - `models.py:279-281` — `atualizar_status_pedido`: UPDATE status concatenado
  - `models.py:289-297` — `buscar_produtos`: query dinâmica inteira com múltiplas concatenações de termo, categoria, preco_min, preco_max
- **Impacto**: Um atacante pode ler, modificar ou deletar qualquer dado do banco. Login pode ser bypassado. Dados de todos os usuários podem ser extraídos. O banco inteiro pode ser destruído.
- **Recomendação**: Substituir TODAS as queries por queries parametrizadas usando placeholders `?` do SQLite3. Exemplo: `cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))`. Para queries dinâmicas como `buscar_produtos`, construir a query com placeholders e passar parâmetros como tupla.

#### AP-03 — God Class / God Module
- **Arquivo**: `models.py` (314 linhas), `controllers.py` (292 linhas)
- **Severidade**: CRITICAL
- **Descrição**: `models.py` contém 314 linhas misturando 4 domínios distintos (produtos, usuários, pedidos, relatórios) em um único arquivo. Contém 16 funções que lidam com acesso a dados para todas as entidades. `controllers.py` com 292 linhas mistura handlers para 4 domínios diferentes com lógica de validação, notificações e formatação de resposta.
- **Impacto**: Impossível testar entidades em isolamento. Qualquer mudança em produtos pode impactar pedidos ou usuários. Acoplamento extremo entre domínios. Arquivos grandes e difíceis de manter.
- **Recomendação**: Separar models por entidade: `models/produto.py`, `models/usuario.py`, `models/pedido.py`. Separar controllers por domínio: `controllers/produto_controller.py`, `controllers/usuario_controller.py`, `controllers/pedido_controller.py`. Separar relatórios em serviço dedicado.

#### AP-04 — Raw SQL Execution Endpoint
- **Arquivo**: `app.py:59-78`
- **Severidade**: CRITICAL
- **Descrição**: O endpoint `POST /admin/query` aceita um JSON com campo `sql` e executa a query SQL arbitrária diretamente no banco de dados. Se for SELECT, retorna os resultados; caso contrário, executa INSERT/UPDATE/DELETE. Não há qualquer autenticação, autorização ou restrição.
- **Impacto**: Qualquer pessoa com acesso à API pode executar comandos SQL arbitrários — deletar todas as tabelas (`DROP TABLE`), extrair todos os dados de usuários incluindo senhas, modificar pedidos, escalar privilégios, ou destruir completamente o banco de dados.
- **Recomendação**: Remover completamente este endpoint. Se for necessário para administração, substituir por endpoints específicos com operações predefinidas e autenticação obrigatória.

---

### HIGH (5)

#### AP-05 — Business Logic in Controllers/Routes
- **Arquivo**: `controllers.py:24-62`, `controllers.py:188-220`, `controllers.py:237-255`, `app.py:47-57`
- **Severidade**: HIGH
- **Descrição**: 
  - `criar_produto` (linhas 24-62): 38 linhas de validações manuais (campos obrigatórios, ranges, categorias válidas) no handler
  - `criar_pedido` (linhas 188-220): lógica de criação de pedido + side effects de notificação (prints de EMAIL, SMS, PUSH) no mesmo handler
  - `atualizar_status_pedido` (linhas 237-255): lógica de notificação condicional por status embutida no handler
  - `reset_database` (app.py:47-57): lógica de reset do banco diretamente na rota
- **Impacto**: Difícil testar regras de negócio isoladamente. Lógica duplicada entre endpoints similares (ex: validações de produto em criar e atualizar). Efeitos colaterais dificultam debugging e teste.
- **Recomendação**: Extrair validações para camada de serviço/validação. Mover notificações para serviços separados com padrão Observer ou eventos. Extrair lógica do reset_database para um serviço admin.

#### AP-06 — Global Mutable State (Singleton)
- **Arquivo**: `database.py:4-11`
- **Severidade**: HIGH
- **Descrição**: Conexão SQLite armazenada como variável global mutável (`db_connection = None` no escopo do módulo, linha 4) com padrão singleton. Usa `check_same_thread=False` (linha 10) para permitir acesso multi-thread, o que é perigoso com SQLite. A função `get_db()` modifica o estado global via `global db_connection` (linha 8).
- **Impacto**: Condições de corrida em ambientes multi-thread. Conexão compartilhada entre requisições sem pool. `check_same_thread=False` pode causar corrupção de dados no SQLite. Vazamento de conexão — se a conexão falhar, todas as requisições subsequentes falham.
- **Recomendação**: Usar o objeto `g` do Flask (`flask.g`) para armazenar a conexão por requisição, ou usar um connection pool adequado. Remover `check_same_thread=False`. Fechar a conexão ao final de cada requisição com `teardown_appcontext`.

#### AP-07 — Insecure Password Handling
- **Arquivo**: `database.py:76-77`, `models.py:109-110`, `models.py:126-128`
- **Severidade**: HIGH
- **Descrição**: Senhas armazenadas em plaintext (texto puro) no banco de dados. Os seeds incluem `'admin123'`, `'123456'`, `'senha123'` como strings literais. A função `login_usuario` compara senhas diretamente na query SQL: `WHERE email = '...' AND senha = '...'`. A função `criar_usuario` insere a senha recebida diretamente sem hash. A listagem de usuários (`get_todos_usuarios` linha 83 e `get_usuario_por_id` linha 99) retorna o campo `senha` nas respostas.
- **Impacto**: Em caso de vazamento do banco de dados, todas as senhas estão visíveis em texto puro. Senhas expostas via endpoints de listagem de usuários. Qualquer pessoa com acesso ao banco pode fazer login como qualquer usuário.
- **Recomendação**: Hashear senhas com bcrypt ou hashlib.sha256() + salt antes de armazenar. Nunca retornar campo `senha` em respostas de API. Comparar hash no login, nunca senha em plaintext.

#### AP-08 — Callback Hell / Pyramid of Doom
- **Arquivo**: N/A — não aplicável (Python síncrono sem padrão de callbacks aninhados)
- **Severidade**: N/A
- **Descrição**: O projeto usa Python com execução síncrona e não apresenta padrão de callbacks aninhados típico de JavaScript.
- **Impacto**: N/A
- **Recomendação**: N/A

#### AP-09 — N+1 Queries
- **Arquivo**: `models.py:171-201`, `models.py:203-233`
- **Severidade**: HIGH (reclassificado de MEDIUM devido à severidade no contexto)
- **Descrição**: 
  - `get_pedidos_usuario` (171-201): Para cada pedido, executa uma query de itens (N queries), e para cada item, executa outra query de produto (N*M queries). Um usuário com 5 pedidos de 3 itens cada gera 1 + 5 + 15 = 21 queries.
  - `get_todos_pedidos` (203-233): Padrão idêntico — poderia gerar centenas de queries com muitos pedidos.
- **Impacto**: Degradação severa de performance. Para 50 pedidos com 3 itens cada = 1 + 50 + 150 = 201 queries em vez de 3 queries com JOINs.
- **Recomendação**: Usar JOIN para buscar pedidos + itens + produtos em uma única query, ou buscar todos os IDs de uma vez e fazer queries batch com `WHERE id IN (...)`.

#### AP-15 — Exposed Sensitive Data in Responses
- **Arquivo**: `controllers.py:264-292`, `models.py:78-86`, `models.py:95-102`
- **Severidade**: HIGH
- **Descrição**: 
  - `health_check` (controllers.py:276-290): expõe `db_path`, `debug`, e `secret_key` com o valor real da chave secreta na resposta da API
  - `get_todos_usuarios` (models.py:83): retorna campo `senha` no JSON de resposta
  - `get_usuario_por_id` (models.py:99): retorna campo `senha` no JSON de resposta
  - `login_usuario` felizmente filtra a senha (linhas 114-119) — inconsistência com outros métodos
- **Impacto**: Vazamento de senhas (mesmo em plaintext) para qualquer cliente da API. Exposição da chave secreta permite forjar sessões. Exposição de configurações internas facilita ataques direcionados.
- **Recomendação**: Remover campo `senha` de todas as respostas de API. No health_check, retornar apenas informações não sensíveis (status, uptime, versão). Nunca expor SECRET_KEY, db_path ou debug em respostas.

---

### MEDIUM (7)

#### AP-10 — Duplicate Code (DRY Violation)
- **Arquivo**: `models.py:12-21, 31-40, 304-313`, `models.py:171-201, 203-233`, `controllers.py:24-62, 64-96`
- **Severidade**: MEDIUM
- **Descrição**: 
  - Serialização de produto repetida 3 vezes com os mesmos 8 campos em `get_todos_produtos`, `get_produto_por_id` e `buscar_produtos`
  - `get_pedidos_usuario` e `get_todos_pedidos` têm lógica idêntica de fetching de itens (30+ linhas duplicadas)
  - Validações de produto duplicadas entre `criar_produto` e `atualizar_produto` (preço negativo, estoque negativo)
- **Impacto**: Bugs precisam ser corrigidos em múltiplos lugares. Código diverge com o tempo. Dificulta manutenção.
- **Recomendação**: Criar função `_produto_to_dict(row)` para serialização. Extrair lógica de itens do pedido para `_get_itens_pedido(pedido_id)`. Unificar validações de produto em função `validar_dados_produto(dados)`.

#### AP-11 — Missing Input Validation
- **Arquivo**: `controllers.py:146-165`, `controllers.py:167-185`, `controllers.py:188-220`
- **Severidade**: MEDIUM
- **Descrição**: 
  - `criar_usuario` (146-165): não valida formato de email, não verifica complexidade mínima de senha, não sanitiza inputs
  - `login` (167-185): não sanitiza email/senha antes de passar para query SQL (combinado com SQL Injection)
  - `criar_pedido` (188-220): não valida estrutura dos itens (cada item precisa de produto_id e quantidade?), não valida se produto_id é inteiro ou se quantidade > 0
- **Impacto**: Dados inválidos podem corromper o banco. Emails mal formatados. Senhas fracas. Exploração via inputs maliciosos.
- **Recomendação**: Adicionar validação de formato de email (regex ou biblioteca). Validar complexidade mínima de senha. Validar estrutura de itens com checagem de tipos e ranges. Usar bibliotecas como `marshmallow` ou `pydantic` para schema validation.

#### AP-12 — Bare Except / Empty Catch
- **Arquivo**: `controllers.py:10, 21, 60, 95, 108, 125, 133, 143, 164, 185, 218, 226, 234, 254, 261, 291`, `app.py:77`
- **Severidade**: MEDIUM
- **Descrição**: 17 ocorrências de `except Exception as e:` genérico em todo o projeto. A maioria apenas imprime o erro com `print()` e retorna HTTP 500 com a mensagem da exceção. Nenhum tratamento específico para erros de banco (sqlite3.Error), validação (ValueError, TypeError) ou conexão. Erros de produção expõem mensagens internas para o cliente.
- **Impacto**: Impossível diferenciar erros de negócio de erros de sistema. Mensagens de erro internas vazam para o cliente (ex: query SQL completa pode aparecer em `str(e)`). Sem rollback explícito em caso de falha no banco.
- **Recomendação**: Capturar exceções específicas: `sqlite3.IntegrityError`, `sqlite3.OperationalError`, `ValueError`, `TypeError`. Criar middleware de erro centralizado que loga o erro completo mas retorna mensagem genérica ao cliente.

#### AP-16 — Deprecated APIs Usage
- **Arquivo**: Nenhuma ocorrência detectada de APIs deprecated (sem `datetime.utcnow()`, `hashlib.md5()`, `@app.before_first_request`)
- **Severidade**: N/A
- **Descrição**: O projeto não usa APIs marcadas como deprecated no Python 3.12+ ou Flask 2.3+.
- **Impacto**: N/A
- **Recomendação**: N/A

#### AP-17 — Mixed Concerns / Side Effects
- **Arquivo**: `controllers.py:208-210`, `controllers.py:247-250`
- **Severidade**: MEDIUM
- **Descrição**: 
  - `criar_pedido` (208-210): após criar o pedido, dispara prints simulando envio de EMAIL, SMS e PUSH notification no mesmo bloco de código — se as notificações fossem reais e falhassem, impactariam a criação do pedido
  - `atualizar_status_pedido` (247-250): notificações condicionais (aprovação → "preparar envio", cancelamento → "devolver estoque") no mesmo handler
- **Impacto**: Se notificações falham, a transação principal pode ser afetada ou deixar estado inconsistente. Difícil testar a lógica de negócio sem disparar efeitos colaterais.
- **Recomendação**: Separar notificações em serviços dedicados usando padrão Observer/eventos. A criação do pedido deve apenas retornar sucesso; um listener/worker deve processar as notificações de forma assíncrona.

#### AP-10b — Import não utilizado (extensão do AP-10 — Duplicate Code)
- **Arquivo**: `models.py:1-2`
- **Severidade**: LOW (incluído para completude)
- **Descrição**: `from database import get_db` e `import sqlite3` — o `import sqlite3` na linha 2 não é usado diretamente (as queries usam o cursor, não sqlite3 diretamente).
- **Impacto**: Código morto, poluição do namespace.
- **Recomendação**: Remover `import sqlite3` do models.py.

---

### LOW (3)

#### AP-13 — Magic Numbers / Magic Strings
- **Arquivo**: `models.py:257-262`, `controllers.py:43-50`, `app.py:88`
- **Severidade**: LOW
- **Descrição**: 
  - `relatorio_vendas` (models.py:257-262): thresholds de desconto como magic numbers — `10000`, `0.1`, `5000`, `0.05`, `1000`, `0.02` sem explicação
  - `controllers.py:43-50`: limites de validação inline — `0` (preço/estoque mínimo), `2` (tamanho mínimo nome), `200` (tamanho máximo nome)
  - `app.py:88`: porta `5000` hardcoded
  - `controllers.py:52`: categorias válidas como lista inline
- **Impacto**: Difícil entender o significado dos valores sem contexto. Mudanças requerem caça aos números mágicos pelo código.
- **Recomendação**: Extrair para constantes nomeadas no topo do módulo ou em arquivo de configuração: `DESCONTO_THRESHOLD_ALTO = 10000`, `DESCONTO_PERCENTUAL_ALTO = 0.1`, `MIN_NOME_LENGTH = 2`, `MAX_NOME_LENGTH = 200`, `CATEGORIAS_VALIDAS = [...]`.

#### AP-14 — Print Statements as Logging
- **Arquivo**: `controllers.py:8, 11, 57, 61, 106, 161, 178, 182, 208-210, 219, 248, 250`, `app.py:56, 83-86`
- **Severidade**: LOW
- **Descrição**: 15+ ocorrências de `print()` usadas como logging. Incluem mensagens operacionais ("Listando N produtos", "Produto criado com ID: N"), erros ("ERRO:", "ERRO CRITICO"), notificações ("ENVIANDO EMAIL:", "NOTIFICAÇÃO:"), e bootstrap ("SERVIDOR INICIADO"). Nenhum uso do módulo `logging` do Python.
- **Impacto**: Sem controle de nível de log (DEBUG, INFO, WARN, ERROR). Logs vão para stdout sem timestamp, sem estrutura, sem possibilidade de filtrar por severidade. Impossível redirecionar para arquivo ou sistema de monitoramento.
- **Recomendação**: Substituir todos os `print()` por chamadas ao módulo `logging` com níveis apropriados: `logging.info()` para operações, `logging.error()` para erros, `logging.warning()` para alertas. Configurar formato com timestamp e nível.

#### AP-18 — Inconsistent Code Patterns
- **Arquivo**: `app.py:11-29` vs `app.py:32, 47, 59`
- **Severidade**: LOW
- **Descrição**: Mix de estilos de roteamento: `app.add_url_rule()` (12 endpoints, linhas 11-29) vs `@app.route()` (3 endpoints, linhas 32, 47, 59). Dois estilos diferentes no mesmo arquivo sem motivo aparente. Inconsistência no formato de resposta: alguns endpoints retornam `{"dados": x, "sucesso": True}`, outros `{"mensagem": x, "sucesso": True}`, `health_check` retorna formato completamente diferente.
- **Impacto**: Codebase confusa para novos desenvolvedores. Clientes da API precisam lidar com formatos inconsistentes.
- **Recomendação**: Padronizar em um estilo de roteamento (preferir `@app.route()` com Blueprints). Padronizar formato de resposta JSON com envelope consistente.

---

## Estatísticas Adicionais

### Distribuição por Arquivo

| Arquivo | Findings |
|---|---|
| models.py | 8 (AP-02, AP-03, AP-09, AP-10, AP-13, AP-15) |
| controllers.py | 7 (AP-03, AP-05, AP-11, AP-12, AP-14, AP-15, AP-17) |
| app.py | 5 (AP-01, AP-04, AP-05, AP-14, AP-18) |
| database.py | 2 (AP-01, AP-06) |
| **TOTAL** | **19** |

### Anti-Patterns Mais Frequentes

| Anti-Pattern | Ocorrências | Severidade |
|---|---|---|
| SQL Injection (AP-02) | 20 | CRITICAL |
| Bare Except (AP-12) | 17 | MEDIUM |
| Print Statements (AP-14) | 15 | LOW |
| N+1 Queries (AP-09) | 2 (com loops internos) | HIGH |
| Duplicate Code (AP-10) | 3 (serialização, itens pedido, validação) | MEDIUM |

---

## Checklist de Validação (Fase 3)

Preenchido APÓS a refatoração:

| Item | Status |
|---|---|
| Aplicação inicia sem erros | ✓ |
| Todos os endpoints respondem | ✓ |
| Estrutura MVC criada | ✓ |
| Configurações externalizadas | ✓ |
| Zero CRITICAL remanescentes | ✓ |
| Zero HIGH remanescentes | ✓ |

---

## Notas

- O projeto era pequeno (780 linhas) mas densamente populado com anti-patterns críticos — praticamente toda query no sistema era vulnerável a SQL Injection
- O endpoint `/admin/query` foi REMOVIDO — agora retorna 404
- A estrutura parcialmente existente (models.py, controllers.py separados) facilitou a migração para MVC completo
- O banco SQLite agora usa o padrão Flask `g` — conexão por request, sem estado global

## Resultado da Refatoração (Fase 3)

### Nova Estrutura MVC

```
src/
├── __init__.py
├── app.py                          # Entry point — apenas bootstrap
├── config/
│   ├── __init__.py
│   └── settings.py                 # Configuracoes via env vars
├── models/
│   ├── __init__.py
│   ├── database.py                 # Conexao Flask g (sem singleton)
│   ├── produto_model.py            # CRUD produtos — queries parametrizadas
│   ├── usuario_model.py            # CRUD usuarios — pbkdf2_hmac
│   └── pedido_model.py             # CRUD pedidos — batch fetching
├── controllers/
│   ├── __init__.py
│   ├── produto_controller.py       # Validacoes e regras de produto
│   ├── usuario_controller.py       # Autenticacao e validacao de email
│   └── pedido_controller.py        # Orquestracao de pedidos
├── views/
│   ├── __init__.py
│   └── routes.py                   # Blueprints — apenas roteamento
├── middlewares/
│   ├── __init__.py
│   └── error_handler.py            # Tratamento centralizado de erros
└── services/
    ├── __init__.py
    └── notification_service.py     # Side effects isolados
```

### Anti-Patterns Corrigidos

| Anti-Pattern | Status | Como foi corrigido |
|---|---|---|
| AP-01 Hardcoded Credentials | ✅ | Extraido para `.env` + `config/settings.py` |
| AP-02 SQL Injection (20 ocorrências) | ✅ | 100% queries com placeholders `?` |
| AP-03 God Module (models.py 314 linhas) | ✅ | Split em 3 arquivos: produto, usuario, pedido |
| AP-04 Raw SQL Endpoint | ✅ | Endpoint `/admin/query` removido |
| AP-05 Business Logic in Routes | ✅ | Extraido para controllers com validacao propria |
| AP-06 Global Mutable State | ✅ | Flask `g` — conexao por request |
| AP-07 Insecure Password | ✅ | pbkdf2_hmac + salt (32 bytes, 100k iteracoes) |
| AP-09 N+1 Queries | ✅ | Batch fetching com `WHERE id IN (...)` |
| AP-10 Duplicate Code | ✅ | Helpers `_produto_to_dict`, `_buscar_itens_pedidos` |
| AP-11 Missing Validation | ✅ | Validacao de email, senha, ranges, categorias |
| AP-12 Bare Except | ✅ | Error handlers centralizados + excecoes especificas |
| AP-13 Magic Numbers | ✅ | Constantes em `settings.py` |
| AP-14 Print Statements | ✅ | Modulo `logging` com niveis e timestamps |
| AP-15 Exposed Sensitive Data | ✅ | Sem `senha` nem `secret_key` nas respostas |
| AP-17 Mixed Concerns | ✅ | `NotificationService` isolado |
| AP-18 Inconsistent Patterns | ✅ | Blueprints padronizados, formato de resposta consistente |

### Validacao de Endpoints

Todos os 15 endpoints testados e funcionando:
- ✅ `GET /` — Home com listagem de endpoints
- ✅ `GET /produtos`, `GET /produtos/<id>` — Listagem e busca
- ✅ `POST /produtos`, `PUT /produtos/<id>`, `DELETE /produtos/<id>` — CRUD com validacao
- ✅ `GET /produtos/busca?q=...` — Busca parametrizada
- ✅ `GET /usuarios`, `GET /usuarios/<id>` — Sem campo senha
- ✅ `POST /usuarios` — Com validacao de email/senha
- ✅ `POST /login` — Autenticacao com hash seguro
- ✅ `GET /pedidos`, `POST /pedidos`, etc. — Gestao de pedidos
- ✅ `GET /relatorios/vendas` — Relatorio com metricas
- ✅ `GET /health` — Sem dados sensiveis
- ✅ `POST /admin/query` → **404** (removido com sucesso)
- ✅ `POST /admin/reset-db` — Reset seguro mantido
