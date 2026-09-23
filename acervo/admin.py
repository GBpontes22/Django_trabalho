from django.contrib import admin

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nacionalidade')
    search_fields = ('nome',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'ano', 'tipo_acervo', 'categoria', 'disponivel')
    list_filter = ('tipo_acervo', 'categoria', 'disponivel')
    search_fields = ('titulo', 'autor__nome', 'isbn')
    list_select_related = ('autor',)


@admin.register(Exemplar)
class ExemplarAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'livro', 'status', 'localizacao')
    list_filter = ('status',)
    search_fields = ('codigo', 'livro__titulo')
    list_select_related = ('livro',)


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'email')


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = (
        'exemplar',
        'membro',
        'emprestado_em',
        'vencimento',
        'devolvido_em',
        'multa',
    )
    list_filter = ('devolvido_em', 'vencimento')
    search_fields = ('exemplar__codigo', 'exemplar__livro__titulo', 'membro__nome')
    list_select_related = ('exemplar__livro', 'membro')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('livro', 'membro', 'solicitada_em', 'status')
    list_filter = ('status',)
    search_fields = ('livro__titulo', 'membro__nome')
    list_select_related = ('livro', 'membro')
