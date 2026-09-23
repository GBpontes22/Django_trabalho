from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    AutorForm,
    EmprestimoForm,
    ExemplarForm,
    LivroForm,
    MembroForm,
    ReservaForm,
)
from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva
from .services import (
    cancelar_reserva,
    registrar_devolucao,
    registrar_emprestimo,
    registrar_reserva,
)


def _mensagem_validacao(request, erro):
    for mensagem in erro.messages:
        messages.error(request, mensagem)


def _formulario(request, *, form_class, titulo, voltar, instance=None, initial=None):
    form = form_class(request.POST or None, instance=instance, initial=initial)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{titulo} salvo com sucesso.')
        return redirect(voltar)
    return render(
        request,
        'acervo/form.html',
        {'form': form, 'titulo_form': titulo, 'voltar_url': reverse(voltar)},
    )


def _excluir(request, *, objeto, titulo, voltar):
    if request.method == 'POST':
        try:
            objeto.delete()
            messages.success(request, f'{titulo} excluido com sucesso.')
        except ProtectedError:
            messages.error(
                request,
                f'{titulo} nao pode ser excluido porque possui registros relacionados.',
            )
        return redirect(voltar)
    return render(
        request,
        'acervo/confirmar_exclusao.html',
        {'objeto': objeto, 'titulo_form': titulo, 'voltar_url': reverse(voltar)},
    )


def inicio(request):
    return redirect('acervo:dashboard')


def dashboard(request):
    contexto = {
        'total_livros': Livro.objects.count(),
        'total_exemplares': Exemplar.objects.count(),
        'exemplares_disponiveis': Exemplar.objects.filter(
            status=Exemplar.STATUS_DISPONIVEL
        ).count(),
        'emprestimos_ativos': Emprestimo.objects.filter(devolvido_em__isnull=True).count(),
        'emprestimos_atrasados': Emprestimo.objects.filter(
            devolvido_em__isnull=True,
            vencimento__lt=timezone.localdate(),
        ).count(),
        'reservas_ativas': Reserva.objects.filter(
            status=Reserva.STATUS_AGUARDANDO
        ).count(),
    }
    return render(request, 'acervo/dashboard.html', contexto)


def lista_livros(request):
    busca = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    livros = Livro.objects.select_related('autor').annotate(
        total_exemplares=Count('exemplares'),
        exemplares_disponiveis=Count(
            'exemplares',
            filter=Q(exemplares__status=Exemplar.STATUS_DISPONIVEL),
        ),
        exemplares_emprestados=Count(
            'exemplares',
            filter=Q(exemplares__status=Exemplar.STATUS_EMPRESTADO),
        ),
    )
    if busca:
        livros = livros.filter(
            Q(titulo__icontains=busca) | Q(autor__nome__icontains=busca)
        )
    if status == Exemplar.STATUS_DISPONIVEL:
        livros = livros.filter(exemplares_disponiveis__gt=0)
    elif status == Exemplar.STATUS_EMPRESTADO:
        livros = livros.filter(exemplares_emprestados__gt=0)
    if tipo:
        livros = livros.filter(tipo_acervo=tipo)
    if categoria:
        livros = livros.filter(categoria=categoria)
    return render(
        request,
        'acervo/lista.html',
        {
            'livros': livros,
            'busca': busca,
            'status_selecionado': status,
            'status_acervo': [
                (Exemplar.STATUS_DISPONIVEL, 'Disponivel'),
                (Exemplar.STATUS_EMPRESTADO, 'Emprestado'),
            ],
            'tipo_selecionado': tipo,
            'categoria_selecionada': categoria,
            'tipos_acervo': Livro.TIPO_ACERVO_CHOICES,
            'categorias': Livro.CATEGORIA_CHOICES,
        },
    )


def novo_livro(request):
    return _formulario(
        request,
        form_class=LivroForm,
        titulo='Novo livro',
        voltar='acervo:lista',
    )


def editar_livro(request, pk):
    return _formulario(
        request,
        form_class=LivroForm,
        titulo='Editar livro',
        voltar='acervo:lista',
        instance=get_object_or_404(Livro, pk=pk),
    )


def excluir_livro(request, pk):
    return _excluir(
        request,
        objeto=get_object_or_404(Livro, pk=pk),
        titulo='Livro',
        voltar='acervo:lista',
    )


def lista_autores(request):
    busca = request.GET.get('q', '').strip()
    autores = Autor.objects.annotate(total_livros=Count('livros'))
    if busca:
        autores = autores.filter(nome__icontains=busca)
    return render(
        request,
        'acervo/autores.html',
        {'autores': autores, 'busca': busca},
    )


def novo_autor(request):
    return _formulario(
        request,
        form_class=AutorForm,
        titulo='Novo autor',
        voltar='acervo:autores',
    )


def editar_autor(request, pk):
    return _formulario(
        request,
        form_class=AutorForm,
        titulo='Editar autor',
        voltar='acervo:autores',
        instance=get_object_or_404(Autor, pk=pk),
    )


def excluir_autor(request, pk):
    return _excluir(
        request,
        objeto=get_object_or_404(Autor, pk=pk),
        titulo='Autor',
        voltar='acervo:autores',
    )


def lista_exemplares(request):
    busca = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    exemplares = Exemplar.objects.select_related('livro', 'livro__autor')
    if busca:
        exemplares = exemplares.filter(
            Q(codigo__icontains=busca) | Q(livro__titulo__icontains=busca)
        )
    if status:
        exemplares = exemplares.filter(status=status)
    return render(
        request,
        'acervo/exemplares.html',
        {'exemplares': exemplares, 'busca': busca, 'status': status, 'status_choices': Exemplar.STATUS_CHOICES},
    )


def novo_exemplar(request):
    return _formulario(
        request,
        form_class=ExemplarForm,
        titulo='Novo exemplar',
        voltar='acervo:exemplares',
    )


def editar_exemplar(request, pk):
    return _formulario(
        request,
        form_class=ExemplarForm,
        titulo='Editar exemplar',
        voltar='acervo:exemplares',
        instance=get_object_or_404(Exemplar, pk=pk),
    )


def excluir_exemplar(request, pk):
    return _excluir(
        request,
        objeto=get_object_or_404(Exemplar, pk=pk),
        titulo='Exemplar',
        voltar='acervo:exemplares',
    )


def lista_membros(request):
    busca = request.GET.get('q', '').strip()
    membros = Membro.objects.annotate(
        emprestimos_ativos=Count(
            'emprestimos', filter=Q(emprestimos__devolvido_em__isnull=True)
        )
    )
    if busca:
        membros = membros.filter(Q(nome__icontains=busca) | Q(email__icontains=busca))
    return render(
        request,
        'acervo/membros.html',
        {'membros': membros, 'busca': busca},
    )


def novo_membro(request):
    return _formulario(
        request,
        form_class=MembroForm,
        titulo='Novo membro',
        voltar='acervo:membros',
    )


def editar_membro(request, pk):
    return _formulario(
        request,
        form_class=MembroForm,
        titulo='Editar membro',
        voltar='acervo:membros',
        instance=get_object_or_404(Membro, pk=pk),
    )


def excluir_membro(request, pk):
    return _excluir(
        request,
        objeto=get_object_or_404(Membro, pk=pk),
        titulo='Membro',
        voltar='acervo:membros',
    )


def lista_emprestimos(request):
    status = request.GET.get('status', 'ativos')
    emprestimos = Emprestimo.objects.select_related('exemplar__livro', 'membro')
    if status == 'ativos':
        emprestimos = emprestimos.filter(devolvido_em__isnull=True)
    elif status == 'atrasados':
        emprestimos = emprestimos.filter(
            devolvido_em__isnull=True, vencimento__lt=timezone.localdate()
        )
    elif status == 'concluidos':
        emprestimos = emprestimos.filter(devolvido_em__isnull=False)
    return render(
        request,
        'acervo/emprestimos.html',
        {'emprestimos': emprestimos, 'status': status},
    )


def novo_emprestimo(request):
    form = EmprestimoForm(
        request.POST or None,
        initial={'vencimento': timezone.localdate() + timedelta(days=14)},
    )
    if request.method == 'POST' and form.is_valid():
        try:
            registrar_emprestimo(**form.cleaned_data)
        except ValidationError as erro:
            _mensagem_validacao(request, erro)
        else:
            messages.success(request, 'Emprestimo registrado com sucesso.')
            return redirect('acervo:emprestimos')
    return render(
        request,
        'acervo/form.html',
        {
            'form': form,
            'titulo_form': 'Novo emprestimo',
            'voltar_url': reverse('acervo:emprestimos'),
        },
    )


def devolver_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    if request.method == 'POST':
        try:
            emprestimo = registrar_devolucao(emprestimo=emprestimo)
        except ValidationError as erro:
            _mensagem_validacao(request, erro)
        else:
            messages.success(
                request,
                f'Devolucao registrada. Multa calculada: R$ {emprestimo.multa:.2f}.',
            )
        return redirect('acervo:emprestimos')
    return render(
        request,
        'acervo/confirmar_devolucao.html',
        {'emprestimo': emprestimo},
    )


def lista_reservas(request):
    status = request.GET.get('status', Reserva.STATUS_AGUARDANDO)
    reservas = Reserva.objects.select_related('livro', 'membro')
    if status:
        reservas = reservas.filter(status=status)
    return render(
        request,
        'acervo/reservas.html',
        {'reservas': reservas, 'status': status, 'status_choices': Reserva.STATUS_CHOICES},
    )


def nova_reserva(request):
    form = ReservaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            registrar_reserva(**form.cleaned_data)
        except ValidationError as erro:
            _mensagem_validacao(request, erro)
        else:
            messages.success(request, 'Reserva adicionada ao fim da fila.')
            return redirect('acervo:reservas')
    return render(
        request,
        'acervo/form.html',
        {
            'form': form,
            'titulo_form': 'Nova reserva',
            'voltar_url': reverse('acervo:reservas'),
        },
    )


def cancelar_reserva_view(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        try:
            cancelar_reserva(reserva=reserva)
        except ValidationError as erro:
            _mensagem_validacao(request, erro)
        else:
            messages.success(request, 'Reserva cancelada com sucesso.')
    return redirect('acervo:reservas')
