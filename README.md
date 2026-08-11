# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

---

# Documentação da Skill

## A) Análise Manual

### Projeto 1: code-smells-project (Python/Flask — API de E-commerce)

Projeto monolítico com ~800 linhas em 4 arquivos. API de loja virtual com produtos, usuários, pedidos e relatórios de vendas.

| # | Severidade | Problema | Arquivo:Linha | Justificativa |
|---|---|---|---|---|
| 1 | **CRITICAL** | SQL Injection generalizado | `models.py:28,48-49,58-60,92,109-110,127-128,140,148-150,155-160,164-165,174,188,220,279,291-297` | Todas as queries usam concatenação de string (`"SELECT ... WHERE id = " + str(id)`), permitindo injeção de SQL em todos os endpoints. Dados de usuários, pedidos e produtos podem ser roubados ou destruídos. |
| 2 | **CRITICAL** | Hardcoded Credentials | `app.py:7` | SECRET_KEY = `'minha-chave-super-secreta-123'` exposta no código. Sessões Flask podem ser forjadas. |
| 3 | **CRITICAL** | God Module | `models.py:1-315` | 315 linhas com 4 domínios misturados (produtos, usuários, pedidos, relatórios). Violação de SRP — impossível testar isoladamente. |
| 4 | **CRITICAL** | Raw SQL Execution Endpoint | `app.py:59-78` | Endpoint `/admin/query` aceita SQL arbitrário do request body e executa diretamente. Acesso total ao banco. |
| 5 | **HIGH** | Business Logic in Controllers | `controllers.py:24-53` | Validação de nome, preço, estoque, categorias tudo inline no handler HTTP. Sem separação. |
| 6 | **HIGH** | Senhas em Plaintext | `models.py:109-110` | Login compara senha diretamente no SQL (`WHERE senha = '` + senha_input + `'`). Sem hash. |
| 7 | **HIGH** | Dados Sensíveis Expostos | `controllers.py:284-290` | Health check retorna `secret_key`, `db_path`, `debug`. Vazamento de informações internas. |
| 8 | **MEDIUM** | N+1 Queries | `models.py:187-201, 219-232` | Loop de pedidos faz query para itens e dentro faz query por produto. Centenas de queries desnecessárias. |
| 9 | **MEDIUM** | Código Duplicado | `models.py:171-201 vs 203-233` | Serialização de pedidos duplicada em `get_pedidos_usuario()` e `get_todos_pedidos()`. |
| 10 | **MEDIUM** | Concern Mixing | `controllers.py:208-210` | Envio de email, SMS e push notification simulados dentro do controller de pedido. Side effects misturados com lógica de negócio. |
| 11 | **LOW** | Magic Numbers | `models.py:258-262` | Faixas de desconto (10000, 5000, 1000) e percentuais (0.1, 0.05, 0.02) sem explicação. |
| 12 | **LOW** | Print Statements como Logging | `app.py, controllers.py, models.py` | Uso generalizado de `print()` sem timestamp, nível de log ou contexto. |
| 13 | **LOW** | Debug Mode em Produção | `app.py:8,88` | `DEBUG = True` e `debug=True` hardcoded. Exporia stack traces em produção. |
| 14 | **LOW** | Global Mutable State | `database.py:4-11` | Singleton `db_connection` global com `check_same_thread=False`. Risco em ambientes multi-thread. |

### Projeto 2: ecommerce-api-legacy (Node.js/Express — LMS API)

Projeto com ~250 linhas em 3 arquivos. API de LMS com checkout de cursos, relatório financeiro e gerenciamento de usuários.

| # | Severidade | Problema | Arquivo:Linha | Justificativa |
|---|---|---|---|---|
| 1 | **CRITICAL** | Hardcoded Secrets | `utils.js:3-7` | Credenciais de banco (`admin_master:senha_super_secreta_prod_123`), chave de gateway de pagamento (`pk_live_...`) e SMTP expostos no código. |
| 2 | **CRITICAL** | God Class | `AppManager.js:1-141` | Classe única contém init DB (5 tabelas), checkout (com nested callbacks) e relatório financeiro. 141 linhas, 3 responsabilidades completamente distintas. |
| 3 | **CRITICAL** | Criptografia Insegura | `utils.js:19-23` | Função `badCrypto()` — loop 10000x concatenando Base64. Totalmente quebrada. Senhas "hasheadas" com isso. |
| 4 | **HIGH** | Callback Hell / Pyramid of Doom | `AppManager.js:37-78` | Checkout com 5 níveis de callbacks aninhados. Ilegível, impossível debugar. |
| 5 | **HIGH** | Log de Dados de Cartão | `AppManager.js:45` | Número do cartão de crédito (`cc`) logado via `console.log`. Violação PCI-DSS. |
| 6 | **HIGH** | Global Mutable State | `utils.js:10-11` | `globalCache` e `totalRevenue` como variáveis globais mutáveis. Race conditions. |
| 7 | **MEDIUM** | N+1 Queries | `AppManager.js:80-129` | Relatório financeiro: loop de cursos → loop de matrículas → query de usuário → query de pagamento. Explosão combinatória. |
| 8 | **MEDIUM** | Cascade Delete sem Cleanup | `AppManager.js:131-137` | DELETE de usuário não remove matrículas, pagamentos e audit logs. Dados órfãos no banco. |
| 9 | **MEDIUM** | Validação de Input Ausente | `AppManager.js:29-33` | Checkout aceita dados brutos sem validação — sem verificar email, cartão, curso. |
| 10 | **LOW** | Variáveis com Nomes Ruins | `AppManager.js:29-32` | `u`, `e`, `p`, `cid`, `cc` — ilegível, sem significado. |
| 11 | **LOW** | Uso de `var` em vez de `let/const` | `utils.js:1,9,10,11` | ES6+ usa `let`/`const`. `var` é obsoleto e tem escopo de função problemático. |
| 12 | **LOW** | Buffer() Deprecated | `utils.js:22` | `Buffer.from(pwd)` deveria ser usado em vez de `Buffer(pwd)` (deprecated desde Node 6). |

### Projeto 3: task-manager-api (Python/Flask — Task Manager API)

Projeto com ~600 linhas em 13 arquivos. API de gerenciamento de tarefas com estrutura parcial (models/, routes/, services/, utils/).

| # | Severidade | Problema | Arquivo:Linha | Justificativa |
|---|---|---|---|---|
| 1 | **HIGH** | MD5 para Hash de Senhas | `user.py:29` | `hashlib.md5(pwd.encode()).hexdigest()` — MD5 é criptograficamente quebrado. Senhas podem ser quebradas em segundos com rainbow tables. |
| 2 | **HIGH** | Hardcoded Credentials em Service | `notification_service.py:10` | `self.email_password = 'senha123'` hardcoded no serviço de email. |
| 3 | **HIGH** | Dados Sensíveis Expostos | `user.py:21` | `to_dict()` inclui `password` (hash) na resposta da API. Vaza hash de senha para clientes. |
| 4 | **MEDIUM** | Lógica Duplicada (DRY) | `task_routes.py:30-57, report_routes.py:33-43` | Verificação de overdue duplicada em 3 lugares diferentes. Mudar a regra exige editar múltiplos arquivos. |
| 5 | **MEDIUM** | Categorias no Blueprint Errado | `report_routes.py:158-223` | CRUD de categorias está em `report_routes.py` em vez de ter seu próprio blueprint. Violação de separação de responsabilidades. |
| 6 | **MEDIUM** | Deprecated API: `datetime.utcnow()` | `task.py:15`, `user.py:14`, `category.py:11` | `datetime.utcnow()` é deprecated no Python 3.12+. Deve usar `datetime.now(timezone.utc)`. |
| 7 | **MEDIUM** | Bare Except Blocks | `task_routes.py:62,152`, `report_routes.py:186` | `except:` e `except Exception:` sem tratamento específico. Esconde erros reais. |
| 8 | **LOW** | Fake JWT Token | `user_routes.py:210` | `'fake-jwt-token-' + str(user.id)` — token falso sem assinatura. Não oferece segurança real. |
| 9 | **LOW** | Magic Strings Repetidas | `task_routes.py:110,177`, `helpers.py:110-112` | Listas de status válidos (`['pending', 'in_progress', 'done', 'cancelled']`) repetidas em vários lugares. |
| 10 | **LOW** | Imports Não Utilizados | `task_routes.py:7`, `helpers.py:1-7` | Vários imports não usados (`json`, `os`, `sys`, `hashlib`, `math`). |

---

## B) Construção da Skill

### Decisões de Design

A skill `refactor-arch` foi estruturada com **1 arquivo de instrução** (`SKILL.md`) e **5 arquivos de referência** que cobrem todas as áreas de conhecimento exigidas:

1. **`SKILL.md`** — O prompt principal que instrui o agente. Define as 3 fases sequenciais (Análise → Auditoria → Refatoração) com procedimentos detalhados para cada uma. Inclui:
   - Instruções explícitas para NÃO modificar arquivos na Fase 1 e Fase 2
   - Pausa obrigatória com confirmação do usuário antes da Fase 3
   - Validação pós-refatoração com checklist

2. **`project-analysis.md`** — Heurísticas de detecção automatizada:
   - Tabelas de mapeamento linguagem↔arquivo de manifesto
   - Sinais de detecção de framework por linguagem (Flask, Express, Django, FastAPI, NestJS, etc.)
   - Padrões de conexão para detectar banco de dados (SQLite, PostgreSQL, MySQL, MongoDB)
   - Classificação de arquitetura (Monolítica / Parcialmente estruturada / Bem estruturada)
   - Catálogo de APIs deprecated por linguagem

3. **`anti-patterns-catalog.md`** — 18 anti-patterns documentados:
   - Cada um com: severidade, descrição, sinais de detecção concretos (padrões de regex, estruturas de código), impacto e recomendação
   - Cobre todas as severidades (4 CRITICAL, 4 HIGH, 6 MEDIUM, 4 LOW)
   - Inclui AP-16 específico para APIs deprecated com tabelas por linguagem

4. **`report-template.md`** — Formato padronizado do relatório:
   - Resumo executivo com métricas
   - Sumário por severidade
   - Findings detalhados com arquivo:linha exatos
   - Checklist de validação pós-refatoração

5. **`mvc-guidelines.md`** — Regras do padrão MVC alvo:
   - Estrutura de diretórios para Python/Flask e Node.js/Express
   - Responsabilidades de cada camada (Config, Model, Controller, View/Route, Middleware, Entry Point)
   - Exemplos de código para cada camada em ambas as stacks
   - Checklist de validação MVC

6. **`refactoring-playbook.md`** — 17 padrões de transformação:
   - Cada um com: anti-pattern alvo, código antes (com problemas) e código depois (corrigido)
   - Exemplos em Python E Node.js quando aplicável
   - Ordem recomendada de aplicação (Segurança → Estrutura → Qualidade → Polimento)

### Anti-Patterns Incluídos e Justificativa

| # | Anti-Pattern | Severidade | Por que incluir |
|---|---|---|---|
| AP-01 | Hardcoded Credentials | CRITICAL | Presente em 3/3 projetos. É o problema mais comum e mais grave em código legado. |
| AP-02 | SQL Injection | CRITICAL | Vulnerabilidade #1 do OWASP Top 10. Presente massivamente no projeto 1. |
| AP-03 | God Class/Module | CRITICAL | Violação arquitetural fundamental. Presente nos 3 projetos. |
| AP-04 | Raw SQL Endpoint | CRITICAL | Backdoor acidental. Encontrado no projeto 1. |
| AP-05 | Business Logic in Routes | HIGH | Principal violação MVC. Presente nos 3 projetos em diferentes graus. |
| AP-06 | Global Mutable State | HIGH | Problema de design que causa bugs sutis. Presente nos projetos 1 e 2. |
| AP-07 | Insecure Password | HIGH | MD5 e plaintext encontrados nos 3 projetos. |
| AP-08 | Callback Hell | HIGH | Específico para Node.js. Essencial para provar agnosticismo. |
| AP-09 | N+1 Queries | MEDIUM | Problema de performance comum. Presente nos projetos 1 e 2. |
| AP-10 | Duplicate Code | MEDIUM | DRY violation. Presente nos 3 projetos. |
| AP-11 | Missing Validation | MEDIUM | Segurança e robustez. Projeto 2 sem validação alguma. |
| AP-12 | Bare Except | MEDIUM | Esconde bugs. Presente nos projetos 1 e 3. |
| AP-13 | Magic Numbers | LOW | Legibilidade. Projeto 1 com faixas de desconto mágicas. |
| AP-14 | Print as Logging | LOW | Operações. Todos os projetos usam print/console.log. |
| AP-15 | Exposed Sensitive Data | HIGH | Vazamento de dados. Hash de senha e secret_key em respostas. |
| AP-16 | Deprecated APIs | MEDIUM | datetime.utcnow() e Buffer() obsoletos. Preparação para futuro. |
| AP-17 | Mixed Concerns | MEDIUM | Side effects em controllers. Notificações mockadas no código. |
| AP-18 | Inconsistent Patterns | LOW | Qualidade. Mix de add_url_rule e @app.route. |

### Como Garantimos Agnosticismo de Tecnologia

1. **Heurísticas de detecção parametrizadas**: O `project-analysis.md` fornece tabelas de mapeamento por linguagem, não regras fixas
2. **Sinais de detecção multi-linguagem**: Cada anti-pattern no catálogo tem padrões de detecção para Python E Node.js
3. **Playbook com exemplos em ambas stacks**: O `refactoring-playbook.md` mostra antes/depois em Python e JavaScript
4. **MVC guidelines adaptativas**: Estruturas de diretório diferentes para Flask vs Express, mas mesmos princípios
5. **Validação em 3 projetos diferentes**: Python/Flask monolítico, Node.js/Express monolítico, Python/Flask semi-estruturado

### Desafios Encontrados

1. **Equilíbrio entre especificidade e generalidade**: Sinais de detecção muito específicos não generalizam; muito genéricos geram falsos positivos. Solução: padrões estruturais (ex: "query SQL dentro de loop") em vez de pattern matching exato.

2. **Callbacks vs Promises no Node.js**: Código legado Node.js usa callbacks, código moderno usa async/await. O playbook precisou cobrir ambas as formas.

3. **Projeto parcialmente organizado**: O task-manager-api já tem models/, routes/, services/ — a skill precisava identificar que a estrutura existe mas tem problemas de qualidade (MD5, dados expostos, lógica duplicada).

---

## C) Resultados

### Resultados por Projeto

| Métrica | Projeto 1 (code-smells) | Projeto 2 (ecommerce-legacy) | Projeto 3 (task-manager) |
|---|---|---|---|
| Stack detectada | Python / Flask 3.1.1 | Node.js / Express 4.18 | Python / Flask 3.0 |
| Arquivos analisados | 4 | 3 | 13 |
| CRITICAL | 4 | *a executar* | *a executar* |
| HIGH | 5 | *a executar* | *a executar* |
| MEDIUM | 7 | *a executar* | *a executar* |
| LOW | 3 | *a executar* | *a executar* |
| **TOTAL** | **19** | *a executar* | *a executar* |
| App funciona pós-refatoração | ✅ | *a executar* | *a executar* |

---

### Projeto 1 — code-smells-project (Python/Flask — E-commerce API)

#### Antes da Refatoração

```
code-smells-project/
├── app.py              # 88 linhas — rotas, config, endpoint SQL arbitrário
├── controllers.py      # 292 linhas — handlers + validações + side effects
├── models.py           # 314 linhas — 4 domínios, SQL Injection, N+1 queries
└── database.py         # 86 linhas — singleton global, seeds inline
```

**Problemas principais**: 100% das queries com SQL Injection, endpoint `/admin/query` executando SQL arbitrário, senhas em plaintext, SECRET_KEY hardcoded, God Module de 314 linhas com 4 domínios.

#### Depois da Refatoração

```
code-smells-project/
├── .env                            # Variáveis de ambiente
├── .gitignore                      # Exclusão de .env, *.db, reports/
├── src/
│   ├── app.py                      # Entry point — apenas bootstrap (50 linhas)
│   ├── config/
│   │   └── settings.py             # Configurações via env vars + constantes
│   ├── models/
│   │   ├── database.py             # Conexão Flask g (sem singleton global)
│   │   ├── produto_model.py        # CRUD produtos — queries parametrizadas
│   │   ├── usuario_model.py        # CRUD usuarios — pbkdf2_hmac + salt
│   │   └── pedido_model.py         # CRUD pedidos — batch fetching (sem N+1)
│   ├── controllers/
│   │   ├── produto_controller.py   # Validações e regras de produto
│   │   ├── usuario_controller.py   # Autenticação + validação de email
│   │   └── pedido_controller.py    # Orquestração de pedidos
│   ├── views/
│   │   └── routes.py               # Blueprints — apenas roteamento
│   ├── middlewares/
│   │   └── error_handler.py        # Tratamento centralizado de erros
│   └── services/
│       └── notification_service.py # Side effects isolados
└── reports/
    └── audit-project-1.md          # Relatório completo da auditoria
```

#### Anti-Patterns Corrigidos

| # | Anti-Pattern | Severidade | Status | Como foi corrigido |
|---|---|---|---|---|
| AP-01 | Hardcoded Credentials | CRITICAL | ✅ | `.env` + `config/settings.py` |
| AP-02 | SQL Injection (20 ocorrências) | CRITICAL | ✅ | 100% placeholders `?` parametrizados |
| AP-03 | God Module (314 linhas) | CRITICAL | ✅ | 3 models por domínio (produto, usuario, pedido) |
| AP-04 | Raw SQL Endpoint `/admin/query` | CRITICAL | ✅ | Endpoint removido — retorna 404 |
| AP-05 | Business Logic in Routes | HIGH | ✅ | Controllers dedicados com validação própria |
| AP-06 | Global Mutable State | HIGH | ✅ | Flask `g` — conexão por request |
| AP-07 | Insecure Password (plaintext) | HIGH | ✅ | pbkdf2_hmac SHA256 + salt (100k iterações) |
| AP-09 | N+1 Queries | HIGH | ✅ | Batch fetching `WHERE id IN (...)` |
| AP-15 | Exposed Sensitive Data | HIGH | ✅ | Sem `senha`, `secret_key`, `db_path` nas respostas |
| AP-10 | Duplicate Code | MEDIUM | ✅ | Helpers `_produto_to_dict`, `_buscar_itens_pedidos` |
| AP-11 | Missing Validation | MEDIUM | ✅ | Validação de email (regex), senha, ranges, categorias |
| AP-12 | Bare Except (17 ocorrências) | MEDIUM | ✅ | Error handlers centralizados + exceções específicas |
| AP-17 | Mixed Concerns / Side Effects | MEDIUM | ✅ | `NotificationService` isolado |
| AP-13 | Magic Numbers | LOW | ✅ | Constantes em `settings.py` (FAIXAS_DESCONTO, etc.) |
| AP-14 | Print Statements (15 ocorrências) | LOW | ✅ | Módulo `logging` com níveis e timestamps |
| AP-18 | Inconsistent Patterns | LOW | ✅ | Blueprints padronizados, formato de resposta consistente |

#### Validação de Endpoints

Todos os **15 endpoints** testados e funcionando após a refatoração:

```
✅ GET  /                          — Home com listagem de endpoints
✅ GET  /health                    — Health check sem dados sensíveis
✅ GET  /produtos                  — Listagem de produtos
✅ GET  /produtos/<id>             — Busca por ID
✅ POST /produtos                  — Criação com validação
✅ PUT  /produtos/<id>             — Atualização com validação
✅ DELETE /produtos/<id>           — Soft-delete
✅ GET  /produtos/busca?q=...      — Busca parametrizada
✅ GET  /usuarios                  — Listagem sem campo senha
✅ GET  /usuarios/<id>             — Busca sem campo senha
✅ POST /usuarios                  — Criação com validação de email/senha
✅ POST /login                     — Autenticação com pbkdf2_hmac
✅ GET  /pedidos                   — Listagem (sem N+1)
✅ POST /pedidos                   — Criação com notificações isoladas
✅ GET  /relatorios/vendas         — Relatório com métricas
✅ POST /admin/query → 404         — Endpoint removido com sucesso
✅ POST /admin/reset-db            — Reset seguro mantido
```

#### Checklist de Validação — Projeto 1

| Fase | Item | Status |
|---|---|---|
| **Fase 1** | Linguagem detectada corretamente | ✅ Python |
| | Framework detectado corretamente | ✅ Flask 3.1.1 |
| | Domínio descrito corretamente | ✅ E-commerce API |
| | Arquivos analisados condizem | ✅ 4 arquivos |
| **Fase 2** | Relatório segue o template | ✅ |
| | Findings com arquivo e linha exatos | ✅ |
| | Ordenados por severidade | ✅ CRITICAL → LOW |
| | ≥ 5 findings | ✅ 19 findings |
| | APIs deprecated verificadas | ✅ |
| | Pausa e confirmação | ✅ |
| **Fase 3** | Estrutura MVC criada | ✅ |
| | Configuração externalizada | ✅ `.env` + `settings.py` |
| | Models por domínio | ✅ 3 arquivos de model |
| | Views/Routes separadas | ✅ Blueprints |
| | Controllers com lógica de negócio | ✅ 3 controllers |
| | Error handling centralizado | ✅ `middlewares/error_handler.py` |
| | Entry point limpo | ✅ `src/app.py` (bootstrap) |
| | Aplicação inicia sem erros | ✅ |
| | Endpoints originais respondem | ✅ 15/15 |

### Projeto 2 e 3

*Resultados serão preenchidos após a execução da skill nos projetos restantes.*

#### Checklist de Validação — Projeto 2 (ecommerce-api-legacy)

*A executar.*

#### Checklist de Validação — Projeto 3 (task-manager-api)

*A executar.*

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e autenticado
- **Python 3.10+** (para os projetos Flask)
- **Node.js 18+** (para o projeto Express)
- Dependências de cada projeto instaladas

### Comandos

```bash
# Instalar dependências (antes de executar a skill)
cd code-smells-project && pip install -r requirements.txt
cd ../ecommerce-api-legacy && npm install
cd ../task-manager-api && pip install -r requirements.txt

# Projeto 1 — Python/Flask E-commerce API
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — Node.js/Express LMS API
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — Python/Flask Task Manager API
cd ../task-manager-api
claude "/refactor-arch"
```

### Como Validar

**Projeto 1 (Flask — refatorado):**
```bash
cd code-smells-project
PYTHONPATH=. python src/app.py
# Acessar: http://localhost:5000
# Testar endpoints:
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/produtos
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"email":"admin@loja.com","senha":"admin123"}'
# Verificar que /admin/query foi removido:
curl -X POST http://localhost:5000/admin/query -H "Content-Type: application/json" -d '{"sql":"SELECT 1"}'
# Deve retornar 404
```

**Projeto 2 (Express):**
```bash
cd ecommerce-api-legacy
npm start
# Testar endpoints:
curl http://localhost:3000/
```

**Projeto 3 (Flask):**
```bash
cd task-manager-api
python app.py
# ou (após refatoração)
PYTHONPATH=. python src/app.py
# Testar endpoints:
curl http://localhost:5000/
curl http://localhost:5000/health
```

### Estrutura da Skill

```
.claude/skills/refactor-arch/
├── SKILL.md                    # Prompt principal (3 fases)
├── project-analysis.md         # Heurísticas de detecção de stack
├── anti-patterns-catalog.md    # 18 anti-patterns com sinais de detecção
├── report-template.md          # Template do relatório de auditoria
├── mvc-guidelines.md           # Regras do padrão MVC alvo
└── refactoring-playbook.md     # 17 padrões de transformação com exemplos
```

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.