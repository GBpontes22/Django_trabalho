from django.contrib import admin
from .models import Livro


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "ano", "tipo_acervo", "categoria", "disponivel")
    list_filter = ("tipo_acervo", "categoria", "disponivel")
    search_fields = ("titulo", "autor")
