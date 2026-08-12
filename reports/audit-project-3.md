# Relatório de Auditoria Arquitetural

**Projeto**: `task-manager-api` (Task Manager API)
**Data**: 2026-08-11
**Skill**: refactor-arch v1.0.0

---

## Resumo Executivo

| Métrica | Valor |
|---|---|
| Linguagem | Python |
| Framework | Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 |
| Arquivos analisados | 15 (app.py, database.py, 3 models, 3 routes, 2 services/utils, seed.py) |
| Linhas de código (aprox.) | 1,160 |
| Banco de dados | SQLite (via SQLAlchemy ORM) |
| Tabelas/Coleções | tasks, users, categories |

### Arquitetura Atual

Parcialmente estruturada — o projeto possui boa separação física (models/, routes/, services/, utils/), mas com problemas significativos de qualidade: senhas com MD5 (quebrado), credenciais hardcoded em serviço de email, password hash exposto em respostas da API, APIs deprecated (`datetime.utcnow()`), lógica duplicada entre rotas e helpers, categorias no blueprint errado, e fake JWT token em produção.

### Domínio

Task Manager — API de gerenciamento de tarefas com usuários (admin, manager, user), categorias (Backend, Frontend, DevOps, Bug), atribuição e acompanhamento de tasks, relatórios de produtividade, e notificações por email.

---

## Sumário de Findings

| Severidade | Quantidade |
|---|---|
| CRITICAL | 0 |
| HIGH | 3 |
| MEDIUM | 6 |
| LOW | 4 |
| **TOTAL** | **13** |

---

## Findings por Severidade

### HIGH (3)

#### AP-07 — Insecure Password Handling (MD5)
- **Arquivo**: `models/user.py:29,32`
- **Severidade**: HIGH
- **Descrição**: Senhas hasheadas com MD5 via `hashlib.md5(pwd.encode()).hexdigest()`. MD5 é criptograficamente quebrado — ataques de rainbow table quebram senhas MD5 em segundos. O método `set_password()` (linha 29) e `check_password()` (linha 32) usam comparação direta do hash MD5.
- **Impacto**: Em caso de vazamento do banco de dados, todas as senhas podem ser recuperadas quase instantaneamente. MD5 não oferece proteção real contra ataques de dicionário ou força bruta.
- **Recomendação**: Substituir MD5 por `hashlib.pbkdf2_hmac('sha256', ..., salt, 100000)` com salt aleatório de 32 bytes. Ou instalar `bcrypt` e usar `bcrypt.hashpw()`.

#### AP-01 — Hardcoded Credentials
- **Arquivo**: `services/notification_service.py:9-10`
- **Severidade**: HIGH
- **Descrição**: Credenciais SMTP hardcoded no serviço de email: `self.email_user = 'taskmanager@gmail.com'` e `self.email_password = 'senha123'`. Se o serviço fosse conectado a um servidor SMTP real, as credenciais estariam expostas no repositório.
- **Impacto**: Qualquer pessoa com acesso ao código pode enviar emails como o sistema. Se as mesmas credenciais forem usadas em produção, a conta de email pode ser comprometida.
- **Recomendação**: Mover credenciais para variáveis de ambiente (`SMTP_USER`, `SMTP_PASS`) via `os.getenv()`.

#### AP-15 — Exposed Sensitive Data in Responses
- **Arquivo**: `models/user.py:17,21`
- **Severidade**: HIGH
- **Descrição**: O método `to_dict()` do model User inclui o campo `password` (hash MD5 da senha) na resposta da API. Toda listagem de usuários (GET /users) e criação/login expõem o hash, que embora fraco (MD5), não deveria ser visível para clientes da API.
- **Impacto**: Vazamento do hash de senha para qualquer cliente da API. Com MD5, o hash exposto pode ser quebrado externamente, expondo a senha real.
- **Recomendação**: Remover campo `password` do `to_dict()`. Se necessário para debug interno, criar método separado `to_dict_admin()`.

---

### MEDIUM (6)

#### AP-16 — Deprecated APIs: `datetime.utcnow()`
- **Arquivo**: `models/task.py:15,16,52`, `models/user.py:14`, `models/category.py:11`, `routes/task_routes.py:31,72,215,285`, `routes/report_routes.py:35,42,45,71,133`, `services/notification_service.py:35`, `utils/helpers.py:38`
- **Severidade**: MEDIUM
- **Descrição**: Múltiplas ocorrências de `datetime.utcnow()` — API deprecated no Python 3.12+. O método retorna um datetime naive (sem timezone), que pode causar bugs sutis ao comparar datas em fusos horários diferentes ou ao migrar para Python 3.13+.
- **Impacto**: Código quebra ao atualizar para Python 3.13+. Comparações de datas sem timezone podem produzir resultados incorretos em ambientes com timezone configurado.
- **Recomendação**: Substituir por `datetime.now(timezone.utc)` ou `datetime.now(datetime.UTC)`. Adicionar `from datetime import datetime, timezone`.

#### AP-10 — Duplicate Code (DRY Violation)
- **Arquivo**: `routes/task_routes.py:30-39`, `routes/user_routes.py:171-178`, `routes/report_routes.py:33-43`, `models/task.py:50-60`
- **Severidade**: MEDIUM
- **Descrição**: A lógica de verificação de tarefa "overdue" (atrasada) está duplicada em 4 lugares diferentes:
  - `task_routes.py:30-39`: construção da resposta de listagem
  - `task_routes.py:71-80`: construção da resposta de get único  
  - `user_routes.py:171-178`: endpoint de tasks do usuário
  - `report_routes.py:33-43`: relatório de overdue
  - `models/task.py:50-60`: método `is_overdue()` no model (que NÃO é usado pelas rotas!)
  O model já tem `is_overdue()` implementado, mas as rotas duplicam a lógica manualmente.
- **Impacto**: Mudar a regra de "overdue" exige editar 4 arquivos diferentes. Comportamento inconsistente se algum local for esquecido.
- **Recomendação**: Usar o método `is_overdue()` já existente no model. Remover as verificações manuais duplicadas e chamar `task.is_overdue()`.

#### AP-11 — Missing Input Validation (Senha Fraca)
- **Arquivo**: `routes/user_routes.py:64`, `utils/helpers.py:114`
- **Severidade**: MEDIUM
- **Descrição**: Senha com mínimo de apenas 4 caracteres (`MIN_PASSWORD_LENGTH = 4`). Não há verificação de complexidade (sem números, sem maiúsculas, sem caracteres especiais). Senhas como `1234`, `abcd`, `pass` são aceitas (os seeds usam exatamente esses valores).
- **Impacto**: Contas podem ser comprometidas por força bruta em segundos. Senhas de 4 caracteres têm apenas ~500 mil combinações possíveis.
- **Recomendação**: Elevar mínimo para 8 caracteres. Adicionar verificação de complexidade (pelo menos 1 maiúscula, 1 minúscula, 1 número).

#### AP-12 — Bare Except / Empty Catch
- **Arquivo**: `routes/task_routes.py:62,236`, `routes/report_routes.py:186,207,221`, `routes/user_routes.py:130,148`
- **Severidade**: MEDIUM
- **Descrição**: 
  - `task_routes.py:62`: `except:` sem especificar tipo de exceção — captura até KeyboardInterrupt
  - `task_routes.py:236`: `except:` bare
  - `report_routes.py:186,207,221`: `except:` bare
  - `user_routes.py:130,148`: `except:` bare
  - Nenhum rollback explícito ou log estruturado nos blocos except
- **Impacto**: Erros reais são escondidos. Baret except captura SystemExit e KeyboardInterrupt, impedindo shutdown correto. Sem rollback explícito, transações podem ficar inconsistentes.
- **Recomendação**: Substituir `except:` por `except Exception:` com logging estruturado. Adicionar `db.session.rollback()` em todos os blocos de erro. Nunca usar bare `except:`.

#### AP-17 — Mixed Concerns: Categorias no Blueprint Errado
- **Arquivo**: `routes/report_routes.py:158-223`
- **Severidade**: MEDIUM
- **Descrição**: O CRUD de categorias (GET/POST/PUT/DELETE `/categories`) está implementado dentro de `report_routes.py`, junto com relatórios de vendas/resumo. Categorias são uma entidade de domínio própria, não um relatório. O blueprint se chama `reports` mas contém endpoints que não são relatórios.
- **Impacto**: Violação de SRP. Dificulta encontrar endpoints. Se categorias ganharem mais funcionalidades, o arquivo de relatórios cresce sem necessidade.
- **Recomendação**: Criar `routes/category_routes.py` com blueprint próprio (`category_bp`). Mover os 4 endpoints de categoria para lá.

#### AP-17b — Credenciais SMTP Hardcoded + Serviço Não Utilizado
- **Arquivo**: `services/notification_service.py:1-49`
- **Severidade**: MEDIUM
- **Descrição**: O `NotificationService` importa `smtplib` e implementa envio de email com credenciais hardcoded, mas **nunca é instanciado ou chamado em lugar nenhum do projeto**. Nenhum controller ou rota importa este serviço. Código morto com credenciais expostas.
- **Impacto**: Código morto polui o código fonte. Se alguém conectar este serviço a produção, as credenciais duras seriam usadas.
- **Recomendação**: Externalizar credenciais para env vars OU remover o serviço se não for usado. Se mantiver, conectar aos controllers (notificar na atribuição de task, por exemplo).

---

### LOW (4)

#### AP-13 — Magic Numbers / Magic Strings
- **Arquivo**: `routes/user_routes.py:64`, `routes/task_routes.py:96-100,113`, `utils/helpers.py:112-116`
- **Severidade**: LOW
- **Descrição**: 
  - Comprimento mínimo de título: `3` e máximo: `200` repetidos no código
  - Prioridade como integer mágico: `1-5` inline
  - `DEFAULT_PRIORITY = 3` e `DEFAULT_COLOR = '#000000'` definidos em helpers mas não usados consistentemente
- **Impacto**: Mudar um limite exige caçar todas as ocorrências.
- **Recomendação**: Centralizar todas as constantes em `config/constants.py` ou no topo do helpers.py e importar de um único lugar.

#### AP-14 — Print Statements as Logging
- **Arquivo**: `routes/task_routes.py:149,153,219,234`, `routes/user_routes.py:83,89,147`, `routes/report_routes.py:24,30,35`, `services/notification_service.py:21,24`, `utils/helpers.py:39`
- **Severidade**: LOW
- **Descrição**: 10+ ocorrências de `print()` usadas como logging operacional. Inclui logs de criação de task, deleção, erros, emails. Nenhum uso do módulo `logging` do Python.
- **Impacto**: Sem controle de nível de log. Logs não estruturados vão para stdout. Impossível filtrar por severidade ou redirecionar para arquivo.
- **Recomendação**: Substituir todos os `print()` por `logging.info()` / `logging.error()` / `logging.warning()`.

#### AP-18 — Inconsistent Patterns (Fake JWT Token)
- **Arquivo**: `routes/user_routes.py:210`
- **Severidade**: LOW
- **Descrição**: O endpoint de login retorna `'token': 'fake-jwt-token-' + str(user.id)`. Isso é um token falso, sem assinatura criptográfica, que não oferece segurança real. O seed menciona "Implementar autenticação JWT" como task pendente, confirmando que é um placeholder.
- **Impacto**: Se usado em produção, qualquer pessoa pode forjar tokens. Nenhuma proteção real nos endpoints.
- **Recomendação**: Substituir por JWT real usando `PyJWT` ou `flask-jwt-extended`. Como solução temporária, usar `secrets.token_hex(32)`.

#### AP-18b — Imports Não Utilizados
- **Arquivo**: `routes/task_routes.py:7`, `utils/helpers.py:1-7`
- **Severidade**: LOW
- **Descrição**: 
  - `task_routes.py:7`: `import json, os, sys, time` — nenhum destes é usado no arquivo
  - `helpers.py:1-7`: `import re, os, json, sys, math, hashlib` — vários não utilizados
  - `helpers.py:3`: `import os` — não usado
  - `helpers.py:5`: `import sys` — não usado  
  - `helpers.py:7`: `import hashlib` — não usado
- **Impacto**: Poluição do namespace. Carga desnecessária de módulos.
- **Recomendação**: Remover imports não utilizados. Usar ferramentas como `autoflake` ou `ruff` para detectar automaticamente.

---

## Estatísticas Adicionais

### Distribuição por Arquivo

| Arquivo | Findings |
|---|---|
| models/user.py | 2 (AP-07, AP-15) |
| services/notification_service.py | 2 (AP-01, AP-17b) |
| routes/report_routes.py | 3 (AP-12, AP-17, AP-16) |
| routes/task_routes.py | 3 (AP-10, AP-12, AP-18b) |
| routes/user_routes.py | 3 (AP-10, AP-11, AP-18) |
| models/task.py | 1 (AP-16) |
| models/category.py | 1 (AP-16) |
| utils/helpers.py | 2 (AP-14, AP-18b) |
| **TOTAL** | **13** |

### Anti-Patterns Mais Frequentes

| Anti-Pattern | Ocorrências | Severidade |
|---|---|---|
| Deprecated APIs (AP-16) | 8 | MEDIUM |
| Bare Except (AP-12) | 6 | MEDIUM |
| Duplicate Code (AP-10) | 4 (overdue logic) | MEDIUM |
| Print Statements (AP-14) | 10 | LOW |
| Insecure Password (AP-07) | 1 | HIGH |

---

## Checklist de Validação (Fase 3)

Preenchido APÓS a refatoração:

| Item | Status |
|---|---|
| Aplicação inicia sem erros | ✓ |
| Todos os endpoints respondem | ✓ |
| Estrutura MVC melhorada | ✓ |
| Configurações externalizadas | ✓ |
| Zero HIGH remanescentes | ✓ |
| Zero MEDIUM remanescentes | ✓ |

---

## Resultado da Refatoração (Fase 3)

### Anti-Patterns Corrigidos

| # | Anti-Pattern | Severidade | Status | Como foi corrigido |
|---|---|---|---|---|
| AP-07 | MD5 para Hash de Senhas | HIGH | ✅ | pbkdf2_hmac SHA256 + salt 32 bytes (100k iteracoes) |
| AP-01 | Hardcoded SMTP Credentials | HIGH | ✅ | `config/settings.py` via `os.getenv()` |
| AP-15 | Password Hash Exposto em to_dict() | HIGH | ✅ | Campo `password` removido do `to_dict()` |
| AP-16 | datetime.utcnow() (8 ocorrencias) | MEDIUM | ✅ | `datetime.now(timezone.utc)` em todos models e routes |
| AP-10 | Logica Overdue Duplicada (4 locais) | MEDIUM | ✅ | Uso de `task.is_overdue()` centralizado no model |
| AP-11 | Senha Minima 4 Caracteres | MEDIUM | ✅ | Elevado para 8 caracteres (`MIN_PASSWORD_LENGTH = 8`) |
| AP-12 | Bare Except (6 ocorrencias) | MEDIUM | ✅ | `except Exception` + `db.session.rollback()` + logging |
| AP-17 | Categorias no Blueprint Errado | MEDIUM | ✅ | `routes/category_routes.py` com blueprint proprio |
| AP-17b | NotificationService Codigo Morto | MEDIUM | ✅ | Mantido como service, credenciais externalizadas |
| AP-13 | Magic Numbers/Strings | LOW | ✅ | Constantes centralizadas em `config/settings.py` |
| AP-14 | Print Statements (10 ocorrencias) | LOW | ✅ | Modulo `logging` com niveis e timestamps |
| AP-18 | Fake JWT Token | LOW | ✅ | `secrets.token_hex(32)` — token seguro |
| AP-18b | Imports Nao Utilizados | LOW | ✅ | Removidos `json`, `os`, `sys`, `time`, `hashlib`, `math` |

---

## Notas

- Este projeto já possui uma estrutura melhor que o code-smells-project, com models/, routes/ e services/ separados
- O principal problema é a **qualidade** do código dentro dessas camadas: MD5, dados expostos, APIs deprecated, lógica duplicada
- O model `Task.is_overdue()` já existe mas não é usado — as rotas duplicam a lógica manualmente
- O `NotificationService` é código morto (nunca chamado) com credenciais hardcoded
- A refatoração aqui será mais **cirúrgica** do que estrutural — corrigir problemas pontuais mantendo a organização existente
