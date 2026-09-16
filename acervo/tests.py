from django.test import TestCase
from django.urls import reverse

from .models import Livro


class LivroViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Livro.objects.create(
            titulo='Dom Casmurro',
            autor='Machado de Assis',
            ano=1899,
            tipo_acervo=Livro.TIPO_FISICO,
            categoria='800',
        )
        Livro.objects.create(
            titulo='Clean Code',
            autor='Robert C. Martin',
            ano=2008,
            tipo_acervo=Livro.TIPO_DIGITAL,
            categoria='600',
        )
        Livro.objects.create(
            titulo='Breve Historia do Tempo',
            autor='Stephen Hawking',
            ano=1988,
            tipo_acervo=Livro.TIPO_DIGITAL,
            categoria='500',
        )

    def test_lista_exibe_livros_com_tipo_e_categoria(self):
        response = self.client.get(reverse('acervo:lista'))

        self.assertContains(response, 'Dom Casmurro')
        self.assertContains(response, 'Fisico')
        self.assertContains(response, '800 - Literatura')

    def test_pesquisa_por_nome(self):
        response = self.client.get(reverse('acervo:lista'), {'q': 'Dom'})

        self.assertContains(response, 'Dom Casmurro')
        self.assertNotContains(response, 'Clean Code')

    def test_pesquisa_por_tipo(self):
        response = self.client.get(
            reverse('acervo:lista'),
            {'tipo': Livro.TIPO_DIGITAL},
        )

        self.assertContains(response, 'Clean Code')
        self.assertContains(response, 'Breve Historia do Tempo')
        self.assertNotContains(response, 'Dom Casmurro')

    def test_pesquisa_por_categoria(self):
        response = self.client.get(reverse('acervo:lista'), {'categoria': '500'})

        self.assertContains(response, 'Breve Historia do Tempo')
        self.assertNotContains(response, 'Dom Casmurro')

    def test_cadastro_cria_livro_com_tipo_e_categoria(self):
        response = self.client.post(
            reverse('acervo:novo'),
            {
                'titulo': 'O Principe',
                'autor': 'Nicolau Maquiavel',
                'ano': 1532,
                'tipo_acervo': Livro.TIPO_DIGITAL,
                'categoria': '300',
                'disponivel': 'on',
            },
        )

        self.assertRedirects(response, reverse('acervo:lista'))
        livro = Livro.objects.get(titulo='O Principe')
        self.assertEqual(livro.tipo_acervo, Livro.TIPO_DIGITAL)
        self.assertEqual(livro.categoria, '300')

# Create your tests here.
