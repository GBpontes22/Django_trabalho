from django import forms
from .models import Livro


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = [
            "titulo",
            "autor",
            "ano",
            "disponivel",
            "tipo_acervo",
            "categoria",
        ]
        labels = {
            "titulo": "Nome do livro",
            "autor": "Autor",
            "ano": "Ano",
            "disponivel": "Disponível",
            "tipo_acervo": "Tipo de acervo",
            "categoria": "Categoria",
        }
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "campo", "placeholder": "Digite o nome do livro"}),
            "autor": forms.TextInput(attrs={"class": "campo", "placeholder": "Digite o autor"}),
            "ano": forms.NumberInput(attrs={"class": "campo", "placeholder": "Ex.: 2024"}),
            "tipo_acervo": forms.Select(attrs={"class": "campo"}),
            "categoria": forms.Select(attrs={"class": "campo"}),
            "disponivel": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }
