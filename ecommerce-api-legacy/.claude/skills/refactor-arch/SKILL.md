---
name: refactor-arch
description: Skill de Auditoria e Refatoração Arquitetural — analisa, audita e refatora qualquer projeto para o padrão MVC, independente da tecnologia
version: 1.0.0
tags: [architecture, refactoring, mvc, audit, code-quality]
---

# Refactor-Arch: Auditoria e Refatoração Arquitetural

## Objetivo

Esta skill automatiza a análise, auditoria e refatoração de projetos de software para o padrão MVC (Model-View-Controller), independente da tecnologia utilizada.

Ela executa **3 fases sequenciais**:

1. **Fase 1 — Análise**: Detecta linguagem, framework, banco de dados, domínio e arquitetura atual do projeto
2. **Fase 2 — Auditoria**: Cruza o código contra o catálogo de anti-patterns, gera relatório detalhado e **pausa para confirmação**
3. **Fase 3 — Refatoração**: Reestrutura o projeto para MVC, aplicando os padrões de transformação e validando o resultado

## Instruções para o Agente

Ao receber o comando `/refactor-arch`, siga rigorosamente as 3 fases abaixo. Use os arquivos de referência como base de conhecimento para cada fase.

---

## FASE 1: ANÁLISE DO PROJETO

### Objetivo
Mapear a stack tecnológica, o domínio e a arquitetura atual do projeto **sem modificar nada**.

### Procedimento

1. **Liste todos os arquivos fonte** do projeto (exclua node_modules, venv, .git, __pycache__, dist, build)

2. **Detecte a linguagem e framework**:
   - Consulte o arquivo `project-analysis.md` para as heurísticas de detecção
   - Identifique package.json, requirements.txt, go.mod, pom.xml, Gemfile, etc.
   - Determine versões exatas lendo os arquivos de manifesto

3. **Identifique o banco de dados**:
   - Procure por strings de conexão, imports de ORM, arquivos de migração
   - Ex: `sqlite3`, `mongoose`, `sequelize`, `SQLAlchemy`, `psycopg2`, `pg`, `mysql2`

4. **Determine o domínio da aplicação**:
   - Analise nomes de entidades, endpoints, tabelas, comentários
   - Ex: "E-commerce API (produtos, pedidos, usuários)", "LMS API (cursos, matrículas, pagamentos)"

5. **Mapeie a arquitetura atual**:
   - Se todos os arquivos estão em 1-2 diretórios sem separação clara → "Monolítica sem separação de camadas"
   - Se há diretórios como models/, routes/, controllers/ mas com mistura de responsabilidades → "Parcialmente estruturada"
   - Se há clara separação com injeção de dependência → "Bem estruturada"
   - Conte os arquivos fonte e estime o total de linhas de código

6. **Liste as tabelas/coleções do banco** (se aplicável)

### Saída Esperada
Imprima um resumo formatado como:

```
================================
PHASE 1: PROJECT ANALYSIS  
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <principais dependências>
Domain:        <descrição do domínio>
Architecture:  <tipo de arquitetura — descrição>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas ou N/A>
================================
```

**IMPORTANTE**: Nesta fase, apenas ANALISE. Não modifique nenhum arquivo.

---

## FASE 2: AUDITORIA DE ARQUITETURA

### Objetivo
Cruzar o código contra o catálogo de anti-patterns, gerar um relatório de auditoria com achados precisos (arquivo e linha) e **pedir confirmação antes de modificar qualquer coisa**.

### Procedimento

1. **Carregue o catálogo de anti-patterns** do arquivo `anti-patterns-catalog.md`

2. **Analise cada arquivo fonte** procurando por todos os anti-patterns do catálogo:
   - Para cada anti-pattern, verifique os sinais de detecção descritos no catálogo
   - Ao encontrar um match, registre: arquivo exato, linha(s) exata(s), severidade e descrição
   - Verifique também APIs deprecated conforme seção específica do catálogo

3. **Classifique cada finding** conforme a escala de severidade:
   - **CRITICAL**: Falhas graves de segurança ou arquitetura (ex: SQL Injection, credenciais hardcoded, God Class)
   - **HIGH**: Violações fortes de MVC/SOLID (ex: lógica de negócio em controllers, acoplamento forte)
   - **MEDIUM**: Problemas de padronização, duplicação, performance (ex: queries N+1, validações ausentes)
   - **LOW**: Melhorias de legibilidade (ex: nomenclatura ruim, magic numbers)

4. **Gere o relatório** seguindo o template definido em `report-template.md`:
   - Resumo executivo com stack, arquivos analisados, linhas de código
   - Sumário com contagem por severidade
   - Lista de findings ordenada por severidade (CRITICAL → LOW)
   - Cada finding deve ter: severidade, tipo, arquivo:linha, descrição, impacto e recomendação

5. **Salve o relatório** em `reports/audit-project-<N>.md` (crie o diretório reports/ se não existir)

6. **PAUSE e PEÇA CONFIRMAÇÃO**:
   - Mostre o sumário do relatório
   - Pergunte explicitamente: "Deseja prosseguir com a Fase 3 — Refatoração? (s/n)"
   - **NÃO modifique nenhum arquivo até o usuário confirmar**

### Saída Esperada

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<N> lines of code

Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

Findings

[CRITICAL] <Tipo>
File: <arquivo>:<linha>
Description: <descrição do problema>
Impact: <impacto no sistema>
Recommendation: <solução recomendada>

... (repetir para cada finding)

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## FASE 3: REFATORAÇÃO PARA MVC

### Objetivo
Reestruturar o projeto para o padrão MVC, eliminando os problemas encontrados na Fase 2, e validar que a aplicação continua funcionando.

### Procedimento

**IMPORTANTE**: Antes de iniciar, faça backup dos arquivos originais ou certifique-se de que o código está commitado. O git deve estar limpo antes de começar.

1. **Planeje a nova estrutura** seguindo as guidelines em `mvc-guidelines.md`:
   - Defina a estrutura de diretórios alvo baseada no padrão MVC
   - Para Python/Flask: `src/config/`, `src/models/`, `src/controllers/`, `src/views/routes/`
   - Para Node.js/Express: `src/config/`, `src/models/`, `src/controllers/`, `src/routes/`
   - Adapte a nomenclatura conforme a convenção da linguagem

2. **Execute as transformações** seguindo o playbook em `refactoring-playbook.md`:
   - Para cada anti-pattern encontrado na Fase 2, aplique o padrão de transformação correspondente
   - Ordem recomendada:
     a. **Extraia configurações** primeiro (remova hardcoded credentials, crie módulo de config)
     b. **Crie Models** (extraia acesso a dados para models, use ORM adequado)
     c. **Crie Controllers** (extraia lógica de negócio dos handlers/rotas)
     d. **Separe Views/Routes** (mantenha apenas roteamento, delegue aos controllers)
     e. **Centralize error handling** (crie middleware de erro)
     f. **Remova código duplicado** (DRY)

3. **Aplique as correções de segurança** (sempre as primeiras):
   - Substitua credenciais hardcoded por variáveis de ambiente
   - Corrija SQL Injection usando queries parametrizadas
   - Substitua hashing inseguro (MD5, SHA1) por bcrypt/scrypt/argon2
   - Remova exposição de dados sensíveis em respostas

4. **Valide o resultado**:
   - Verifique se a aplicação inicia sem erros
   - Teste cada endpoint original para garantir que continua respondendo
   - Execute `python app.py` ou `node src/app.js` e verifique a saída
   - Se houver testes, execute-os

5. **Imprima o resultado final**:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<árvore de diretórios>

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly  
  ✓ Zero anti-patterns remaining
================================
```

### Regras Importantes para a Refatoração

- **Mantenha a aplicação funcionando**: A cada mudança significativa, teste se a aplicação ainda inicia
- **Não mude APIs públicas**: Endpoints devem manter mesma URL, método HTTP e formato de resposta
- **Preserve a lógica de negócio**: O comportamento deve ser idêntico ao original
- **Use as dependências existentes**: Não adicione novas bibliotecas a menos que estritamente necessário
- **Siga as convenções da linguagem**: Use snake_case para Python, camelCase para JavaScript/Node.js
- **Documente as mudanças**: Adicione comentários explicativos onde apropriado

---

## Pós-Execução

Após completar as 3 fases, informe ao usuário:

1. O relatório de auditoria foi salvo em `reports/audit-project-<N>.md`
2. O código refatorado está na branch atual
3. Instruções para rodar a aplicação e verificar os endpoints
4. Sugestão para commitar as alterações com uma mensagem descritiva
