from django.shortcuts import redirect, render

from .forms import LivroForm
from .models import Livro


def inicio(request):
    return redirect('acervo:lista')


def lista_livros(request):
    busca = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    livros = Livro.objects.all()

    if busca:
        livros = livros.filter(titulo__icontains=busca)
    if tipo:
        livros = livros.filter(tipo_acervo=tipo)
    if categoria:
        livros = livros.filter(categoria=categoria)

    contexto = {
        'livros': livros,
        'busca': busca,
        'tipo_selecionado': tipo,
        'categoria_selecionada': categoria,
        'tipos_acervo': Livro.TIPO_ACERVO_CHOICES,
        'categorias': Livro.CATEGORIA_CHOICES,
    }
    return render(request, 'acervo/lista.html', contexto)


def novo_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('acervo:lista')
    else:
        form = LivroForm()

    return render(request, 'acervo/form.html', {'form': form})

# Create your views here.
