# Biblioteca Django

Consolidado das atividades das aulas 04 e 05 de Django: projeto, app, model, admin, views, URLs, templates, arquivos estaticos e formularios.

Os PDFs das aulas foram usados como referencia didatica. A implementacao deste repositorio segue a solicitacao da entrega: acrescentar tipo de acervo, categoria do acervo e pesquisa por nome, tipo e categoria.

## Como rodar

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Depois acesse `http://127.0.0.1:8000/`.

