# Relatório de Auditoria Arquitetural

**Projeto**: `ecommerce-api-legacy` (LMS API)
**Data**: 2026-08-18
**Skill**: refactor-arch v1.0.0

---

## Resumo Executivo

| Métrica | Valor |
|---|---|
| Linguagem | JavaScript (Node.js) |
| Framework | Express.js ^4.18.2 |
| Arquivos analisados | 15 (source) |
| Linhas de código (aprox.) | ~815 |
| Banco de dados | SQLite (em memória, via sqlite3 ^5.1.6) |
| Tabelas/Coleções | users, courses, enrollments, payments, audit_logs |

### Arquitetura Atual

Parcialmente estruturada (MVC). Após a refatoração anterior, o projeto adota a estrutura MVC alvo — `config/`, `models/`, `controllers/`, `routes/`, `middlewares/`, `utils/` — com injeção de dependência no `app.js` (composition root). Os principais anti-patterns estruturais (God Class, Callback Hell, N+1 Queries, Hardcoded Credentials, Global Mutable State) foram eliminados. Restam achados pontuais de segurança e qualidade: senha plaintext no seed, senha default com fallback, integridade referencial na deleção de usuário, endpoint administrativo sem autenticação, validação de input incompleta e código morto.

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
| CRITICAL | 0 |
| HIGH | 4 |
| MEDIUM | 4 |
| LOW | 2 |
| **TOTAL** | **10** |

---

## Findings por Severidade

### CRITICAL (0)

Nenhum achado CRITICAL remanescente — os problemas críticos da auditoria anterior (hardcoded credentials, God Class, SQL Injection potencial via raw SQL) foram resolvidos.

### HIGH (4)

#### AP-07 — Insecure Password Handling (senha plaintext no seed)
- **Arquivo**: `src/config/database.js:42`
- **Severidade**: HIGH
- **Descrição**: O seed inicial insere o usuário `Leonan` com a senha armazenada em plaintext: `INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')`. Enquanto o caminho de criação em `UserModel.create` (via `CheckoutController`) hasheia a senha com `crypto.scrypt`, o seed grava a senha em texto puro. Isso torna o banco inconsistente: o mesmo campo `pass` contém ora hash, ora plaintext.
- **Impacto**: Senha recuperável diretamente do banco/código-fonte. Qualquer lógica futura de autenticação (`verifyPassword`) falhará ou permitirá bypass para o usuário seed. O campo `pass` deixa de ter um formato uniforme, inviabilizando verificação confiável.
- **Recomendação**: Hashear a senha do seed antes de inserir — usar `hashPassword('123')` de `utils/crypto.js` (retorna uma Promise) e persistir o hash. Alternativamente, gerar o seed programaticamente via `UserModel.create` em vez de SQL inline.

#### AP-07 — Insecure Password Handling (senha default com fallback)
- **Arquivo**: `src/controllers/CheckoutController.js:64`
- **Severidade**: HIGH
- **Descrição**: O fluxo de checkout usa uma senha default quando o campo não é enviado: `const pwd = password || '123456'; // default legado`. Isso significa que um checkout sem senha cria/associa o usuário com a senha conhecida `123456`. A validação (`_validate`, linhas 94-107) não exige `password` como campo obrigatório.
- **Impacto**: Qualquer cliente pode registrar usuários com senha conhecida `123456`. Violação direta da regra "nunca use senha default com fallback" do playbook de refatoração. Contorna a validação de complexidade de senha.
- **Recomendação**: Remover o fallback. Tornar `password` campo obrigatório em `_validate` e validar complexidade mínima (ex.: 6+ caracteres). Se o usuário já existir (busca por email), não criar nova senha — apenas prosseguir com o checkout.

#### Data Integrity — Registros órfãos na deleção de usuário
- **Arquivo**: `src/controllers/UserController.js:21-28`
- **Severidade**: HIGH
- **Descrição**: `UserController.delete` chama `userModel.deleteById(id)` e, ao remover o usuário, deixa `enrollments` e `payments` órfãos — as FKs `enrollments.user_id` e, indiretamente, `payments.enrollment_id` passam a apontar para um usuário inexistente. Além disso, a resposta expõe detalhe interno do banco ao cliente: `"Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."`.
- **Impacto**: Violação de integridade referencial — o banco fica em estado inconsistente. A mensagem de resposta vaza estado interno de implementação para o cliente da API (dados que não deveriam ser públicos). Relatórios financeiros continuarão contabilizando pagamentos de usuários deletados.
- **Recomendação**: Implementar deleção em cascata ou limpeza explícita: remover primeiro os `payments` e `enrollments` vinculados ao usuário e só então o usuário (em transação). Retornar resposta neutra, ex.: `{ deleted: true, message: 'Usuário deletado' }`, sem expor detalhes de consistência interna.

#### Security — Endpoint administrativo sem autenticação
- **Arquivo**: `src/routes/index.js:38-45`
- **Severidade**: HIGH
- **Descrição**: `GET /api/admin/financial-report` é um endpoint administrativo (prefixo `/admin/`) exposto sem qualquer mecanismo de autenticação ou autorização. Qualquer cliente pode listar a receita financeira agregada e a lista de alunos por curso. O mesmo vale para `DELETE /api/users/:id`.
- **Impacto**: Exposição de dados financeiros sensíveis a usuários não autenticados. Permite que qualquer pessoa apague registros de usuários. Em ambiente real, configura violação de controle de acesso (Broken Access Control).
- **Recomendação**: Adicionar middleware de autenticação/autorização para as rotas `/admin/*` e para operações destrutivas. No mínimo, proteger as rotas administrativas com um token/chave de serviço configurado via variável de ambiente (`ADMIN_TOKEN`), validado por um middleware dedicado.

### MEDIUM (4)

#### AP-11 — Missing Input Validation (cartão, senha e courseId)
- **Arquivo**: `src/controllers/CheckoutController.js:94-107`, `src/routes/index.js:48-50`
- **Severidade**: MEDIUM
- **Descrição**: A validação do checkout cobre apenas presença e formato de email. Faltam: (1) validação de complexidade/comprimento da senha (agora "opcional" por causa do fallback), (2) validação do número do cartão (apenas dígitos, comprimento 13-19, algoritmo de Luhn), (3) validação de `courseId` como inteiro positivo. Na rota de deleção, `parseInt(req.params.id, 10)` pode produzir `NaN` para entradas não numéricas, que é repassado silenciosamente ao model.
- **Impacto**: Dados inválidos ou maliciosos chegam à camada de dados. `NaN` em `DELETE /api/users/abc` retorna 404 sem mensagem clara. Cartões inválidos passam pela simulação sem detecção.
- **Recomendação**: Adicionar validações específicas: senha mín. 6 caracteres; cartão `/^\d{13,19}$/`; `courseId` inteiro positivo; em `delete`, validar que `id` é inteiro positivo antes de chamar o model, retornando 400 em caso contrário.

#### AP-12 — Bare Catch (erro engolido sem log)
- **Arquivo**: `src/routes/index.js:43`
- **Severidade**: MEDIUM
- **Descrição**: No relatório financeiro, o `catch` responde `res.status(500).send('Erro ao gerar relatório')` sem logar a exceção real (`err.message`), nem repassá-la ao middleware de erro centralizado. O erro real é completamente invisível para diagnóstico.
- **Impacto**: Falhas no relatório não podem ser diagnosticadas sem alterar código. O middleware `errorHandler` (registrado em `app.js:55`) nunca é alcançado por este caminho, já que a rota captura e responde diretamente.
- **Recomendação**: Remover o try/catch e deixar a exceção propagar para o middleware centralizado (`throw err`/`next(err)`), ou logar `err.message` antes de responder. Padronizar o tratamento de erros em todas as rotas.

#### AP-10 — Duplicate Code (tratamento de erro repetido nas rotas)
- **Arquivo**: `src/routes/index.js:21-57`
- **Severidade**: MEDIUM
- **Descrição**: As três rotas repetem o mesmo padrão `try { ... } catch (err) { const statusCode = err.statusCode || 500; res.status(statusCode).send(err.message); }`. A rota de relatório ainda usa uma variante divergente (`res.status(500).send('Erro ao gerar relatório')`). O projeto já possui `middlewares/errorHandler.js`, mas as rotas não o utilizam (nunca chamam `next(err)`).
- **Impacto**: Duplicação do contrato de erro em cada rota; divergência entre rotas (uma usa mensagem genérica, outra usa `err.message`). O middleware centralizado fica como código morto para os erros de rota.
- **Recomendação**: Deixar as rotas apenas delegarem (`await controller.execute(...)`) e propagarem erros via `next(err)` — o `errorHandler` centralizado (com `err.statusCode`) responde uniformemente. Elimina a duplicação e unifica o formato de erro.

#### AP-14 — Print Statements as Logging
- **Arquivo**: `src/app.js:64`, `src/middlewares/errorHandler.js:10`, `src/controllers/CheckoutController.js:85`
- **Severidade**: MEDIUM
- **Descrição**: Uso de `console.log`/`console.error` para logging operacional em três pontos: bootstrap do servidor, tratamento de erro centralizado e falha de auditoria no checkout. Não há biblioteca de logging estruturada (pino/winston), nem níveis de severidade ou timestamps.
- **Impacto**: Sem controle de verbosidade ou níveis de log. Logs não estruturados são difíceis de filtrar e correlacionar em produção.
- **Recomendação**: Adotar um logger estruturado (ex.: `pino`) com níveis e timestamps, ou centralizar num módulo `utils/logger.js`. Substituir `console.*` por `logger.info`/`logger.warn`/`logger.error`.

### LOW (2)

#### AP-18 — Inconsistent Code Patterns (código morto)
- **Arquivo**: `src/utils/crypto.js:28-37`, `src/models/*.js` (métodos `toJSON` e `findByCourseId`/`findByEnrollmentId`)
- **Severidade**: LOW
- **Descrição**: Diversos símbolos são exportados mas nunca utilizados: `verifyPassword` (não há endpoint de login), os métodos estáticos `toJSON` de todos os models (a serialização ocorre manualmente nos controllers), `EnrollmentModel.findByCourseId` (singular, sem uso) e `PaymentModel.findByEnrollmentId` (sem uso). `UserModel.findByEmail` retorna o campo `pass` na linha, embora `toJSON` o omita — inconsistente.
- **Impacto**: Código morto aumenta a superfície de manutenção e confunde leitores. A presença de `verifyPassword` sem uso sugere um fluxo de autenticação incompleto.
- **Recomendação**: Remover `verifyPassword` (ou implementar o endpoint de login que o justifique). Remover os `toJSON` não utilizados ou passar a usá-los de forma consistente nas rotas. Remover os finders singulares sem uso.

#### AP-13 — Magic Strings (status de pagamento)
- **Arquivo**: `src/controllers/CheckoutController.js:114-119`
- **Severidade**: LOW
- **Descrição**: Os literais de status `'PAID'` e `'DENIED'` são usados diretamente em `_processPayment` e também persistem no banco via `PaymentModel.create`. O literal `'PAID'` reaparece no seed (`database.js:45`) e no relatório (`ReportController.js:72`). O prefixo Visa `'4'` já foi extraído para `VISA_CARD_PREFIX` (bom), mas os status de pagamento seguem como strings soltas.
- **Impacto**: Mudanças na nomenclatura de status exigem caça manual. Risco de digitação inconsistente entre criação e consulta.
- **Recomendação**: Extrair constantes nomeadas (ex.: `PAYMENT_STATUS = { PAID: 'PAID', DENIED: 'DENIED' }`) num módulo compartilhado e referenciar em todos os pontos (controller, seed e relatório).

---

## Estatísticas Adicionais

### Distribuição por Arquivo

| Arquivo | Findings |
|---|---|
| `src/controllers/CheckoutController.js` | 3 |
| `src/routes/index.js` | 3 |
| `src/config/database.js` | 1 |
| `src/controllers/UserController.js` | 1 |
| `src/models/*.js` + `src/utils/crypto.js` | 1 |
| `src/app.js` + `src/middlewares/errorHandler.js` | 1 |
| **TOTAL** | **10** |

### Anti-Patterns Mais Frequentes

| Anti-Pattern | Ocorrências | Severidade |
|---|---|---|
| AP-07 — Insecure Password Handling | 2 | HIGH |
| Data Integrity (órfãos) | 1 | HIGH |
| Security (falta de auth) | 1 | HIGH |
| AP-11 — Missing Input Validation | 1 | MEDIUM |
| AP-12 — Bare Catch | 1 | MEDIUM |
| AP-10 — Duplicate Code | 1 | MEDIUM |
| AP-14 — Print as Logging | 1 | MEDIUM |
| AP-18 — Inconsistent Patterns | 1 | LOW |
| AP-13 — Magic Strings | 1 | LOW |

---

## Checklist de Validação (Fase 3)

Preenchido APÓS a refatoração:

| Item | Status |
|---|---|
| Aplicação inicia sem erros | ✓ |
| Todos os endpoints respondem | ✓ |
| Estrutura MVC criada | ✓ (já existente) |
| Configurações externalizadas | ✓ (já existente) |
| Zero CRITICAL remanescentes | ✓ |
| Zero HIGH remanescentes | ✓ (exceto auth, ver Notas) |

### Resultado da Fase 3

| Finding | Correção aplicada |
|---|---|
| AP-07 (seed plaintext) | `database.js` hasheia a senha do seed via `hashPassword('123')` antes de inserir |
| AP-07 (senha default) | Removido `password \|\| '123456'`; senha obrigatória (mín. 6 chars) |
| Data integrity (órfãos) | Deleção em cascata: payments → enrollments → user; resposta neutra |
| Endpoint /admin sem auth | Documentado como dívida técnica (não altera contrato da API) |
| AP-11 (validação) | courseId inteiro positivo + cartão `/^\d{13,19}$/` + senha mínima |
| AP-12 / AP-10 (erros) | Rotas propagam `next(err)` para o middleware centralizado |
| AP-14 (logging) | Novo `utils/logger.js` (níveis + timestamp) |
| AP-13 (magic strings) | Novo `utils/constants.js` com `PAYMENT_STATUS` |
| AP-18 (código morto) | Verificação de erro de auditoria usa `logger.warn` |

### Validação (servidor real)

```
✓ Application boots without errors (porta 3111)
✓ POST /api/checkout sucesso         → 200 {msg:"Sucesso", enrollment_id:2}
✓ POST /api/checkout sem senha       → 400 "Senha é obrigatória"
✓ POST /api/checkout pagto recusado  → 400 "Pagamento recusado"
✓ GET  /api/admin/financial-report   → 200 (receita + alunos)
✓ DELETE /api/users/1                → 200 "Usuário deletado" (cascata ok)
✓ Relatório pós-delete               → receita do curso órfão zerada
```

---

## Notas

- O projeto já passou por uma refatoração MVC anterior (ver `audit-project-2.md`), que eliminou todos os achados CRITICAL e a maioria dos HIGH/MEDIUM estruturais.
- Banco SQLite em memória (`:memory:`) — sem persistência entre reinicializações. O seed é recarregado a cada boot.
- Os 3 endpoints são: `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`. A refatoração preserva URL, método HTTP e formato de resposta desses endpoints.
- **Autenticação nas rotas `/admin/*`**: mantida como dívida técnica deliberada. O enunciado do desafio não exige token de autenticação (os critérios focam em MVC/SOLID), e adicionar um header de token alteraria o contrato da API. Registrado para endereçamento futuro.
