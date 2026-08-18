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
> via `python -m src.app`. Os arquivos na raiz (`app.py`, `controllers.py`,
> `database.py`, `models.py`) são a versão **legada pré-refatoração**, mantida
> apenas como referência de entrada do desafio.
