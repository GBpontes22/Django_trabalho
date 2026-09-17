# Projeto Biblioteca — Aulas 04 e 05

Projeto em Django para consolidar as atividades das Aulas 04 e 05.

## Banco de dados
Este projeto foi configurado com **SQLite**, portanto não precisa de PostgreSQL, servidor de banco ou configuração de usuário/senha.

O arquivo `db.sqlite3` será criado automaticamente após executar as migrations.

## Como executar no VS Code

No terminal, dentro da pasta do projeto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse:

- Sistema: http://127.0.0.1:8000/livros/
- Admin: http://127.0.0.1:8000/admin/

## Funcionalidades

- Cadastro de livros
- Tipo de acervo: Digital ou Físico
- Categorias:
  - 000 – Generalidades e Informação
  - 100 – Filosofia e Psicologia
  - 200 – Religião e Teologia
  - 300 – Ciências Sociais e Direito
  - 400 – Linguística e Idiomas
  - 500 – Ciências Puras (Exatas e Naturais)
  - 600 – Ciências Aplicadas (Tecnologia)
  - 700 – Artes e Recreação
  - 800 – Literatura
  - 900 – História e Geografia
- Busca por nome
- Filtro por tipo de acervo
- Filtro por categoria
- Django Admin
- ModelForm
- CSRF
- Templates com herança
- Migrations

## Estrutura

- `biblioteca/` — configuração do projeto
- `acervo/` — aplicação principal
- `templates/` — páginas HTML
- `static/` — CSS
- `manage.py` — gerenciamento do Django
- `db.sqlite3` — banco SQLite, criado localmente

## Observação sobre commits

Para atender ao requisito de pelo menos 10 commits, faça os commits por etapas no Git, por exemplo:

1. Estrutura inicial do projeto
2. Configuração do Django
3. Criação do app acervo
4. Criação do model Livro
5. Migrations
6. Configuração do Admin
7. Criação do formulário
8. Criação da view de listagem
9. Criação das URLs
10. Criação dos templates
11. Implementação da busca
12. Ajustes de CSS
13. Testes finais

Os commits precisam ser feitos no seu próprio repositório GitHub.
