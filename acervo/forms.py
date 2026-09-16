from django import forms

from .models import Livro


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = [
            'titulo',
            'autor',
            'ano',
            'tipo_acervo',
            'categoria',
            'disponivel',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex.: Dom Casmurro'}),
            'autor': forms.TextInput(attrs={'placeholder': 'Ex.: Machado de Assis'}),
            'ano': forms.NumberInput(attrs={'min': 0}),
        }

