# Template de Relatório de Auditoria

Este documento define o formato padronizado do relatório gerado na Fase 2 da skill refactor-arch.

---

## Estrutura do Relatório

O relatório deve ser salvo em `reports/audit-project-<N>.md` com a seguinte estrutura:

```markdown
# Relatório de Auditoria Arquitetural

**Projeto**: `<nome do projeto>`
**Data**: `<YYYY-MM-DD HH:MM>`
**Skill**: refactor-arch v1.0.0

---

## Resumo Executivo

| Métrica | Valor |
|---|---|
| Linguagem | `<linguagem>` |
| Framework | `<framework> <versão>` |
| Arquivos analisados | `<N>` |
| Linhas de código (aprox.) | `<N>` |
| Banco de dados | `<tipo>` |
| Tabelas/Coleções | `<lista>` |

### Arquitetura Atual

`<descrição da arquitetura detectada>`

### Domínio

`<descrição do domínio da aplicação>`

---

## Sumário de Findings

| Severidade | Quantidade |
|---|---|
| CRITICAL | `<N>` |
| HIGH | `<N>` |
| MEDIUM | `<N>` |
| LOW | `<N>` |
| **TOTAL** | **`<N>`** |

---

## Findings por Severidade

### CRITICAL (`<N>`)

#### `<ID>` — `<Título do Anti-Pattern>`
- **Arquivo**: `<caminho/arquivo>:<linha_inicial>-<linha_final>`
- **Severidade**: CRITICAL
- **Descrição**: `<descrição detalhada do problema encontrado>`
- **Impacto**: `<consequências deste problema no sistema>`
- **Recomendação**: `<solução sugerida>`

*(repetir para cada finding CRITICAL)*

### HIGH (`<N>`)

*(mesmo formato dos findings CRITICAL)*

### MEDIUM (`<N>`)

*(mesmo formato dos findings CRITICAL)*

### LOW (`<N>`)

*(mesmo formato dos findings CRITICAL)*

---

## Estatísticas Adicionais

### Distribuição por Arquivo

| Arquivo | Findings |
|---|---|
| `<arquivo>` | `<N>` |
| **TOTAL** | **`<N>`** |

### Anti-Patterns Mais Frequentes

| Anti-Pattern | Ocorrências | Severidade |
|---|---|---|
| `<nome>` | `<N>` | `<severidade>` |

---

## Checklist de Validação (Fase 3)

Preenchido APÓS a refatoração:

| Item | Status |
|---|---|
| Aplicação inicia sem erros | ✓ / ✗ |
| Todos os endpoints respondem | ✓ / ✗ |
| Estrutura MVC criada | ✓ / ✗ |
| Configurações externalizadas | ✓ / ✗ |
| Zero CRITICAL remanescentes | ✓ / ✗ |
| Zero HIGH remanescentes | ✓ / ✗ |

---

## Notas

`<observações adicionais, limitações da análise, sugestões futuras>`
```

---

## Regras de Formatação

1. **Ordem**: Findings devem ser ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW)
2. **Precisão**: Cada finding deve indicar arquivo e linha(s) exatas
3. **Acionabilidade**: Cada finding deve ter recomendação clara e específica
4. **Consistência**: Usar os nomes de anti-patterns do catálogo oficial
5. **Completude**: Se um anti-pattern aparece em múltiplos locais, agrupar ou listar cada ocorrência

## Exemplo de Finding Bem Escrito

```markdown
#### AP-01 — Hardcoded Credentials
- **Arquivo**: `app.py:7-8`
- **Severidade**: CRITICAL
- **Descrição**: SECRET_KEY hardcoded como string literal 'minha-chave-super-secreta-123' e DEBUG=True ativado diretamente no código. A chave secreta está exposta no repositório e visível para qualquer pessoa com acesso ao código fonte.
- **Impacto**: Sessões de usuário podem ser forjadas. Tokens JWT ou cookies de sessão assinados com esta chave são inseguros. O modo DEBUG expõe stack traces detalhados em produção.
- **Recomendação**: Mover SECRET_KEY para variável de ambiente (`os.getenv('SECRET_KEY')`) e DEBUG para `os.getenv('DEBUG', 'False').lower() == 'true'`. Usar python-dotenv para carregar arquivo .env em desenvolvimento.
```

## Exemplo de Finding Mal Escrito (EVITAR)

```markdown
- Código ruim no app.py — tem coisas hardcoded
```

---

## Salvamento do Relatório

1. Criar diretório `reports/` na raiz do projeto se não existir
2. Salvar como `reports/audit-project-<N>.md` onde N é 1, 2 ou 3
3. O arquivo deve ser Markdown válido e bem formatado
