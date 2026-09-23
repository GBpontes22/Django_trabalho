## Funcionalidades

- CRUD de autores, livros, exemplares e membros.
- Acervo Digital ou Fisico e classificacao nas categorias 000 a 900.
- Pesquisa de livros por nome/autor, tipo e categoria.
- Registro de emprestimos e devolucoes.
- Um unico emprestimo ativo por exemplar.
- Multa automatica de R$ 1,00 por dia de atraso.
- Fila de reservas em ordem de solicitacao (FIFO).
- Prioridade do primeiro membro da fila quando um exemplar fica disponivel.
- Django Admin e painel com indicadores operacionais.
- Configuracao por variaveis de ambiente e suporte a PostgreSQL.
- Testes automatizados das regras e fluxos principais.

## Entidades do P1

`Autor`, `Livro`, `Exemplar`, `Membro`, `Emprestimo` e `Reserva`.

## Instalacao

No PowerShell, na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Crie o banco `biblioteca_db` no PostgreSQL e ajuste `DB_USER` e `DB_PASSWORD` no arquivo `.env`. Em seguida:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py popular_acervo
python manage.py runserver
```

Acesse o sistema em `http://127.0.0.1:8000/` e o Admin em `http://127.0.0.1:8000/admin/`.

Para uma demonstracao rapida sem PostgreSQL, altere no `.env`:

```env
DB_ENGINE=sqlite
DB_NAME=db.sqlite3
```

## Validacao

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Regras principais

- Somente membros ativos podem emprestar ou reservar.
- Um exemplar em manutencao ou emprestado nao pode ser emprestado novamente.
- Reservas sao aceitas quando nao ha exemplar disponivel.
- Havendo fila, apenas o primeiro membro pode receber o proximo exemplar.
- Ao devolver, o exemplar volta a ficar disponivel e a multa e calculada automaticamente.

## Referencias da disciplina

Os PDFs das aulas foram usados como referencia didatica. As instrucoes de ambiente e implementacao foram adaptadas para manter o projeto reproduzivel e testavel sem versionar credenciais, banco local ou ambiente virtual.

A justificativa das duas features obrigatorias esta em `RELATORIO_P1.md`.
