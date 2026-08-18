# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python -m src.app
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado
automaticamente no primeiro boot, já com produtos e usuários de exemplo.

> **Nota**: o código refatorado (padrão MVC) vive em `src/` e deve ser executado
> via `python -m src.app`. Os arquivos legados da raiz (`app.py`, `controllers.py`,
> `database.py`, `models.py`) — que continham os anti-patterns originais do desafio —
> foram removidos após a refatoração; a versão pré-refatoração está preservada no
> histórico do git (commit anterior).
