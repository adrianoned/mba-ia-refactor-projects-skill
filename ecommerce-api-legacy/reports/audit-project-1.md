# Relatório de Auditoria Arquitetural

**Projeto**: `ecommerce-api-legacy` (LMS API)
**Data**: 2026-08-11
**Skill**: refactor-arch v1.0.0

---

## Resumo Executivo

| Métrica | Valor |
|---|---|
| Linguagem | JavaScript (Node.js) |
| Framework | Express.js ^4.18.2 |
| Arquivos analisados | 3 |
| Linhas de código (aprox.) | ~180 |
| Banco de dados | SQLite (em memória, via sqlite3 ^5.1.6) |
| Tabelas/Coleções | users, courses, enrollments, payments, audit_logs |

### Arquitetura Atual

Monolítica sem separação de camadas. O projeto possui apenas 3 arquivos fonte em um único diretório `src/`. Toda a lógica de negócio, acesso a dados, roteamento HTTP e inicialização do banco está concentrada na classe `AppManager` (141 linhas). Credenciais e funções utilitárias estão expostas em `utils.js`. Não há diretórios para models, controllers, routes, middlewares ou config.

### Domínio

LMS (Learning Management System) API com fluxo de checkout de cursos:
- **Cursos**: Clean Architecture, Docker — com preço e status active/inactive
- **Usuários**: cadastro com nome/email/senha durante checkout
- **Matrículas**: vincula usuário a curso após pagamento
- **Pagamentos**: processamento simulado (cartão iniciado com "4" = aprovado)
- **Auditoria**: logs de ações de checkout

---

## Sumário de Findings

| Severidade | Quantidade |
|---|---|
| CRITICAL | 4 |
| HIGH | 5 |
| MEDIUM | 8 |
| LOW | 3 |
| **TOTAL** | **20** |

---

## Findings por Severidade

### CRITICAL (4)

#### AP-01 — Hardcoded Credentials
- **Arquivo**: `src/utils.js:1-7`
- **Severidade**: CRITICAL
- **Descrição**: Objeto `config` contém 4 credenciais hardcoded como strings literais: `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"` (credenciais de banco), `paymentGatewayKey: "pk_live_1234567890abcdef"` (chave de gateway de pagamento live), `smtpUser: "no-reply@fullcycle.com.br"` (usuário SMTP). Todas visíveis em plaintext no repositório.
- **Impacto**: Qualquer pessoa com acesso ao código fonte tem credenciais de produção. A chave de gateway `pk_live_` sugere ambiente de produção real. Vazamento pode comprometer banco de dados, gateway de pagamento e servidor de email.
- **Recomendação**: Mover todas as credenciais para variáveis de ambiente (`process.env.DB_USER`, `process.env.PAYMENT_GATEWAY_KEY`, etc.) usando `dotenv`. Criar arquivo `config/settings.js` centralizado com valores default apenas para desenvolvimento. Adicionar `.env` ao `.gitignore`.

#### AP-03 — God Class / God Module
- **Arquivo**: `src/AppManager.js:1-141`
- **Severidade**: CRITICAL
- **Descrição**: A classe `AppManager` (141 linhas) concentra 5 responsabilidades distintas: (1) inicialização e schema do banco de dados (`initDb`, linhas 10-23), (2) lógica de checkout com processamento de pagamento (linhas 28-78), (3) geração de relatório financeiro com queries aninhadas (linhas 80-129), (4) deleção de usuários (linhas 131-137), (5) roteamento HTTP (`setupRoutes`). Opera sobre 5 tabelas diferentes (users, courses, enrollments, payments, audit_logs).
- **Impacto**: Impossível testar qualquer funcionalidade em isolamento. Qualquer mudança afeta todo o sistema. Acoplamento extremo entre domínios (usuários, cursos, pagamentos). Violação direta do SRP (Single Responsibility Principle).
- **Recomendação**: Separar em: `models/User.js`, `models/Course.js`, `models/Enrollment.js`, `models/Payment.js` para dados; `controllers/CheckoutController.js`, `controllers/ReportController.js` para lógica de negócio; `routes/index.js` para roteamento; `config/database.js` para inicialização do banco.

#### AP-03 (2ª ocorrência) — God Module (utils.js)
- **Arquivo**: `src/utils.js:1-25`
- **Severidade**: CRITICAL
- **Descrição**: O arquivo `utils.js` mistura 3 responsabilidades não relacionadas: (1) configuração com credenciais hardcoded (`config`), (2) estado global mutável (`globalCache`, `totalRevenue`), (3) função de criptografia caseira (`badCrypto`), (4) logging com efeito colateral de cache (`logAndCache`). Nome genérico "utils" mascara a diversidade de responsabilidades.
- **Impacto**: Módulo sem coesão — exports config, cache global, criptografia e logging. Impossível reutilizar componentes individuais sem carregar todo o módulo.
- **Recomendação**: Separar em módulos distintos: `config/settings.js` (config), `services/cacheService.js` (cache), `utils/crypto.js` (hash de senhas com algoritmo seguro), `utils/logger.js` (logging).

### HIGH (5)

#### AP-05 — Business Logic in Routes
- **Arquivo**: `src/AppManager.js:28-78` (POST /api/checkout)
- **Severidade**: HIGH
- **Descrição**: A rota de checkout contém 50 linhas de lógica de negócio inline dentro do handler HTTP: validação de campos (linhas 29-35), consulta de curso (linhas 37-38), consulta de usuário (linhas 40-41), processamento de pagamento com regra de bandeira de cartão (linhas 45-48), criação de usuário com hash de senha (linhas 66-72), criação de matrícula (linha 50), registro de pagamento (linha 54) e auditoria (linha 57). Tudo acoplado ao `req`/`res` do Express.
- **Impacto**: Regras de negócio não podem ser testadas sem iniciar o servidor HTTP. Duplicação inevitável se checkout for reutilizado. Acoplamento ao framework Express impede migração.
- **Recomendação**: Extrair para `controllers/CheckoutController` que recebe dados já extraídos (sem `req`/`res`) e retorna resultado ou erro. A rota apenas extrai parâmetros, delega ao controller e formata a resposta HTTP.

#### AP-05 (2ª ocorrência) — Business Logic in Routes
- **Arquivo**: `src/AppManager.js:80-129` (GET /api/admin/financial-report)
- **Severidade**: HIGH
- **Descrição**: Rota de relatório financeiro com 49 linhas de lógica complexa de agregação de dados: iteração sobre cursos, sub-consultas de matrículas, consultas de usuário e pagamento por matrícula, controle manual de concorrência com contadores `coursesPending`/`enrPending`. Tudo dentro do handler HTTP.
- **Impacto**: Lógica de relatório completamente inacessível sem HTTP. Controle manual de concorrência propenso a bugs. Impossível testar em isolamento.
- **Recomendação**: Extrair para `controllers/ReportController` com métodos assíncronos usando async/await e Promises. Separar queries em models. Usar `Promise.all()` no lugar de contadores manuais.

#### AP-06 — Global Mutable State
- **Arquivo**: `src/utils.js:9-10`
- **Severidade**: HIGH
- **Descrição**: Duas variáveis globais mutáveis no escopo do módulo: `let globalCache = {}` (linha 9) usado como cache compartilhado entre todas as requisições, e `let totalRevenue = 0` (linha 10) declarado mas nunca utilizado (dead code). A função `logAndCache` (linhas 12-15) modifica `globalCache` como efeito colateral.
- **Impacto**: `globalCache` é compartilhado entre todas as requisições — pode causar vazamento de dados entre usuários. Sem mecanismo de expiração ou limite de tamanho, cresce indefinidamente (memory leak). Condições de corrida em ambiente multi-requisição.
- **Recomendação**: Substituir `globalCache` por uma classe `CacheService` com escopo controlado e injetada via construtor. Remover `totalRevenue` (variável não utilizada).

#### AP-07 — Insecure Password Handling
- **Arquivo**: `src/utils.js:17-23`
- **Severidade**: HIGH
- **Descrição**: Função `badCrypto(pwd)` implementa criptografia caseira extremamente fraca: concatena substrings de Base64 em loop (10000 iterações), retorna apenas 10 caracteres. O nome da função (`badCrypto`) ironicamente reconhece a fragilidade. Senhas no seed do banco estão em plaintext (`'123'`, linha 18 do AppManager.js). No checkout, senha default é `"123456"` (AppManager.js:68) quando nenhuma é fornecida.
- **Impacto**: Hash trivialmente reversível — colisões garantidas com apenas 10 caracteres de output. Senhas podem ser recuperadas em segundos. Plaintext passwords no seed contaminam o ambiente de desenvolvimento.
- **Recomendação**: Substituir por `crypto.scrypt()` (módulo nativo do Node.js) com salt aleatório de 16+ bytes e keylen de 64 bytes. Armazenar no formato `salt:hash`. Implementar `verifyPassword()` separado. Remover senha default — exigir senha do usuário.

#### AP-15 — Exposed Sensitive Data in Responses
- **Arquivo**: `src/AppManager.js:45`
- **Severidade**: HIGH
- **Descrição**: Número de cartão de crédito (`cc`) e chave do gateway de pagamento (`config.paymentGatewayKey`) são expostos em `console.log` durante o processamento: `` console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`) ``. O log inclui o PAN (Primary Account Number) completo do cartão e a chave secreta do gateway.
- **Impacto**: Violação de PCI-DSS — dados de cartão não devem ser logados. Chave de gateway exposta em logs pode ser usada para realizar transações fraudulentas. Logs frequentemente são armazenados em sistemas de monitoramento com acesso amplo.
- **Recomendação**: Remover completamente o log do número do cartão. Se necessário log de auditoria, mascarar o cartão: `cc.slice(-4).padStart(cc.length, '*')`. Nunca logar `paymentGatewayKey` — no máximo logar os últimos 4 caracteres para identificação.

### MEDIUM (8)

#### AP-08 — Callback Hell
- **Arquivo**: `src/AppManager.js:37-77` (POST /api/checkout)
- **Severidade**: HIGH (rebaixado para MEDIUM por escopo reduzido)
- **Descrição**: A rota de checkout possui 4 níveis de callbacks aninhados: `db.get(courses)` → `db.get(users)` → `db.run(enrollments)` → `db.run(payments)` → `db.run(audit_logs)`. A função `processPaymentAndEnroll` é definida dentro do callback de usuário, com referência a `self` para acessar o `db`. 5 operações sequenciais formam uma pirâmide de indentação profunda.
- **Impacto**: Fluxo extremamente difícil de ler e debugar. Tratamento de erro inconsistente (cada nível tem seu próprio `if (err) return`). `self = this` (linha 26) é necessário apenas por causa dos callbacks que perdem o contexto.
- **Recomendação**: Converter para async/await usando `util.promisify()` nos métodos do sqlite3. O fluxo linear fica legível com `const course = await db.get(...)`, eliminando todos os níveis de aninhamento.

#### AP-08 (2ª ocorrência) — Callback Hell
- **Arquivo**: `src/AppManager.js:83-127` (GET /api/admin/financial-report)
- **Severidade**: MEDIUM
- **Descrição**: Rota de relatório com 3 níveis de callbacks aninhados + 2 loops `forEach`: `db.all(courses)` → `courses.forEach` → `db.all(enrollments)` → `enrollments.forEach` → `db.get(user)` → `db.get(payment)`. Controle de concorrência manual com variáveis `coursesPending` e `enrPending` para detectar quando todas as queries assíncronas completaram.
- **Impacto**: Race conditions potenciais no controle manual de concorrência. Código ilegível — 49 linhas para uma agregação que poderia ser feita em 20 com queries otimizadas. Resposta pode ser enviada múltiplas vezes se houver bug nos contadores.
- **Recomendação**: Reescrever com async/await e queries batch. Buscar todos os cursos, depois todas as matrículas de uma vez (`WHERE course_id IN (...)`), depois todos os usuários e pagamentos de uma vez. Montar o relatório em memória.

#### AP-09 — N+1 Queries
- **Arquivo**: `src/AppManager.js:89-126`
- **Severidade**: MEDIUM
- **Descrição**: O relatório financeiro executa queries em loops aninhados, resultando no clássico problema N+1:
  1. 1 query para listar cursos (N cursos)
  2. N queries para matrículas de cada curso
  3. M queries para usuário de cada matrícula (onde M = total de matrículas)
  4. M queries para pagamento de cada matrícula
  Com 2 cursos e 1 matrícula, são 1 + 2 + 1 + 1 = 5 queries. Com 100 cursos e 1000 matrículas, seriam 1 + 100 + 1000 + 1000 = 2101 queries.
- **Impacto**: Degradação severa de performance com crescimento de dados. Cada query é síncrona em callback, mas o overhead de I/O é cumulativo. Tempo de resposta cresce linearmente com número de cursos e matrículas.
- **Recomendação**: Substituir por 4 queries batch: (1) todos os cursos, (2) todas as matrículas com `WHERE course_id IN (...)`, (3) todos os usuários com `WHERE id IN (...)`, (4) todos os pagamentos com `WHERE enrollment_id IN (...)`. Montar o relatório em memória em O(n).

#### AP-10 — Duplicate Code (DRY Violation)
- **Arquivo**: `src/AppManager.js:37-38, 40-41, 50-51, 54-55, 69`
- **Severidade**: MEDIUM
- **Descrição**: Padrão de tratamento de erro repetido em todas as operações de banco: `if (err) return res.status(500).send("Erro ...")`. A construção manual de objetos de resposta (ex: `{ msg: "Sucesso", enrollment_id: enrId }`) é feita inline sem serializadores. Campos de requisição são extraídos manualmente com nomes abreviados e não documentados (`u`, `e`, `p`, `cid`, `cc`).
- **Impacto**: Mudanças no formato de resposta precisam ser feitas em múltiplos lugares. Tratamento de erro inconsistente — alguns retornam string pura, outros JSON. Nomes de campos inconsistentes entre entrada e banco.
- **Recomendação**: Criar helpers: `sendSuccess(res, data, statusCode)` e `sendError(res, message, statusCode)`. Usar objetos de request bem nomeados (`userName`, `email`, `password`, `courseId`, `cardNumber`). Centralizar formato de resposta.

#### AP-11 — Missing Input Validation
- **Arquivo**: `src/AppManager.js:29-35`
- **Severidade**: MEDIUM
- **Descrição**: Checkout valida apenas presença de campos (`if (!u || !e || !cid || !cc)`), sem nenhuma validação de formato ou tipo: email não é validado contra regex de email, senha não tem requisito mínimo de complexidade, `c_id` (courseId) não é verificado como número inteiro positivo, `card` (número do cartão) não é validado (comprimento, dígitos, algoritmo de Luhn).
- **Impacto**: Dados inválidos chegam ao banco (emails mal formatados, senhas vazias). Erros 500 ocorrem downstream em vez de serem capturados na entrada. Possível bypass de validações de negócio com dados maliciosos.
- **Recomendação**: Validar todos os inputs: email com regex, senha mín. 6 caracteres, courseId como inteiro positivo, cartão com formato numérico. Retornar erros específicos: "Email inválido", "Senha deve ter no mínimo 6 caracteres".

#### AP-12 — Bare Except / Empty Catch
- **Arquivo**: `src/AppManager.js:38, 41, 51, 55, 57, 69, 84, 92, 104, 106`
- **Severidade**: MEDIUM
- **Descrição**: Todas as operações de banco usam o mesmo padrão genérico de erro: `if (err) return res.status(500).send("Erro DB")` ou `"Erro Matrícula"`, `"Erro Pagamento"`, `"Erro ao criar usuário"`. O erro real (`err.message`) nunca é logado. Não há diferenciação entre tipos de erro (constraint violation vs connection error vs syntax error). Nenhum bloco try/catch no código inteiro.
- **Impacto**: Erros reais são completamente invisíveis — o operador vê apenas "Erro DB" sem saber a causa. Debugging requer modificação de código para logar o erro. Transações podem ficar inconsistentes (matrícula criada sem pagamento correspondente).
- **Recomendação**: Logar `err.message` em todos os handlers de erro. Usar middleware de erro centralizado do Express. Em operações multi-step (checkout), implementar rollback ou cleanup em caso de falha parcial.

#### AP-17 — Mixed Concerns / Side Effects
- **Arquivo**: `src/AppManager.js:59`
- **Severidade**: MEDIUM
- **Descrição**: A função `logAndCache` é chamada como efeito colateral dentro do fluxo de criação de auditoria (linha 59). Mistura logging, caching e resposta HTTP no mesmo bloco. Se `logAndCache` lançar exceção, a resposta HTTP nunca é enviada e o cliente fica pendente.
- **Impacto**: Side effects acoplados ao fluxo principal — se o cache falhar, o checkout falha. Violação do princípio de comando/consulta (CQS) — a operação de inserção de auditoria também modifica estado global do cache.
- **Recomendação**: Separar caching da resposta HTTP. Enviar resposta primeiro, depois atualizar cache em background. Ou usar try/catch no cache para que falhas de cache não afetem a resposta ao cliente.

#### AP-16 — Deprecated APIs Usage
- **Arquivo**: `src/AppManager.js:1-141`
- **Severidade**: MEDIUM
- **Descrição**: Uso de padrão de callbacks aninhados com `sqlite3` em vez de async/await com `util.promisify()`. Embora não seja estritamente "deprecated", o padrão de callbacks é considerado obsoleto desde Node.js 8+ (2017) com a introdução de async/await nativo. O código está inteiramente em estilo callback, sem nenhuma Promise ou async/await.
- **Impacto**: Código mais verboso e propenso a erros. Callback hell documentado em AP-08. Perde benefícios de stack traces assíncronos e tratamento de erros moderno.
- **Recomendação**: Promisify os métodos do sqlite3: `const { promisify } = require('util')`. Criar wrapper `Database` com métodos `getAsync`, `runAsync`, `allAsync`. Reescrever todos os handlers como async.

### LOW (3)

#### AP-13 — Magic Numbers / Magic Strings
- **Arquivo**: `src/AppManager.js:46, 68`
- **Severidade**: LOW
- **Descrição**: Números e strings mágicas sem explicação: `cc.startsWith("4")` (linha 46) — "4" é o prefixo de bandeira Visa, mas não documentado. Senha default `"123456"` (linha 68) é um magic string usado quando o campo `pwd` não é enviado. Porta `3000` em `utils.js:6` é um magic number (deveria ser configurável via `PORT` env var).
- **Impacto**: Lógica de negócio obscura — por que "4" significa aprovado? Senha default é um risco de segurança (AP-07) e não documentado. Mudanças requerem caça aos números mágicos pelo código.
- **Recomendação**: Extrair para constantes no topo do módulo: `const VISA_PREFIX = '4'`, `const DEFAULT_PORT = 3000`. Documentar com comentário: "Simula validação de bandeira — Visa (prefixo 4) = aprovado". Remover senha default.

#### AP-14 — Print Statements as Logging
- **Arquivo**: `src/app.js:13`, `src/AppManager.js:45`, `src/utils.js:13`
- **Severidade**: LOW
- **Descrição**: Uso de `console.log()` em 3 locais para logging operacional: início do servidor (app.js:13), processamento de pagamento com dados sensíveis (AppManager.js:45), e operação de cache (utils.js:13). Nenhuma biblioteca de logging estruturada (winston, pino, bunyan). Sem níveis de severidade, timestamps ou contexto.
- **Impacto**: Sem controle de verbosidade. Logs vão para stdout sem estrutura, difícil filtrar em produção. Informações sensíveis logadas sem máscara (ver AP-15).
- **Recomendação**: Integrar `pino` ou `winston` com níveis (debug, info, warn, error). Adicionar timestamps automáticos. Máscarar dados sensíveis nos logs. Usar `logger.info()` em vez de `console.log()`.

#### AP-18 — Inconsistent Code Patterns
- **Arquivo**: `src/AppManager.js:26, 54`
- **Severidade**: LOW
- **Descrição**: Uso inconsistente de `this` vs `self` para referenciar a instância da classe: `const self = this` é declarado na linha 26, mas o código alterna entre `this.db` (linhas 11-21, 37, 40, 50, 69, 83, 92, 104, 106, 131-133) e `self.db` (linhas 54, 57). Apenas 2 das 11 chamadas usam `self`. Campos de requisição usam nomes abreviados não documentados (`u`, `e`, `p`, `c_id`, `cc`), inconsistente com os nomes no banco.
- **Impacto**: Confusão sobre quando usar `this` vs `self`. Padrão de abreviação torna o código difícil de entender sem documentação externa.
- **Recomendação**: Usar arrow functions para preservar `this` automaticamente, eliminando a necessidade de `self`. Renomear campos de requisição para nomes descritivos: `userName`, `email`, `password`, `courseId`, `cardNumber`. Padronizar em um estilo consistente.

---

## Estatísticas Adicionais

### Distribuição por Arquivo

| Arquivo | Findings |
|---|---|
| `src/AppManager.js` | 14 |
| `src/utils.js` | 4 |
| `src/app.js` | 1 |
| `src/AppManager.js` + `src/utils.js` (compartilhado) | 1 |
| **TOTAL** | **20** |

### Anti-Patterns Mais Frequentes

| Anti-Pattern | Ocorrências | Severidade |
|---|---|---|
| AP-05 — Business Logic in Routes | 2 | HIGH |
| AP-03 — God Class / God Module | 2 | CRITICAL |
| AP-08 — Callback Hell | 2 | MEDIUM |
| AP-01 — Hardcoded Credentials | 1 | CRITICAL |
| AP-07 — Insecure Password Handling | 1 | HIGH |
| AP-06 — Global Mutable State | 1 | HIGH |
| AP-09 — N+1 Queries | 1 | MEDIUM |
| AP-10 — Duplicate Code | 1 | MEDIUM |
| AP-11 — Missing Input Validation | 1 | MEDIUM |
| AP-12 — Bare Except / Empty Catch | 1 | MEDIUM |
| AP-17 — Mixed Concerns | 1 | MEDIUM |
| AP-16 — Deprecated APIs Usage | 1 | MEDIUM |
| AP-15 — Exposed Sensitive Data | 1 | HIGH |
| AP-13 — Magic Numbers | 1 | LOW |
| AP-14 — Print as Logging | 1 | LOW |
| AP-18 — Inconsistent Patterns | 1 | LOW |

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

- O projeto é um boilerplate educacional ("desafio-arquitetura-ia-boilerplate") com 3 endpoints e seed data fixo
- Banco SQLite em memória (`:memory:`) — sem persistência entre reinicializações
- Os endpoints são: POST `/api/checkout`, GET `/api/admin/financial-report`, DELETE `/api/users/:id`
- A refatoração deve preservar exatamente o comportamento e formato de resposta dos 3 endpoints originais
- O nome "Frankenstein LMS" no log de startup reflete a natureza "monstro" do código atual
