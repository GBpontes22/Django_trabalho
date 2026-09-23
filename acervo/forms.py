from django import forms
from django.utils import timezone

from .models import Autor, Exemplar, Livro, Membro


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nome', 'nacionalidade', 'data_nascimento']
        widgets = {'data_nascimento': forms.DateInput(attrs={'type': 'date'})}


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = [
            'titulo',
            'autor',
            'ano',
            'isbn',
            'tipo_acervo',
            'categoria',
            'disponivel',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex.: Dom Casmurro'}),
            'ano': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_ano(self):
        ano = self.cleaned_data.get('ano')
        if ano and ano > timezone.localdate().year:
            raise forms.ValidationError(
                'O ano de publicacao nao pode ser um ano futuro.'
            )
        return ano


class ExemplarForm(forms.ModelForm):
    class Meta:
        model = Exemplar
        fields = ['livro', 'codigo', 'localizacao', 'status']

    def clean_status(self):
        status = self.cleaned_data['status']
        possui_emprestimo = self.instance.pk and self.instance.emprestimos.filter(
            devolvido_em__isnull=True
        ).exists()
        if possui_emprestimo and status != Exemplar.STATUS_EMPRESTADO:
            raise forms.ValidationError(
                'Registre a devolucao antes de alterar o status deste exemplar.'
            )
        if not possui_emprestimo and status == Exemplar.STATUS_EMPRESTADO:
            raise forms.ValidationError(
                'O status emprestado e definido ao registrar um emprestimo.'
            )
        return status


class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ['nome', 'email', 'telefone', 'ativo']


class EmprestimoForm(forms.Form):
    membro = forms.ModelChoiceField(
        queryset=Membro.objects.filter(ativo=True), label='Membro'
    )
    exemplar = forms.ModelChoiceField(
        queryset=Exemplar.objects.filter(status=Exemplar.STATUS_DISPONIVEL),
        label='Exemplar',
    )
    vencimento = forms.DateField(
        label='Data de vencimento', widget=forms.DateInput(attrs={'type': 'date'})
    )


class ReservaForm(forms.Form):
    membro = forms.ModelChoiceField(
        queryset=Membro.objects.filter(ativo=True), label='Membro'
    )
    livro = forms.ModelChoiceField(
        queryset=Livro.objects.filter(disponivel=True), label='Livro'
    )
