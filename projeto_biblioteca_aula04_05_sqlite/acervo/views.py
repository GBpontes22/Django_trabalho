from django.shortcuts import redirect, render

from .forms import LivroForm
from .models import Livro


def lista_livros(request):
    livros = Livro.objects.all()

    nome = request.GET.get("nome", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    categoria = request.GET.get("categoria", "").strip()

    if nome:
        livros = livros.filter(titulo__icontains=nome)

    if tipo:
        livros = livros.filter(tipo_acervo=tipo)

    if categoria:
        livros = livros.filter(categoria=categoria)

    contexto = {
        "livros": livros,
        "nome": nome,
        "tipo": tipo,
        "categoria": categoria,
        "tipos_acervo": Livro.TIPOS_ACERVO,
        "categorias": Livro.CATEGORIAS,
    }

    return render(request, "acervo/lista.html", contexto)


def novo_livro(request):
    if request.method == "POST":
        form = LivroForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = LivroForm()

    return render(request, "acervo/form.html", {"form": form})
